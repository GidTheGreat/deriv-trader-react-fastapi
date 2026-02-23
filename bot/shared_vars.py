import asyncio
from collections import deque
mode="live"

active_trade = False

tick_processed = asyncio.Event()

delay = 2/10

total_profit = 0

profit = 0

markets = ["R_25"]

market_data ={symbol:{"ticks":deque(maxlen=500)} for symbol in markets}

sub_accu = False

time_to_trade =False

increase_stake= False

stake = 1

take_profit = 0.2