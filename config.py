# ==========================================================
# Scanner Settings
# ==========================================================

# Exit when EMA50-EMA200 gap falls below this level
# after a confirmed Death Cross.
DEATH_CROSS_CONFIRMATION = -0.05

# Portfolio kill switch (%)
STOP_LOSS_PERCENT = -15

# Ignore penny stocks
MIN_STOCK_PRICE = 50

# Reject abnormal historical data
# (single-day move larger than this percentage)
MAX_DAILY_MOVE_PERCENT = 70

# Golden Cross should have occurred within the last N candles
GOLDEN_CROSS_LOOKBACK = 3

# ==========================================================
# EMA Settings
# ==========================================================

ENTRY_FAST_EMA = 50
ENTRY_SLOW_EMA = 200

EXIT_FAST_EMA = 9
EXIT_SLOW_EMA = 21

# ==========================================================
# Strategy Settings
# ==========================================================

# Exit when EMA50-EMA200 gap falls below 50%
# of its maximum value after the Golden Cross.
GAP_THRESHOLD = 0.50

# ==========================================================
# Performance
# ==========================================================

USE_CACHE = True
MAX_WORKERS = 8

# ==========================================================
# Backtest Period
# ==========================================================

BACKTEST_YEARS = 10