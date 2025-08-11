# IMC Trading Competition - Prosperity Strategies

This repository contains 5 different trading strategies for the IMC Trading Competition, each implementing unique approaches to algorithmic trading across different market conditions and products.

## Overview

Each round implements a different trading philosophy and set of strategies, ranging from basic market making to advanced statistical arbitrage and machine learning-inspired approaches. The strategies are designed to be educational and demonstrate various trading concepts while maintaining risk management principles.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Strategy Progression                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Round 1       │   Round 2       │   Round 3                   │
│   Momentum      │   Microstructure │   Multi-Timeframe           │
│   + Risk Mgmt   │   + Order Book  │   + Adaptive                │
├─────────────────┼─────────────────┼─────────────────────────────┤
│   Round 4       │   Round 5       │                             │
│   Statistical   │   Ensemble      │                             │
│   Arbitrage     │   + Risk Parity │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## Round 1: Momentum-Based Trading with Risk Management

**File:** `round1.py`

### Strategy Overview
Round 1 focuses on momentum-based strategies with integrated risk management, using three different products to demonstrate various approaches to trend following and mean reversion.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Round 1 Strategies                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   PEARLS        │   BANANAS       │   COCONUTS                  │
│   Kalman Filter │   Momentum      │   Bollinger Bands           │
│   ┌─────────┐   │   ┌─────────┐   │   ┌─────────┐               │
│   │Estimate │   │   │Short MA │   │   │Upper    │               │
│   │Fair     │   │   │vs Long  │   │   │Band     │               │
│   │Value    │   │   │MA       │   │   │┌─────┐  │               │
│   └─────────┘   │   └─────────┘   │   ││Price│  │               │
│   ┌─────────┐   │   ┌─────────┐   │   │└─────┘  │               │
│   │Trade on │   │   │Follow   │   │   │Lower    │               │
│   │Deviation│   │   │Trend    │   │   │Band     │               │
│   └─────────┘   │   └─────────┘   │   └─────────┘               │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Products and Strategies

#### PEARLS: Statistical Arbitrage with Kalman Filter
- **Approach:** Uses a simplified Kalman filter to estimate the "true" price of PEARLS
- **Logic:** 
  - Maintains a running estimate of the fair value using Kalman filtering
  - Trades when the current price deviates significantly from the estimated fair value
  - Uses a threshold of 0.5 for trading decisions
- **Risk Management:** Position limits of 20 units with conservative position sizing (3 units per trade)
- **Key Features:**
  - Adaptive estimation that responds to new information
  - Reduces noise in price data
  - Suitable for products with stable fundamentals

**Kalman Filter Process:**
```
Price Data → Kalman Update → Fair Value Estimate → Trading Signal
     ↓              ↓              ↓                    ↓
  Current      Kalman Gain    New Estimate        Buy/Sell
  Price        Calculation    (Filtered)          Decision
```

#### BANANAS: Momentum Breakout Strategy
- **Approach:** Identifies and follows price momentum using multiple moving averages
- **Logic:**
  - Compares 5-period and 20-period moving averages
  - Enters positions when momentum exceeds 0.5 threshold
  - Uses volatility-adjusted position sizing
- **Risk Management:** Dynamic position sizing based on recent volatility
- **Key Features:**
  - Captures trending markets effectively
  - Adapts to changing market conditions
  - Volatility-based risk adjustment

**Momentum Calculation:**
```
Short MA (5 periods) - Long MA (20 periods) = Momentum Score
     ↓                        ↓                      ↓
  Recent Trend           Historical Trend        Signal Strength
```

#### COCONUTS: Volatility-Based Mean Reversion
- **Approach:** Uses Bollinger Bands for mean reversion trading
- **Logic:**
  - Calculates 15-period moving average and standard deviation
  - Creates upper and lower bands at ±2 standard deviations
  - Trades when price breaks outside the bands
- **Risk Management:** Position sizing scales with volatility ratio
- **Key Features:**
  - Effective in sideways markets
  - Adapts to changing volatility
  - Clear entry and exit signals

**Bollinger Bands Visualization:**
```
Price
  │                    Upper Band (SMA + 2σ)
  │    ╭─────────────────────────────────╮
  │    │                                 │
  │    │         Price Movement          │
  │    │                                 │
  │    ╰─────────────────────────────────╯
  │                    Lower Band (SMA - 2σ)
  └─────────────────────────────────────────→ Time
```

## Round 2: Market Microstructure and Order Book Analysis

**File:** `round2.py`

