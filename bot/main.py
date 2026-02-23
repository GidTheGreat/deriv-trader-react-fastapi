"""Establish a connection to deriv and place trade.
Use websocket version 16"""

import asyncio
from websockets.asyncio.client import connect
import json

from bot.req_proc_symbols import req_active_symbols,active_symbols
from bot.auth_balance import authorize,subscribe_balance,account_balance
from bot.handle_ticks import sub_ticks,handle_ticks
import bot.shared_vars
from bot.status2 import background_live_updates,status_messages
from bot.look_for_trade import parse_proposal_data


async def connect_to_ws():
    """Establish connection to deriv 
    websocket endpoint"""
    app_id = 82750 
    token = "xQHRRDpUWkGNGNW" 
    uri = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    
    status_messages["connection"]["connection_status"] =("attempting to establish connection")
    
    async with connect(uri) as ws:
        status_messages["connection"]["connection_status"] ="[open] Connection established"
        await req_active_symbols(ws)
        await authorize(ws,token,status_messages)
        
        while True:
            message_json = await ws.recv()
            message = json.loads(message_json)
            if "active_symbols" in message:
                active_syms_list = active_symbols(message)
                for symbol in bot.shared_vars.markets:
                    if symbol in active_syms_list:
                        await sub_ticks(ws,symbol)
            
            elif "authorize" in message:
                status_messages["connection"]["auth"] =("successfully authorized")
                await subscribe_balance(ws)
                
            elif "balance" in message:
                account_balance(message,status_messages)

            elif "tick" in message:
                    await handle_ticks(message.get("tick"), ws, status_messages)
            
            elif "buy" in message:
                status_messages["trades"]["trade placed"] =("successfully")               

            elif "proposal_open_contract" in message:
                if message["proposal_open_contract"]['status'] == "open":
                    profit_perc = message["proposal_open_contract"]['profit_percentage']
                    bot.shared_vars.profit = message["proposal_open_contract"]['profit']
                    trade_status = message["proposal_open_contract"]['status']
                    status_messages["profit_loss"]["active_trade"] =(f"profit percentage:{profit_perc},"
                        f"profit:{bot.shared_vars.profit},trade status:{trade_status}")
                
                else:
                    if bot.shared_vars.profit < 0:
                        bot.shared_vars.increase_stake = True
                    bot.shared_vars.total_profit+=bot.shared_vars.profit
                    status_messages["connection"]["trade placed"] =("resetting active trade")
                    status_messages["profit_loss"]["stats"] =(f"Total Profit:{bot.shared_vars.total_profit}")
                    bot.shared_vars.active_trade = False

            elif "proposal" in message:
                parse_proposal_data(message,status_messages)
                
            else:
                print(message)
                    
    

async def main():
    task1 = asyncio.create_task(connect_to_ws())
    task2 = asyncio.create_task(background_live_updates())
    await asyncio.gather(task1, task2)
    
    

if __name__ == '__main__':
    asyncio.run(main())