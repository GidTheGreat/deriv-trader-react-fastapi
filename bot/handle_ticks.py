"""Subscrribe and process tick stream"""

import json
from datetime import datetime
from bot.look_for_trade import look_for_trade
import bot.shared_vars

async def sub_ticks(ws,symbol):
    """Subscribe to tick stream"""
    #print("Attempting to subscribe to ticks")
    await ws.send(json.dumps({
        "ticks": symbol,
        "subscribe": 1
    }))

async def handle_ticks(server_response, ws, status_messages):
    """Parse ticks"""
    symbol = server_response.get("symbol")
    quote = server_response.get("quote")
    epoch = server_response.get("epoch")

    bot.shared_vars.market_data[symbol]["ticks"].append({"epoch":epoch,"quote":quote})
    
    status_messages["ticks"]["tick"] =(f"quote:{quote},"
    f"epoch:{datetime.fromtimestamp(epoch)}, symbol:{symbol}")

    if not bot.shared_vars.active_trade:
        await look_for_trade(ws, symbol,status_messages)