### Strategy Overview
Round 2 focuses on market microstructure analysis, using order book data and market structure to make trading decisions.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Round 2 Strategies                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ PINA_COLADAS    │  DIVING_GEAR    │    BERRIES                  │
│ Order Book      │  Spread-Based   │  VWAP Strategy              │
│ Imbalance       │  Market Making  │                             │
│ ┌─────────────┐ │  ┌─────────────┐ │  ┌─────────────┐           │
│ │Bid Volume   │ │  │Wide Spread  │ │  │Volume       │           │
│ │vs Ask       │ │  │Place Orders │ │  │Weighted     │           │
│ │Volume       │ │  │Inside       │ │  │Average      │           │
│ └─────────────┘ │  └─────────────┘ │  └─────────────┘           │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Products and Strategies

#### PINA_COLADAS: Order Book Imbalance Strategy
- **Approach:** Analyzes the imbalance between bid and ask volumes in the order book
- **Logic:**
  - Calculates order book imbalance: (bid_volume - ask_volume) / total_volume
  - Trades when imbalance exceeds ±0.3 threshold
  - Uses 5-period average of imbalance for signal generation
- **Risk Management:** Position limit of 15 units with 4-unit trade sizes
- **Key Features:**
  - Captures short-term supply/demand imbalances
  - Responds quickly to market pressure
  - Uses actual order book data

**Order Book Imbalance:**
```
Order Book State:
Bids: [100@50, 200@49, 150@48]  Asks: [120@51, 180@52, 90@53]
     ↓                              ↓
Total Bid Volume: 450          Total Ask Volume: 390
     ↓                              ↓
Imbalance = (450 - 390) / (450 + 390) = 0.071
```

#### DIVING_GEAR: Spread-Based Market Making
- **Approach:** Adaptive market making based on bid-ask spread analysis
- **Logic:**
  - Calculates spread as percentage of mid-price
  - Places orders inside wide spreads to capture the spread
  - Uses volatility-adjusted minimum spread thresholds
- **Risk Management:** Conservative position sizing with position-based limits
- **Key Features:**
  - Profits from bid-ask spreads
  - Adapts to market volatility
  - Reduces market impact

**Spread Analysis:**
```
Bid: 100@50  Ask: 120@51
     ↓           ↓
Spread = 51 - 50 = 1
Spread % = 1 / 50.5 = 1.98%
Decision: Place orders inside spread if > threshold
```

#### BERRIES: Volume-Weighted Price Strategy
- **Approach:** Uses Volume Weighted Average Price (VWAP) for mean reversion trading
- **Logic:**
  - Calculates VWAP over 15-period window
  - Trades when price deviates more than 2% from VWAP
  - Uses historical price and volume data
- **Risk Management:** 5-unit trade sizes with position limits
- **Key Features:**
  - Incorporates volume information
  - Effective for institutional-style trading
  - Clear mean reversion signals

**VWAP Calculation:**
```
VWAP = Σ(Price × Volume) / Σ(Volume)
     = (P1×V1 + P2×V2 + ... + Pn×Vn) / (V1 + V2 + ... + Vn)
```

## Round 3: Multi-Timeframe Analysis and Adaptive Strategies

**File:** `round3.py`

### Strategy Overview
Round 3 implements advanced multi-timeframe analysis and adaptive strategies that can switch between different market regimes.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Round 3 Strategies                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│DOLPHIN_SIGHTINGS│   BAGUETTE      │      DIP                    │
│Multi-Timeframe  │Regime Detection │Pairs Trading                │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐             │
│ │Short Term   │ │ │Trending     │ │ │Correlation  │             │
│ │Medium Term  │ │ │Mean Revert  │ │ │Analysis     │             │
│ │Long Term    │ │ │Auto Switch  │ │ │Spread       │             │
│ └─────────────┘ │ └─────────────┘ │ │Trading      │             │
│                 │                 │ └─────────────┘             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Products and Strategies

#### DOLPHIN_SIGHTINGS: Multi-Timeframe Trend Analysis
- **Approach:** Combines signals from multiple timeframes for robust trend identification
- **Logic:**
  - Analyzes short-term (5 periods), medium-term (15 periods), and long-term (30 periods) trends
  - Creates weighted consensus score: 50% short + 30% medium + 20% long
  - Uses volatility-adjusted position sizing
- **Risk Management:** Position limit of 25 units with dynamic sizing
- **Key Features:**
  - Reduces false signals from single timeframe
  - Captures trends at multiple scales
  - Robust to market noise

**Multi-Timeframe Weighting:**
```
Trend Score = (Short × 0.5) + (Medium × 0.3) + (Long × 0.2)
     ↓              ↓              ↓              ↓
  Consensus      Recent        Intermediate    Long-term
  Signal         Trend         Trend           Trend
```

#### BAGUETTE: Adaptive Mean Reversion with Regime Detection
- **Approach:** Automatically detects market regime and adapts strategy accordingly
- **Logic:**
  - Calculates regime score based on mean reversion strength
  - Switches between "trending" and "mean_reverting" modes
  - Uses different strategies for each regime
