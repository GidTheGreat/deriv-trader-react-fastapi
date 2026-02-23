"""Login to deriv account and subscribe to balance"""
import json
import asyncio

async def authorize(ws,api_token,status_messages):
    """Authorize access to deriv account"""

    status_messages["connection"]["auth"] =("Attempting to authorize access")
    await ws.send(json.dumps({
        "authorize": api_token
    }))


async def subscribe_balance(ws):
    """Subscribe to account balance"""

    #print("Attempting to subscribe to account balance")
    await ws.send(json.dumps({
        "balance": 1,
        "subscribe": 1
    }))

def account_balance(server_response, status_messages):
    """Account balance info"""

    balance_dict = server_response.get("balance",{})
    balance = balance_dict.get("balance",{})
    currency = balance_dict.get("currency",{})
    status_messages["account balance"]["current balance"] =(f"{balance}{currency}")
