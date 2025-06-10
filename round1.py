from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import jsonpickle
import math
import statistics


class Trader:
    def run(self, state: TradingState):
        """
        Implements:
          - Rainforest Resin: Passive Market Making
          - Kelp: Simple Trend Following
          - Squid Ink: Z-Score Mean Reversion
        """

        # --- 1) Load historical data from traderData (persisted between calls) ---
        if state.traderData:
            try:
                hist_data = jsonpickle.decode(state.traderData)
            except:
                hist_data = {}
        else:
            hist_data = {}

        # We’ll store rolling price lists in hist_data["prices"][symbol]
        if "prices" not in hist_data:
            hist_data["prices"] = {}

        # --- 2) Prepare to output your new orders ---
        result = {}

        # A handy reference to position limit
        POSITION_LIMIT = 50

        # Define your product names
        PRODUCTS = ["RAINFOREST_RESIN", "KELP", "SQUID_INK"]

        # --- 3) Update rolling prices and place orders for each product ---
        for product in PRODUCTS:
            # If not in the current order_depth, skip
            if product not in state.order_depths:
                continue

            order_depth = state.order_depths[product]
            current_pos = state.position.get(product, 0)

            # Extract best bid and best ask to compute mid-price
            best_bid = None
            if len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
            best_ask = None
            if len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())

            # Compute a mid-price for data tracking
            mid_price = None
            if best_bid is not None and best_ask is not None:
                mid_price = (best_bid + best_ask) / 2.0

            # Store mid_price in rolling history
            if mid_price is not None:
                if product not in hist_data["prices"]:
                    hist_data["prices"][product] = []
                hist_data["prices"][product].append(mid_price)

                # Keep a rolling window—e.g., up to 30 points
                hist_data["prices"][product] = hist_data["prices"][product][-30:]

            # Decide how many units to buy/sell in total.
            # We'll accumulate actual order objects in a local list:
            orders = []

            # --- 3A) Rainforest Resin: Passive Market Making ---
            if product == "RAINFOREST_RESIN":
                # If we have a mid_price, place a bid at (mid - 1), ask at (mid + 1)
                # We also watch if position is drifting. If we’re too long, we might only place an ask, etc.
                if mid_price is not None:
                    # Spread of ±1 around mid
                    buy_price = int(mid_price - 1)
                    sell_price = int(mid_price + 1)

                    # Suppose we want to place up to some size, e.g. 5 or 10 each side
                    mm_size = 5

                    # If we’re too long, we’ll reduce or skip buy quotes
                    # Example: if current_pos > 40, we place no more buy orders
                    if current_pos < POSITION_LIMIT:
                        # Ensure we can buy at least 1 more
                        can_buy = POSITION_LIMIT - current_pos
                        buy_quantity = min(mm_size, can_buy)
                        if buy_quantity > 0 and buy_price > 0:  # sanity check
                            orders.append(Order(product, buy_price, buy_quantity))

                    # If we’re too short, we reduce or skip sell quotes
                    if current_pos > -POSITION_LIMIT:
                        can_sell = current_pos - (-POSITION_LIMIT)  # basically current_pos + 50
                        # For example, if current_pos = -20, can_sell = 30
                        # But realistically we only want to sell if we have a long position
                        # so let’s just check if we actually hold something > 0, or if we want to short
                        # For now, we’ll allow shorting. So we can always do a 5-lot sell, if within limits.
                        sell_quantity = mm_size
                        # If we are near short limit, skip:
                        if current_pos <= -POSITION_LIMIT:
                            sell_quantity = 0
                        if sell_quantity > 0:
                            orders.append(Order(product, sell_price, -sell_quantity))

            # --- 3B) Kelp: Simple Trend Following ---
            elif product == "KELP":
                # We track the slope of the last N mid-prices. If slope > 0, go long; if slope < 0, go short.
                # For simplicity, use the last 5 points to compute a simple linear slope.
                N = 5
                if product in hist_data["prices"] and len(hist_data["prices"][product]) >= N:
                    recent_prices = hist_data["prices"][product][-N:]

                    # Quick slope calculation:
                    #   slope ~ (p[N-1] - p[0]) / N  (a rough measure)
                    slope = (recent_prices[-1] - recent_prices[0]) / (N - 1)

                    # If slope > 0 => uptrend => buy
                    # If slope < 0 => downtrend => sell
                    # We can scale the order size with the magnitude of slope or keep it simple.

                    order_size = 5  # base size
                    if slope > 0:
                        # Buy
                        # We attempt to hit the best ask if it's within reason
                        if best_ask is not None:
                            # Don’t exceed limit
                            can_buy = POSITION_LIMIT - current_pos
                            buy_qty = min(order_size, max(0, can_buy))
                            if buy_qty > 0:
                                orders.append(Order(product, best_ask, buy_qty))

                    elif slope < 0:
                        # Sell
                        if best_bid is not None:
                            # How many can we sell?
                            # If we have a positive position, we can flatten it
                            # Or go short if we want
                            can_sell = POSITION_LIMIT + current_pos  # e.g. if pos=-10, can_sell=40
                            sell_qty = min(order_size, max(0, can_sell))
                            if sell_qty > 0:
                                orders.append(Order(product, best_bid, -sell_qty))

            # --- 3C) Squid Ink: Z-Score Mean Reversion ---
            elif product == "SQUID_INK":
                # Keep a rolling window (e.g. 20). Calculate mean, std dev, then z-score of last price.
                if product in hist_data["prices"] and len(hist_data["prices"][product]) >= 10:
                    window_prices = hist_data["prices"][product][-20:]  # up to last 20
                    avg_price = statistics.mean(window_prices)
                    stdev = statistics.pstdev(window_prices)  # population stdev
                    latest_price = window_prices[-1]

                    if stdev > 0:
                        z_score = (latest_price - avg_price) / stdev

                        # If z >= +1 => price "too high" => SELL
                        # If z <= -1 => price "too low"  => BUY
                        threshold = 1.0
                        # Let’s do a 5-lot times the integer part of z
                        # (So if z=2.1, we do 10-lot, if z=1.0, we do 5-lot)

                        magnitude = int(abs(z_score))
                        base_lot = 5
                        trade_size = base_lot * max(1, magnitude)  # at least 5, scaled up

                        if z_score >= threshold:
                            # Sell
                            if best_bid is not None:
                                can_sell = POSITION_LIMIT + current_pos  # how many we can short
                                sell_qty = min(trade_size, max(0, can_sell))
                                if sell_qty > 0:
                                    orders.append(Order(product, best_bid, -sell_qty))

                        elif z_score <= -threshold:
                            # Buy
                            if best_ask is not None:
                                can_buy = POSITION_LIMIT - current_pos
                                buy_qty = min(trade_size, max(0, can_buy))
                                if buy_qty > 0:
                                    orders.append(Order(product, best_ask, buy_qty))

            # Attach the collected orders for this product into the result
            if len(orders) > 0:
                result[product] = orders

        # --- 4) If you want to request conversions, do it here (we do not for now) ---
        conversions = 0

        # --- 5) Encode hist_data back into a string for next iteration ---
        traderData = jsonpickle.encode(hist_data)

        return result, conversions, traderData