- **Risk Management:** Different position sizes for different regimes
- **Key Features:**
  - Adapts to changing market conditions
  - Combines trend following and mean reversion
  - Self-adjusting strategy

**Regime Detection Flow:**
```
Market Data → Regime Score → Regime Classification → Strategy Selection
     ↓              ↓              ↓                      ↓
  Price &      Mean Reversion   Trending vs        Trend Following
  Volatility   Strength         Mean Reverting     vs Mean Reversion
```

#### DIP: Correlation-Based Pairs Trading
- **Approach:** Implements statistical arbitrage between correlated products
- **Logic:**
  - Calculates correlation between DIP and BAGUETTE
  - Trades when correlation > 0.7
  - Uses z-score analysis of price spreads
- **Risk Management:** 5-unit trade sizes with correlation-based filtering
- **Key Features:**
  - Market-neutral approach
  - Exploits relative value opportunities
  - Reduces directional risk

**Pairs Trading Process:**
```
Product A Price → Correlation → Spread Analysis → Z-Score → Trade Signal
Product B Price →   (>0.7)   →   (A - B)      → (>1.5)  → Buy/Sell
```

## Round 4: Advanced Statistical Arbitrage and ML-Inspired Approaches

**File:** `round4.py`

### Strategy Overview
Round 4 implements sophisticated statistical arbitrage strategies inspired by machine learning and advanced quantitative techniques.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Round 4 Strategies                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   UKULELE       │ PICNIC_BASKET   │   TREASURE_MAP              │
│ Harmonic        │ Basket Trading  │ Hidden Markov               │
│ Patterns        │ with PCA        │ Model                       │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐             │
│ │Fibonacci    │ │ │Correlation  │ │ │Regime       │             │
│ │Retracements │ │ │Matrix       │ │ │Probability  │             │
│ │Pattern      │ │ │Relative     │ │ │Volatility   │             │
│ │Recognition  │ │ │Value        │ │ │Regime       │             │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┘             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Products and Strategies

#### UKULELE: Harmonic Pattern Recognition
- **Approach:** Identifies harmonic price patterns using Fibonacci retracement levels
- **Logic:**
  - Detects local highs and lows in price data
  - Calculates Fibonacci retracement levels (38.2% and 61.8%)
  - Trades when price reaches these levels
- **Risk Management:** 7-unit trade sizes with pattern-based filtering
- **Key Features:**
  - Technical analysis approach
  - Clear entry and exit points
  - Based on market psychology

**Fibonacci Retracement Levels:**
```
High Point
    │
    │    61.8% Retracement
    │    ┌─────────┐
    │    │         │
    │    │ 38.2%   │
    │    │Retrace  │
    │    │         │
    │    └─────────┘
    │
Low Point
```

#### PICNIC_BASKET: Basket Trading with Principal Component Analysis
- **Approach:** Uses correlation analysis to find relative value opportunities
- **Logic:**
  - Calculates correlation matrix across all products
  - Finds most correlated product to PICNIC_BASKET
  - Trades based on relative value when correlation > 0.6
- **Risk Management:** 8-unit trade sizes with correlation thresholds
- **Key Features:**
  - Multi-product analysis
  - Statistical arbitrage approach
  - Reduces single-product risk

**Correlation Matrix Example:**
```
        PEARLS  BANANAS  COCONUTS  BASKET
PEARLS    1.0     0.2      0.1     0.3
BANANAS   0.2     1.0      0.4     0.7  ← Highest correlation
COCONUTS  0.1     0.4      1.0     0.5
BASKET    0.3     0.7      0.5     1.0
```

#### TREASURE_MAP: Hidden Markov Model for Regime Detection
- **Approach:** Advanced regime detection using simplified Hidden Markov Model concepts
- **Logic:**
  - Tracks regime probability based on trend strength
  - Identifies three regimes: trending, mean_reverting, sideways
  - Adjusts strategy and position sizing based on regime
- **Risk Management:** Volatility-adjusted position sizing with regime-based multipliers
- **Key Features:**
  - Sophisticated regime detection
  - Adaptive strategy selection
  - Risk-adjusted sizing

**Regime State Machine:**
```
Trending ←───┐    ┌───→ Mean Reverting
    │        │    │         │
    │        │    │         │
    └────────┴────┴─────────┘
         Sideways
```

## Round 5: Ensemble Methods and Advanced Risk Management

**File:** `round5.py`

### Strategy Overview
Round 5 implements ensemble methods and advanced risk management techniques, combining multiple strategies and sophisticated risk controls.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Round 5 Strategies                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│COCONUT_COUPON   │   INVENTORY     │    SUNDIAL                  │
│Delta Hedging    │   Ensemble      │ Time-Based                  │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐             │
│ │Delta        │ │ │Momentum     │ │ │Seasonal     │             │
│ │Calculation  │ │ │Mean Rev     │ │ │Patterns     │             │
│ │Gamma        │ │ │Volatility   │ │ │Calendar     │             │
│ │Position     │ │ │Ensemble     │ │ │Effects      │             │
│ │Targeting    │ │ │Weighting    │ │ │Time Steps   │             │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┘             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Products and Strategies

