from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import jsonpickle
import math
import statistics
import numpy as np


class Trader:
    def run(self, state: TradingState):
        """
        Round 2 Strategy: Market Microstructure and Order Book Analysis
        - PINA_COLADAS: Order Book Imbalance Strategy
        - DIVING_GEAR: Spread-Based Market Making
        - BERRIES: Volume-Weighted Price Strategy
        """

        # Initialize historical data storage
        if state.traderData:
            try:
                hist_data = jsonpickle.decode(state.traderData)
            except:
                hist_data = {}
        else:
            hist_data = {}

        if "prices" not in hist_data:
            hist_data["prices"] = {}
        if "order_imbalances" not in hist_data:
            hist_data["order_imbalances"] = {}
        if "vwap_data" not in hist_data:
            hist_data["vwap_data"] = {}

        result = {}
        POSITION_LIMIT = 15
        PRODUCTS = ["PINA_COLADAS", "DIVING_GEAR", "BERRIES"]

        for product in PRODUCTS:
            if product not in state.order_depths:
                continue

            order_depth = state.order_depths[product]
            current_pos = state.position.get(product, 0)

            # Extract market data
            best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
            best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
            mid_price = (best_bid + best_ask) / 2.0 if best_bid and best_ask else None
            spread = best_ask - best_bid if best_bid and best_ask else None

            # Update price history
            if mid_price is not None:
                if product not in hist_data["prices"]:
                    hist_data["prices"][product] = []
                hist_data["prices"][product].append(mid_price)
                hist_data["prices"][product] = hist_data["prices"][product][-40:]

            orders = []

            # PINA_COLADAS: Order Book Imbalance Strategy
            if product == "PINA_COLADAS":
                if best_bid and best_ask:
                    # Calculate order book imbalance
                    bid_volume = sum(order_depth.buy_orders.values())
                    ask_volume = sum(order_depth.sell_orders.values())
                    total_volume = bid_volume + ask_volume
                    
                    if total_volume > 0:
                        imbalance = (bid_volume - ask_volume) / total_volume
                        
                        # Store imbalance history
                        if product not in hist_data["order_imbalances"]:
                            hist_data["order_imbalances"][product] = []
                        hist_data["order_imbalances"][product].append(imbalance)
                        hist_data["order_imbalances"][product] = hist_data["order_imbalances"][product][-20:]
                        
                        # Trading logic based on imbalance
                        if len(hist_data["order_imbalances"][product]) >= 5:
                            recent_imbalance = np.mean(hist_data["order_imbalances"][product][-5:])
                            
                            if recent_imbalance > 0.3:  # Strong buying pressure
                                if current_pos < POSITION_LIMIT:
                                    buy_qty = min(4, POSITION_LIMIT - current_pos)
                                    if buy_qty > 0:
                                        orders.append(Order(product, best_ask, buy_qty))
                            elif recent_imbalance < -0.3:  # Strong selling pressure
                                if current_pos > -POSITION_LIMIT:
                                    sell_qty = min(4, POSITION_LIMIT + current_pos)
                                    if sell_qty > 0:
                                        orders.append(Order(product, best_bid, -sell_qty))

            # DIVING_GEAR: Spread-Based Market Making
            elif product == "DIVING_GEAR":
                if spread is not None and mid_price is not None:
                    # Calculate spread as percentage of mid price
                    spread_pct = spread / mid_price
                    
                    # Adaptive spread threshold based on recent volatility
                    if len(hist_data["prices"][product]) >= 10:
                        volatility = np.std(hist_data["prices"][product][-10:]) / mid_price
                        min_spread = max(0.01, volatility * 2)  # At least 1% spread
                        
                        if spread_pct > min_spread:
                            # Wide spread, place orders inside the spread
                            buy_price = int(mid_price - spread * 0.3)
                            sell_price = int(mid_price + spread * 0.3)
                            
                            # Position-based order sizing
                            if current_pos < POSITION_LIMIT:
                                buy_qty = min(3, POSITION_LIMIT - current_pos)
                                if buy_qty > 0:
                                    orders.append(Order(product, buy_price, buy_qty))
                            
                            if current_pos > -POSITION_LIMIT:
                                sell_qty = min(3, POSITION_LIMIT + current_pos)
                                if sell_qty > 0:
                                    orders.append(Order(product, sell_price, -sell_qty))

            # BERRIES: Volume-Weighted Price Strategy
            elif product == "BERRIES":
                if best_bid and best_ask and len(hist_data["prices"][product]) >= 15:
                    # Calculate VWAP (Volume Weighted Average Price)
                    if product not in hist_data["vwap_data"]:
                        hist_data["vwap_data"][product] = {"prices": [], "volumes": []}
                    
                    vwap_data = hist_data["vwap_data"][product]
                    vwap_data["prices"].append(mid_price)
                    vwap_data["volumes"].append(1)  # Assume unit volume for simplicity
                    
                    # Keep last 15 data points
                    vwap_data["prices"] = vwap_data["prices"][-15:]
                    vwap_data["volumes"] = vwap_data["volumes"][-15:]
                    
                    if len(vwap_data["prices"]) >= 10:
                        # Calculate VWAP
                        total_volume = sum(vwap_data["volumes"])
                        vwap = sum(p * v for p, v in zip(vwap_data["prices"], vwap_data["volumes"])) / total_volume
                        
                        # Calculate VWAP deviation
                        vwap_deviation = (mid_price - vwap) / vwap
                        
                        # Mean reversion strategy around VWAP
                        threshold = 0.02  # 2% deviation
                        
                        if vwap_deviation > threshold:  # Price above VWAP, sell
                            if current_pos > -POSITION_LIMIT:
                                sell_qty = min(5, POSITION_LIMIT + current_pos)
                                if sell_qty > 0:
                                    orders.append(Order(product, best_bid, -sell_qty))
                        elif vwap_deviation < -threshold:  # Price below VWAP, buy
                            if current_pos < POSITION_LIMIT:
                                buy_qty = min(5, POSITION_LIMIT - current_pos)
                                if buy_qty > 0:
                                    orders.append(Order(product, best_ask, buy_qty))

            if len(orders) > 0:
                result[product] = orders

        conversions = 0
        traderData = jsonpickle.encode(hist_data)
        return result, conversions, traderData 