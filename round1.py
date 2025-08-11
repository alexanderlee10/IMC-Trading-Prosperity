from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import jsonpickle
import math
import statistics
import numpy as np


class Trader:
    def run(self, state: TradingState):
        """
        Round 1 Strategy: Momentum-Based Trading with Risk Management
        - PEARLS: Statistical Arbitrage with Kalman Filter
        - BANANAS: Momentum Breakout Strategy
        - COCONUTS: Volatility-Based Mean Reversion
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
        if "volumes" not in hist_data:
            hist_data["volumes"] = {}
        if "kalman_state" not in hist_data:
            hist_data["kalman_state"] = {}

        result = {}
        POSITION_LIMIT = 20
        PRODUCTS = ["PEARLS", "BANANAS", "COCONUTS"]

        for product in PRODUCTS:
            if product not in state.order_depths:
                continue

            order_depth = state.order_depths[product]
            current_pos = state.position.get(product, 0)

            # Extract market data
            best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
            best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
            mid_price = (best_bid + best_ask) / 2.0 if best_bid and best_ask else None

            # Update price history
            if mid_price is not None:
                if product not in hist_data["prices"]:
                    hist_data["prices"][product] = []
                hist_data["prices"][product].append(mid_price)
                hist_data["prices"][product] = hist_data["prices"][product][-50:]

            orders = []

            # PEARLS: Statistical Arbitrage with Kalman Filter
            if product == "PEARLS":
                if mid_price is not None and len(hist_data["prices"][product]) >= 10:
                    prices = hist_data["prices"][product]
                    
                    # Simple Kalman filter for trend estimation
                    if product not in hist_data["kalman_state"]:
                        hist_data["kalman_state"][product] = {"estimate": prices[-1], "error": 1.0}
                    
                    kalman = hist_data["kalman_state"][product]
                    
                    # Kalman update
                    measurement = mid_price
                    kalman_gain = kalman["error"] / (kalman["error"] + 1.0)
                    kalman["estimate"] = kalman["estimate"] + kalman_gain * (measurement - kalman["estimate"])
                    kalman["error"] = (1 - kalman_gain) * kalman["error"]
                    
                    # Trading logic based on deviation from Kalman estimate
                    deviation = mid_price - kalman["estimate"]
                    threshold = 0.5
                    
                    if abs(deviation) > threshold:
                        if deviation > 0:  # Price above estimate, sell
                            if best_bid and current_pos > -POSITION_LIMIT:
                                sell_qty = min(3, POSITION_LIMIT + current_pos)
                                if sell_qty > 0:
                                    orders.append(Order(product, best_bid, -sell_qty))
                        else:  # Price below estimate, buy
                            if best_ask and current_pos < POSITION_LIMIT:
                                buy_qty = min(3, POSITION_LIMIT - current_pos)
                                if buy_qty > 0:
                                    orders.append(Order(product, best_ask, buy_qty))

            # BANANAS: Momentum Breakout Strategy
            elif product == "BANANAS":
                if len(hist_data["prices"][product]) >= 20:
                    prices = hist_data["prices"][product]
                    
                    # Calculate momentum indicators
                    short_ma = np.mean(prices[-5:])
                    long_ma = np.mean(prices[-20:])
                    momentum = short_ma - long_ma
                    
                    # Volatility-based position sizing
                    volatility = np.std(prices[-10:])
                    base_size = max(1, int(5 / (volatility + 0.1)))
                    
                    if momentum > 0.5:  # Strong upward momentum
                        if best_ask and current_pos < POSITION_LIMIT:
                            buy_qty = min(base_size, POSITION_LIMIT - current_pos)
                            if buy_qty > 0:
                                orders.append(Order(product, best_ask, buy_qty))
                    elif momentum < -0.5:  # Strong downward momentum
                        if best_bid and current_pos > -POSITION_LIMIT:
                            sell_qty = min(base_size, POSITION_LIMIT + current_pos)
                            if sell_qty > 0:
                                orders.append(Order(product, best_bid, -sell_qty))

            # COCONUTS: Volatility-Based Mean Reversion
            elif product == "COCONUTS":
                if len(hist_data["prices"][product]) >= 15:
                    prices = hist_data["prices"][product]
                    
                    # Calculate Bollinger Bands
                    window = 15
                    sma = np.mean(prices[-window:])
                    std = np.std(prices[-window:])
                    upper_band = sma + 2 * std
                    lower_band = sma - 2 * std
                    
                    # Position sizing based on volatility
                    volatility_ratio = std / sma if sma > 0 else 1
                    position_size = max(2, int(8 * volatility_ratio))
                    
                    if mid_price > upper_band:  # Overbought, sell
                        if best_bid and current_pos > -POSITION_LIMIT:
                            sell_qty = min(position_size, POSITION_LIMIT + current_pos)
                            if sell_qty > 0:
                                orders.append(Order(product, best_bid, -sell_qty))
                    elif mid_price < lower_band:  # Oversold, buy
                        if best_ask and current_pos < POSITION_LIMIT:
                            buy_qty = min(position_size, POSITION_LIMIT - current_pos)
                            if buy_qty > 0:
                                orders.append(Order(product, best_ask, buy_qty))

            if len(orders) > 0:
                result[product] = orders

        conversions = 0
        traderData = jsonpickle.encode(hist_data)
        return result, conversions, traderData