#### COCONUT_COUPON: Options-Inspired Delta Hedging
- **Approach:** Implements delta hedging concepts from options trading
- **Logic:**
  - Calculates "delta" based on price momentum using tanh function
  - Tracks "gamma" (rate of change of delta)
  - Adjusts position to maintain target delta
- **Risk Management:** Delta-based position targeting with 35-unit limits
- **Key Features:**
  - Options-inspired approach
  - Dynamic position management
  - Risk-neutral positioning

**Delta Hedging Process:**
```
Price Movement → Momentum → Delta Calculation → Position Adjustment
     ↓              ↓              ↓                ↓
  Current      Short vs Long   Tanh Function   Target Position
  Change       Moving Avg      (-1 to +1)      vs Current
```

#### INVENTORY: Multi-Strategy Ensemble with Risk Parity
- **Approach:** Combines multiple strategies with risk parity principles
- **Logic:**
  - Implements three strategies: momentum, mean reversion, volatility
  - Calculates ensemble weight based on signal agreement
  - Uses risk parity for position sizing
- **Risk Management:** Risk-adjusted sizing based on volatility ratios
- **Key Features:**
  - Ensemble approach reduces overfitting
  - Risk parity ensures balanced risk allocation
  - Signal agreement weighting

**Ensemble Strategy Combination:**
```
Strategy 1: Momentum     ──┐
Strategy 2: Mean Rev     ──┼──→ Signal Agreement → Ensemble Weight
Strategy 3: Volatility   ──┘
     ↓
Combined Signal × Weight = Final Decision
```

#### SUNDIAL: Time-Based Arbitrage with Calendar Effects
- **Approach:** Exploits time-based patterns and seasonal effects
- **Logic:**
  - Tracks seasonal patterns and intraday volatility
  - Implements stronger mean reversion at specific time steps
  - Uses volatility-based momentum during high volatility periods
- **Risk Management:** Time-based position sizing with calendar effects
- **Key Features:**
  - Time-aware trading
  - Seasonal pattern recognition
  - Volatility regime adaptation

**Time-Based Trading Patterns:**
```
Time Step: 1  2  3  4  5  6  7  8  9  10
Pattern:   ─  ─  ─  ─  ↑  ─  ─  ─  ─  ↑
                     5th step   10th step
                  1.2x weight  1.5x weight
```

## Common Features Across All Rounds

### Risk Management
- **Position Limits:** Each round has appropriate position limits (15-35 units)
- **Position Sizing:** Dynamic sizing based on volatility and market conditions
- **Stop Losses:** Implicit through position limits and signal thresholds

### Data Management
- **Historical Data:** All strategies maintain rolling price histories
- **State Persistence:** Uses `traderData` to persist information between calls
- **Memory Management:** Limits historical data to prevent memory issues

### Market Data Processing
- **Order Book Analysis:** Extracts best bid/ask and calculates mid-prices
- **Spread Analysis:** Monitors bid-ask spreads for market making opportunities
- **Volume Analysis:** Incorporates volume information where available

## Implementation Notes

### Dependencies
- `numpy`: For numerical computations and statistical functions
- `jsonpickle`: For data serialization and persistence
- `statistics`: For basic statistical calculations
- `math`: For mathematical operations

### Performance Considerations
- **Computational Efficiency:** All strategies use efficient algorithms
- **Memory Usage:** Rolling windows prevent unbounded memory growth
- **Latency:** Minimal computational overhead for real-time trading

### Extensibility
- **Modular Design:** Each product strategy is independent
- **Parameter Tuning:** Key parameters can be easily adjusted
- **Strategy Addition:** New strategies can be added following the same pattern

## Usage

To use any of these strategies:

1. Replace the existing `round1.py` with the desired round file
2. Ensure all dependencies are installed
3. The strategy will automatically handle data persistence and state management

## Educational Value

These strategies demonstrate:
- **Market Making:** Passive liquidity provision
- **Trend Following:** Momentum-based strategies
- **Mean Reversion:** Statistical arbitrage approaches
- **Risk Management:** Position sizing and limits
- **Market Microstructure:** Order book analysis
- **Multi-Timeframe Analysis:** Combining different time horizons
- **Regime Detection:** Adaptive strategy selection
- **Ensemble Methods:** Combining multiple strategies
- **Advanced Risk Management:** Options-inspired approaches

Each round builds upon the previous ones, introducing more sophisticated concepts while maintaining educational clarity and practical applicability. 