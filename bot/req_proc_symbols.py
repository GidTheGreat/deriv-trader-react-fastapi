"""Request active symbols and process server response to get
a list of symbols"""

import json

def active_symbols(server_resp):
    """Parse server response to get the list of active symbols"""

    #print("parsing server response")
    
    #Get list of active symbols.Each entry is a dict
    symbols_dict_list = server_resp.get("active_symbols",[])

    #Create actual list of symbols
    symbols_list = [symbol_dict.get("symbol") 
                    for symbol_dict in symbols_dict_list]
    
    #print(symbols_list)
    #print("server response parsed")
    return symbols_list
    
async def req_active_symbols(ws):
    """Request active symbols"""
    await ws.send(json.dumps(
        {
            "active_symbols": "brief",
            "product_type": "basic"
        }
    ))
    #print("req succesful")
