from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import jsonpickle
import math
import statistics
import numpy as np


class Trader:
    def run(self, state: TradingState):
        """
        Round 5 Strategy: Ensemble Methods and Advanced Risk Management
        - COCONUT_COUPON: Options-Inspired Delta Hedging
        - INVENTORY: Multi-Strategy Ensemble with Risk Parity
        - SUNDIAL: Time-Based Arbitrage with Calendar Effects
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
        if "ensemble_signals" not in hist_data:
            hist_data["ensemble_signals"] = {}
        if "risk_metrics" not in hist_data:
            hist_data["risk_metrics"] = {}
        if "time_data" not in hist_data:
            hist_data["time_data"] = {}

        result = {}
        POSITION_LIMIT = 35
        PRODUCTS = ["COCONUT_COUPON", "INVENTORY", "SUNDIAL"]

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
                hist_data["prices"][product] = hist_data["prices"][product][-100:]

            orders = []

            # COCONUT_COUPON: Options-Inspired Delta Hedging
            if product == "COCONUT_COUPON":
                if len(hist_data["prices"][product]) >= 30:
                    prices = hist_data["prices"][product]
                    
                    # Calculate implied volatility (simplified)
                    returns = np.diff(prices[-20:])
                    implied_vol = np.std(returns) * np.sqrt(252)  # Annualized
                    
                    # Calculate delta (simplified option delta approximation)
                    if product not in hist_data["risk_metrics"]:
                        hist_data["risk_metrics"][product] = {"delta": 0, "gamma": 0}
                    
                    risk_data = hist_data["risk_metrics"][product]
                    
                    # Simplified delta calculation based on price momentum
                    short_ma = np.mean(prices[-5:])
                    long_ma = np.mean(prices[-20:])
                    momentum = (short_ma - long_ma) / long_ma if long_ma > 0 else 0
                    
                    # Delta ranges from -1 to 1 based on momentum
                    new_delta = np.tanh(momentum * 5)  # Scale momentum and bound to [-1, 1]
                    
                    # Gamma (rate of change of delta)
                    gamma = new_delta - risk_data["delta"]
                    risk_data["delta"] = new_delta
                    risk_data["gamma"] = gamma
                    
                    # Delta hedging logic
                    target_position = int(risk_data["delta"] * POSITION_LIMIT * 0.5)
                    position_adjustment = target_position - current_pos
                    
                    if abs(position_adjustment) > 2:  # Only trade if adjustment is significant
                        if position_adjustment > 0:  # Need to buy
                            if best_ask and current_pos < POSITION_LIMIT:
                                buy_qty = min(position_adjustment, POSITION_LIMIT - current_pos)
                                if buy_qty > 0:
                                    orders.append(Order(product, best_ask, buy_qty))
                        else:  # Need to sell
                            if best_bid and current_pos > -POSITION_LIMIT:
                                sell_qty = min(abs(position_adjustment), POSITION_LIMIT + current_pos)
                                if sell_qty > 0:
                                    orders.append(Order(product, best_bid, -sell_qty))

            # INVENTORY: Multi-Strategy Ensemble with Risk Parity
            elif product == "INVENTORY":
                if len(hist_data["prices"][product]) >= 40:
                    prices = hist_data["prices"][product]
                    
                    if product not in hist_data["ensemble_signals"]:
                        hist_data["ensemble_signals"][product] = {
                            "momentum_signal": 0,
                            "mean_reversion_signal": 0,
                            "volatility_signal": 0,
                            "ensemble_weight": 0
                        }
                    
                    ensemble_data = hist_data["ensemble_signals"][product]
                    
                    # Strategy 1: Momentum Signal
                    short_ma = np.mean(prices[-5:])
                    long_ma = np.mean(prices[-20:])
                    momentum_signal = (short_ma - long_ma) / long_ma if long_ma > 0 else 0
                    ensemble_data["momentum_signal"] = momentum_signal
                    
                    # Strategy 2: Mean Reversion Signal
                    sma = np.mean(prices[-20:])
                    mean_reversion_signal = (sma - mid_price) / sma if sma > 0 else 0
                    ensemble_data["mean_reversion_signal"] = mean_reversion_signal
                    
                    # Strategy 3: Volatility Signal
                    volatility = np.std(prices[-10:])
                    avg_volatility = np.mean([np.std(prices[i:i+10]) for i in range(len(prices)-20, len(prices)-10)])
                    volatility_signal = (volatility - avg_volatility) / avg_volatility if avg_volatility > 0 else 0
                    ensemble_data["volatility_signal"] = volatility_signal
                    
                    # Calculate ensemble weight based on signal agreement
                    signals = [momentum_signal, mean_reversion_signal, volatility_signal]
                    signal_agreement = 1 - np.std(signals)  # Higher agreement = higher weight
                    ensemble_data["ensemble_weight"] = max(0.1, signal_agreement)
                    
                    # Risk parity position sizing
                    volatility_ratio = volatility / mid_price if mid_price > 0 else 1
                    risk_adjusted_size = int(10 / (volatility_ratio + 0.1))
                    
                    # Combined signal
                    combined_signal = (
                        momentum_signal * 0.4 +
                        mean_reversion_signal * 0.4 +
                        volatility_signal * 0.2
                    ) * ensemble_data["ensemble_weight"]
                    
                    # Trading logic
                    threshold = 0.02
                    if abs(combined_signal) > threshold:
                        if combined_signal > 0:  # Buy signal
                            if best_ask and current_pos < POSITION_LIMIT:
                                buy_qty = min(risk_adjusted_size, POSITION_LIMIT - current_pos)
                                if buy_qty > 0:
                                    orders.append(Order(product, best_ask, buy_qty))
                        else:  # Sell signal
                            if best_bid and current_pos > -POSITION_LIMIT:
                                sell_qty = min(risk_adjusted_size, POSITION_LIMIT + current_pos)
                                if sell_qty > 0:
                                    orders.append(Order(product, best_bid, -sell_qty))

            # SUNDIAL: Time-Based Arbitrage with Calendar Effects
            elif product == "SUNDIAL":
                if len(hist_data["prices"][product]) >= 50:
                    prices = hist_data["prices"][product]
                    
                    if product not in hist_data["time_data"]:
                        hist_data["time_data"][product] = {
                            "time_step": 0,
                            "seasonal_pattern": [],
                            "intraday_volatility": []
                        }
                    
                    time_data = hist_data["time_data"][product]
                    time_data["time_step"] += 1
                    
                    # Track seasonal patterns (simplified)
                    if len(time_data["seasonal_pattern"]) < 100:
                        time_data["seasonal_pattern"].append(mid_price)
                    else:
                        time_data["seasonal_pattern"] = time_data["seasonal_pattern"][1:] + [mid_price]
                    
                    # Calculate intraday volatility
                    if len(prices) >= 10:
                        recent_volatility = np.std(prices[-10:])
                        time_data["intraday_volatility"].append(recent_volatility)
                        time_data["intraday_volatility"] = time_data["intraday_volatility"][-20:]
                    
                    # Time-based trading patterns
                    time_step = time_data["time_step"]
                    
                    # Pattern 1: End-of-period mean reversion
                    if len(time_data["seasonal_pattern"]) >= 20:
                        seasonal_mean = np.mean(time_data["seasonal_pattern"][-20:])
                        seasonal_deviation = (mid_price - seasonal_mean) / seasonal_mean if seasonal_mean > 0 else 0
                        
                        # Stronger mean reversion at certain time steps
                        time_multiplier = 1.0
                        if time_step % 10 == 0:  # Every 10th step
                            time_multiplier = 1.5
                        elif time_step % 5 == 0:  # Every 5th step
                            time_multiplier = 1.2
                        
                        if abs(seasonal_deviation) > 0.015 * time_multiplier:
                            if seasonal_deviation > 0:  # Overvalued
                                if best_bid and current_pos > -POSITION_LIMIT:
                                    sell_qty = min(6, POSITION_LIMIT + current_pos)
                                    if sell_qty > 0:
                                        orders.append(Order(product, best_bid, -sell_qty))
                            else:  # Undervalued
                                if best_ask and current_pos < POSITION_LIMIT:
                                    buy_qty = min(6, POSITION_LIMIT - current_pos)
                                    if buy_qty > 0:
                                        orders.append(Order(product, best_ask, buy_qty))
                    
                    # Pattern 2: Volatility-based momentum
                    if len(time_data["intraday_volatility"]) >= 10:
                        current_vol = time_data["intraday_volatility"][-1]
                        avg_vol = np.mean(time_data["intraday_volatility"][-10:])
                        
                        if current_vol > avg_vol * 1.3:  # High volatility period
                            # Momentum strategy during high volatility
                            short_trend = prices[-1] - prices[-5] if len(prices) >= 5 else 0
                            
                            if short_trend > 0:  # Upward momentum
                                if best_ask and current_pos < POSITION_LIMIT:
                                    buy_qty = min(4, POSITION_LIMIT - current_pos)
                                    if buy_qty > 0:
                                        orders.append(Order(product, best_ask, buy_qty))
                            elif short_trend < 0:  # Downward momentum
                                if best_bid and current_pos > -POSITION_LIMIT:
                                    sell_qty = min(4, POSITION_LIMIT + current_pos)
                                    if sell_qty > 0:
                                        orders.append(Order(product, best_bid, -sell_qty))

            if len(orders) > 0:
                result[product] = orders

        conversions = 0
        traderData = jsonpickle.encode(hist_data)
        return result, conversions, traderData 