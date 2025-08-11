from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import jsonpickle
import math
import statistics
import numpy as np


class Trader:
    def run(self, state: TradingState):
        """
        Round 3 Strategy: Multi-Timeframe Analysis and Adaptive Strategies
        - DOLPHIN_SIGHTINGS: Multi-Timeframe Trend Analysis
        - BAGUETTE: Adaptive Mean Reversion with Regime Detection
        - DIP: Correlation-Based Pairs Trading
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
        if "regime_data" not in hist_data:
            hist_data["regime_data"] = {}
        if "correlation_data" not in hist_data:
            hist_data["correlation_data"] = {}

        result = {}
        POSITION_LIMIT = 25
        PRODUCTS = ["DOLPHIN_SIGHTINGS", "BAGUETTE", "DIP"]

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
                hist_data["prices"][product] = hist_data["prices"][product][-60:]

            orders = []

            # DOLPHIN_SIGHTINGS: Multi-Timeframe Trend Analysis
            if product == "DOLPHIN_SIGHTINGS":
                if len(hist_data["prices"][product]) >= 30:
                    prices = hist_data["prices"][product]
                    
                    # Short-term trend (5 periods)
                    short_ma = np.mean(prices[-5:])
                    short_trend = short_ma - prices[-5]
                    
                    # Medium-term trend (15 periods)
                    medium_ma = np.mean(prices[-15:])
                    medium_trend = medium_ma - prices[-15]
                    
                    # Long-term trend (30 periods)
                    long_ma = np.mean(prices[-30:])
                    long_trend = long_ma - prices[-30]
                    
                    # Multi-timeframe consensus
                    trend_score = (short_trend * 0.5 + medium_trend * 0.3 + long_trend * 0.2)
                    
                    # Volatility-adjusted position sizing
                    volatility = np.std(prices[-10:])
                    base_size = max(2, int(8 / (volatility + 0.1)))
                    
                    if trend_score > 0.5:  # Strong upward trend across timeframes
                        if best_ask and current_pos < POSITION_LIMIT:
                            buy_qty = min(base_size, POSITION_LIMIT - current_pos)
                            if buy_qty > 0:
                                orders.append(Order(product, best_ask, buy_qty))
                    elif trend_score < -0.5:  # Strong downward trend across timeframes
                        if best_bid and current_pos > -POSITION_LIMIT:
                            sell_qty = min(base_size, POSITION_LIMIT + current_pos)
                            if sell_qty > 0:
                                orders.append(Order(product, best_bid, -sell_qty))

            # BAGUETTE: Adaptive Mean Reversion with Regime Detection
            elif product == "BAGUETTE":
                if len(hist_data["prices"][product]) >= 20:
                    prices = hist_data["prices"][product]
                    
                    # Detect market regime (trending vs mean-reverting)
                    if product not in hist_data["regime_data"]:
                        hist_data["regime_data"][product] = {"regime": "unknown", "regime_score": 0}
                    
                    regime_data = hist_data["regime_data"][product]
                    
                    # Calculate regime indicators
                    price_change = prices[-1] - prices[-20]
                    volatility = np.std(prices[-10:])
                    mean_reversion_strength = abs(prices[-1] - np.mean(prices[-20:])) / volatility if volatility > 0 else 0
                    
                    # Update regime score
                    regime_score = regime_data["regime_score"] * 0.9 + mean_reversion_strength * 0.1
                    regime_data["regime_score"] = regime_score
                    
                    # Determine regime
                    if regime_score > 1.5:
                        regime_data["regime"] = "trending"
                    elif regime_score < 0.5:
                        regime_data["regime"] = "mean_reverting"
                    
                    # Trading logic based on regime
                    if regime_data["regime"] == "mean_reverting":
                        # Traditional mean reversion
                        sma = np.mean(prices[-20:])
                        deviation = (mid_price - sma) / sma
                        
                        if abs(deviation) > 0.02:  # 2% deviation
                            if deviation > 0:  # Overvalued, sell
                                if best_bid and current_pos > -POSITION_LIMIT:
                                    sell_qty = min(6, POSITION_LIMIT + current_pos)
                                    if sell_qty > 0:
                                        orders.append(Order(product, best_bid, -sell_qty))
                            else:  # Undervalued, buy
                                if best_ask and current_pos < POSITION_LIMIT:
                                    buy_qty = min(6, POSITION_LIMIT - current_pos)
                                    if buy_qty > 0:
                                        orders.append(Order(product, best_ask, buy_qty))
                    
                    elif regime_data["regime"] == "trending":
                        # Trend following
                        short_ma = np.mean(prices[-5:])
                        long_ma = np.mean(prices[-15:])
                        
                        if short_ma > long_ma:  # Uptrend
                            if best_ask and current_pos < POSITION_LIMIT:
                                buy_qty = min(4, POSITION_LIMIT - current_pos)
                                if buy_qty > 0:
                                    orders.append(Order(product, best_ask, buy_qty))
                        else:  # Downtrend
                            if best_bid and current_pos > -POSITION_LIMIT:
                                sell_qty = min(4, POSITION_LIMIT + current_pos)
                                if sell_qty > 0:
                                    orders.append(Order(product, best_bid, -sell_qty))

            # DIP: Correlation-Based Pairs Trading
            elif product == "DIP":
                if len(hist_data["prices"][product]) >= 25:
                    prices = hist_data["prices"][product]
                    
                    # Calculate correlation with other products (simplified)
                    if "BAGUETTE" in hist_data["prices"] and len(hist_data["prices"]["BAGUETTE"]) >= 25:
                        baguette_prices = hist_data["prices"]["BAGUETTE"][-25:]
                        
                        # Calculate rolling correlation
                        if len(prices) >= 25 and len(baguette_prices) >= 25:
                            correlation = np.corrcoef(prices[-25:], baguette_prices[-25:])[0, 1]
                            
                            if not np.isnan(correlation) and abs(correlation) > 0.7:
                                # High correlation detected, implement pairs trading
                                # Calculate spread between products
                                spread = prices[-1] - baguette_prices[-1]
                                
                                # Store spread history
                                if product not in hist_data["correlation_data"]:
                                    hist_data["correlation_data"][product] = {"spreads": []}
                                
                                hist_data["correlation_data"][product]["spreads"].append(spread)
                                hist_data["correlation_data"][product]["spreads"] = hist_data["correlation_data"][product]["spreads"][-20:]
                                
                                if len(hist_data["correlation_data"][product]["spreads"]) >= 10:
                                    spread_mean = np.mean(hist_data["correlation_data"][product]["spreads"])
                                    spread_std = np.std(hist_data["correlation_data"][product]["spreads"])
                                    
                                    if spread_std > 0:
                                        z_score = (spread - spread_mean) / spread_std
                                        
                                        if z_score > 1.5:  # Spread too wide, sell DIP
                                            if best_bid and current_pos > -POSITION_LIMIT:
                                                sell_qty = min(5, POSITION_LIMIT + current_pos)
                                                if sell_qty > 0:
                                                    orders.append(Order(product, best_bid, -sell_qty))
                                        elif z_score < -1.5:  # Spread too narrow, buy DIP
                                            if best_ask and current_pos < POSITION_LIMIT:
                                                buy_qty = min(5, POSITION_LIMIT - current_pos)
                                                if buy_qty > 0:
                                                    orders.append(Order(product, best_ask, buy_qty))

            if len(orders) > 0:
                result[product] = orders

        conversions = 0
        traderData = jsonpickle.encode(hist_data)
        return result, conversions, traderData 