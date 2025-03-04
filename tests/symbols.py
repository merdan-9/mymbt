#!/usr/bin/env python3
"""
Symbols configuration file for price monitoring
This file contains the list of symbols to monitor and their respective thresholds
"""

# List of symbols to monitor with their thresholds
# Format: [symbol, upper_threshold, lower_threshold]
# Set threshold to None if you don't want to monitor that direction
SYMBOLS_TO_MONITOR = [
    {"symbol": "DOGE-USD", "upper_threshold": 0.194, "lower_threshold": 0.18888},
    {"symbol": "BTC-USD", "upper_threshold": 85500, "lower_threshold": 80900},
    # {"symbol": "ADA-USD", "upper_threshold": 0.50, "lower_threshold": 0.35},
    # {"symbol": "XRP-USD", "upper_threshold": 0.60, "lower_threshold": 0.45}, 85555, 0.21
] 
