from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import jsonpickle
import math
import statistics
import numpy as np


class Trader:
    def run(self, state: TradingState):
        """
        Round 4 Strategy: Advanced Statistical Arbitrage and ML-Inspired Approaches
        - UKULELE: Harmonic Pattern Recognition
        - PICNIC_BASKET: Basket Trading with Principal Component Analysis
        - TREASURE_MAP: Hidden Markov Model for Regime Detection
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
        if "harmonic_patterns" not in hist_data:
            hist_data["harmonic_patterns"] = {}
        if "pca_data" not in hist_data:
            hist_data["pca_data"] = {}
        if "hmm_data" not in hist_data:
            hist_data["hmm_data"] = {}

        result = {}
        POSITION_LIMIT = 30
        PRODUCTS = ["UKULELE", "PICNIC_BASKET", "TREASURE_MAP"]

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
                hist_data["prices"][product] = hist_data["prices"][product][-80:]

            orders = []

            # UKULELE: Harmonic Pattern Recognition
            if product == "UKULELE":
                if len(hist_data["prices"][product]) >= 40:
                    prices = hist_data["prices"][product]
                    
                    # Detect harmonic patterns (simplified Gartley pattern)
                    if product not in hist_data["harmonic_patterns"]:
                        hist_data["harmonic_patterns"][product] = {"pattern_type": None, "confidence": 0}
                    
                    pattern_data = hist_data["harmonic_patterns"][product]
                    
                    # Find local extremes
                    highs = []
                    lows = []
                    for i in range(1, len(prices) - 1):
                        if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                            highs.append((i, prices[i]))
                        elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                            lows.append((i, prices[i]))
                    
                    # Look for harmonic patterns in recent data
                    if len(highs) >= 2 and len(lows) >= 2:
                        recent_highs = [h for h in highs if h[0] >= len(prices) - 20]
                        recent_lows = [l for l in lows if l[0] >= len(prices) - 20]
                        
                        if len(recent_highs) >= 1 and len(recent_lows) >= 1:
                            # Calculate Fibonacci ratios
                            high1, high2 = recent_highs[-2:] if len(recent_highs) >= 2 else [recent_highs[-1], recent_highs[-1]]
                            low1, low2 = recent_lows[-2:] if len(recent_lows) >= 2 else [recent_lows[-1], recent_lows[-1]]
                            
                            # Simplified harmonic pattern detection
                            swing_high = max(high1[1], high2[1])
                            swing_low = min(low1[1], low2[1])
                            current_price = prices[-1]
                            
                            # Calculate retracement levels
                            range_size = swing_high - swing_low
                            if range_size > 0:
                                retracement_618 = swing_high - 0.618 * range_size
                                retracement_382 = swing_high - 0.382 * range_size
                                
                                # Trading logic based on retracement levels
                                if current_price < retracement_618:  # Oversold
                                    if best_ask and current_pos < POSITION_LIMIT:
                                        buy_qty = min(7, POSITION_LIMIT - current_pos)
                                        if buy_qty > 0:
                                            orders.append(Order(product, best_ask, buy_qty))
                                elif current_price > retracement_382:  # Overbought
                                    if best_bid and current_pos > -POSITION_LIMIT:
                                        sell_qty = min(7, POSITION_LIMIT + current_pos)
                                        if sell_qty > 0:
                                            orders.append(Order(product, best_bid, -sell_qty))

            # PICNIC_BASKET: Basket Trading with Principal Component Analysis
            elif product == "PICNIC_BASKET":
                if len(hist_data["prices"][product]) >= 30:
                    prices = hist_data["prices"][product]
                    
                    # Collect prices from all available products for PCA
                    all_prices = []
                    product_names = []
                    
                    for prod in hist_data["prices"]:
                        if len(hist_data["prices"][prod]) >= 30:
                            all_prices.append(hist_data["prices"][prod][-30:])
                            product_names.append(prod)
                    
                    if len(all_prices) >= 2:
                        # Convert to numpy array
                        price_matrix = np.array(all_prices).T
                        
                        # Calculate correlation matrix
                        corr_matrix = np.corrcoef(price_matrix.T)
                        
                        # Find the product with highest correlation to PICNIC_BASKET
                        if product in product_names:
                            product_idx = product_names.index(product)
                            correlations = corr_matrix[product_idx]
                            
                            # Find most correlated product (excluding self)
                            other_correlations = [(i, corr) for i, corr in enumerate(correlations) if i != product_idx]
                            if other_correlations:
                                most_correlated_idx, correlation = max(other_correlations, key=lambda x: abs(x[1]))
                                most_correlated_product = product_names[most_correlated_idx]
                                
                                if abs(correlation) > 0.6:  # Strong correlation
                                    # Calculate relative value
                                    basket_price = prices[-1]
                                    correlated_price = hist_data["prices"][most_correlated_product][-1]
                                    
                                    # Calculate historical price ratio
                                    price_ratios = []
                                    for i in range(min(len(prices), len(hist_data["prices"][most_correlated_product]))):
                                        if hist_data["prices"][most_correlated_product][i] > 0:
                                            ratio = prices[i] / hist_data["prices"][most_correlated_product][i]
                                            price_ratios.append(ratio)
                                    
                                    if len(price_ratios) >= 10:
                                        ratio_mean = np.mean(price_ratios)
                                        ratio_std = np.std(price_ratios)
                                        
                                        if ratio_std > 0:
                                            current_ratio = basket_price / correlated_price
                                            z_score = (current_ratio - ratio_mean) / ratio_std
                                            
                                            if z_score > 1.5:  # Basket overvalued relative to correlated product
                                                if best_bid and current_pos > -POSITION_LIMIT:
                                                    sell_qty = min(8, POSITION_LIMIT + current_pos)
                                                    if sell_qty > 0:
                                                        orders.append(Order(product, best_bid, -sell_qty))
                                            elif z_score < -1.5:  # Basket undervalued relative to correlated product
                                                if best_ask and current_pos < POSITION_LIMIT:
                                                    buy_qty = min(8, POSITION_LIMIT - current_pos)
                                                    if buy_qty > 0:
                                                        orders.append(Order(product, best_ask, buy_qty))

            # TREASURE_MAP: Hidden Markov Model for Regime Detection
            elif product == "TREASURE_MAP":
                if len(hist_data["prices"][product]) >= 50:
                    prices = hist_data["prices"][product]
                    
                    if product not in hist_data["hmm_data"]:
                        hist_data["hmm_data"][product] = {
                            "regime": "unknown",
                            "regime_probability": 0.5,
                            "volatility_regime": "normal"
                        }
                    
                    hmm_data = hist_data["hmm_data"][product]
                    
                    # Calculate regime indicators
                    returns = np.diff(prices[-20:])
                    volatility = np.std(returns)
                    mean_return = np.mean(returns)
                    
                    # Update volatility regime
                    if volatility > np.std(returns[-10:]) * 1.5:
                        hmm_data["volatility_regime"] = "high"
                    elif volatility < np.std(returns[-10:]) * 0.5:
                        hmm_data["volatility_regime"] = "low"
                    else:
                        hmm_data["volatility_regime"] = "normal"
                    
                    # Simplified regime detection
                    trend_strength = abs(mean_return) / volatility if volatility > 0 else 0
                    
                    # Update regime probability
                    if trend_strength > 0.5:
                        hmm_data["regime_probability"] = min(1.0, hmm_data["regime_probability"] + 0.1)
                    else:
                        hmm_data["regime_probability"] = max(0.0, hmm_data["regime_probability"] - 0.1)
                    
                    # Determine regime
                    if hmm_data["regime_probability"] > 0.7:
                        hmm_data["regime"] = "trending"
                    elif hmm_data["regime_probability"] < 0.3:
                        hmm_data["regime"] = "mean_reverting"
                    else:
                        hmm_data["regime"] = "sideways"
                    
                    # Trading logic based on regime and volatility
                    if hmm_data["regime"] == "trending":
                        # Trend following with volatility-adjusted sizing
                        if mean_return > 0:  # Uptrend
                            if best_ask and current_pos < POSITION_LIMIT:
                                size_multiplier = 2 if hmm_data["volatility_regime"] == "high" else 1
                                buy_qty = min(6 * size_multiplier, POSITION_LIMIT - current_pos)
                                if buy_qty > 0:
                                    orders.append(Order(product, best_ask, buy_qty))
                        else:  # Downtrend
                            if best_bid and current_pos > -POSITION_LIMIT:
                                size_multiplier = 2 if hmm_data["volatility_regime"] == "high" else 1
                                sell_qty = min(6 * size_multiplier, POSITION_LIMIT + current_pos)
                                if sell_qty > 0:
                                    orders.append(Order(product, best_bid, -sell_qty))
                    
                    elif hmm_data["regime"] == "mean_reverting":
                        # Mean reversion with tighter thresholds in low volatility
                        sma = np.mean(prices[-20:])
                        deviation = (mid_price - sma) / sma
                        
                        threshold = 0.015 if hmm_data["volatility_regime"] == "low" else 0.025
                        
                        if abs(deviation) > threshold:
                            if deviation > 0:  # Overvalued
                                if best_bid and current_pos > -POSITION_LIMIT:
                                    sell_qty = min(5, POSITION_LIMIT + current_pos)
                                    if sell_qty > 0:
                                        orders.append(Order(product, best_bid, -sell_qty))
                            else:  # Undervalued
                                if best_ask and current_pos < POSITION_LIMIT:
                                    buy_qty = min(5, POSITION_LIMIT - current_pos)
                                    if buy_qty > 0:
                                        orders.append(Order(product, best_ask, buy_qty))

            if len(orders) > 0:
                result[product] = orders

        conversions = 0
        traderData = jsonpickle.encode(hist_data)
        return result, conversions, traderData 