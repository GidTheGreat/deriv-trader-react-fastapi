"""Look for a worthy trade entry"""
import json
from datetime import datetime
import bot.shared_vars
async def sub_accu_data(ws,growth_rate=0.05):
    """Subscribe to accumulator relevant info"""
    await ws.send(json.dumps({
        "proposal": 1,
        "amount": 10,
        "basis": "stake",
        "contract_type": "ACCU",
        "currency": "USD",
        "growth_rate": growth_rate,
        "symbol": "R_25",
        "subscribe": 1
        }
        ))
    
def parse_proposal_data(server_response,status_messages):
    """Process accumulator relevant info"""

    last_tick_time = datetime.fromtimestamp(server_response["proposal"]["contract_details"].get("last_tick_epoch",17000000))
    higher_barrier = server_response["proposal"]["contract_details"].get("high_barrier")
    low_barrier = server_response["proposal"]["contract_details"].get("low_barrier")
    ticks_statyed_in = server_response["proposal"]["contract_details"].get("ticks_stayed_in")

    status_messages["proposal"]["proposal_data"]=(f"last tick time:{last_tick_time},"
    f"high barrier:{higher_barrier},low barrier:{low_barrier},ticks stayed in:{ticks_statyed_in[0]}")

    #status_messages["proposal"]["ticks_stayed_in"]=server_response
    if ticks_statyed_in[0] > 2 and ticks_statyed_in[0] < 4:
        bot.shared_vars.time_to_trade=True

async def look_for_trade(ws, symbol, status_messages):
    """Decide whether to trade"""
    if not bot.shared_vars.active_trade:
        tick_data= list(bot.shared_vars.market_data[symbol]["ticks"])
        if not bot.shared_vars.sub_accu:
            await sub_accu_data(ws,growth_rate=0.05)
            bot.shared_vars.sub_accu=True

        if bot.shared_vars.time_to_trade:
            if bot.shared_vars.increase_stake:
                bot.shared_vars.stake*=3
                bot.shared_vars.take_profit*=3
                bot.shared_vars.increase_stake=False
        
            await ws.send(json.dumps({
                "buy": 1,
                "price": bot.shared_vars.stake,
                "parameters": {
                    "amount": bot.shared_vars.stake,
                    "basis": "stake",
                    "contract_type": "ACCU",
                    "currency": "USD",
                    "growth_rate": 0.05,
                    "symbol": symbol,
                    "limit_order": {
                    "take_profit": bot.shared_vars.take_profit
                    }
                },
                "subscribe": 1
                }
            ))
            bot.shared_vars.active_trade = True
            bot.shared_vars.time_to_trade = False
            bot.shared_vars.stake=1
            bot.shared_vars.take_profit=0.2

        


