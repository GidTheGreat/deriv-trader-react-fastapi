from fastapi import FastAPI,Request,Response,Body,Depends, HTTPException,WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from websockets.asyncio.client import connect
import json
from schemas import UserFeedback
from jwt import create_access_token,get_current_user_from_cookie,get_current_user_ws

from fastapi.responses import JSONResponse
import global_vars
from contextlib import asynccontextmanager
import psycopg2
import asyncio
from runbot import spawn_bot
from fastapi.middleware.cors import CORSMiddleware
from multiprocessing import Manager
from multiprocessing.managers import DictProxy
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    
    yield  # this is where the app “lives”
    print("Shutting down")

app = FastAPI(lifespan=lifespan)
manager=Manager()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"])


def get_token(token_dict=Body(...)):
    if isinstance(token_dict,dict):
        return token_dict["token"]
    
    else:
        return json.loads(token_dict)["token"]



@app.post("/api/login_token")
async def validate_token(req: Request,token: str = Depends(get_token)):
    deriv_url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    print(token)
    try:
        async with connect(deriv_url) as ws:
            print("connected")
            await ws.send(json.dumps({"authorize": token}))
            response = await ws.recv()
            data = json.loads(response)
            
            if "error" in data:
                raise HTTPException(status_code=401, 
                                    detail=data["error"].get("message", "Invalid token"))

            auth = data.get("authorize", {})
            balance = auth.get("balance")
            name = auth.get("fullname")
            email = auth.get("email")
            
            global_vars.tokens[email]=token
            jt_token = create_access_token(email)

            response = JSONResponse({"balance": balance,
                "name": name})
            response.set_cookie(
                key="access_token",
                value=jt_token,
                httponly=True,
                secure=False,        # only HTTPS
                samesite="Lax",     # or "Strict"
                max_age=1800      # seconds
            )
            return response
            
    except Exception as e:
        print(e)
        return {"error": str(e)}
   
    

@app.post("/api/start_bot")
async def start_bot(current_user:str = Depends(get_current_user_from_cookie)):
    if current_user in global_vars.active_bots:
        return {"bot status":f"bot already running for {current_user}"}
    elif current_user not in global_vars.active_bots:
        
        decrypted_token = global_vars.tokens[current_user]
        status_messages=manager.dict()
        status_messages[current_user]=manager.dict()
        if "ticks" not in status_messages[current_user]:
            status_messages[current_user]["ticks"]= manager.dict()
            status_messages[current_user]["connection"]= manager.dict()
            status_messages[current_user]["trades"]= manager.dict()
            status_messages[current_user]["profit_loss"]= manager.dict()
            status_messages[current_user]["account balance"]= manager.dict()
            status_messages[current_user]["proposal"]= manager.dict()
        
        spawned_bot_process = spawn_bot(decrypted_token, status_messages[current_user])
        global_vars.active_bots[current_user]={"bot": spawned_bot_process,
                                               "bot_data": status_messages}
        
        return {"bot status":f"bot started for {current_user}"}
    
@app.post("/api/stop_bot")
async def stop_bot(current_user:str = Depends(get_current_user_from_cookie)):
    if current_user not in global_vars.active_bots:
        return {"bot status":f"no bot running for {current_user}"}
    elif current_user in global_vars.active_bots:
        global_vars.active_bots[current_user]["bot"].terminate()
        global_vars.active_bots[current_user]["bot"].join()
        del global_vars.active_bots[current_user]
        return {"bot status":f"bot stopped for {current_user}"}

@app.post("/api/logout")
async def logout():
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie(
        key="access_token",  # same name used when setting it
        path="/"
    )
    return response


@app.websocket("/ws")
async def websocket_endpont(websocket: WebSocket,
                            current_user: str = Depends(get_current_user_ws)):
    
    await websocket.accept()
    
    while True:
        try:
            if current_user in global_vars.active_bots:
                st = global_vars.active_bots[current_user]["bot_data"]
                st= st[current_user]
                parsed = parse(st)
                await websocket.send_json(parsed)  
                await asyncio.sleep(2) 
            else:
                await websocket.send_json({"bot status":"no active bot running"})  
                await asyncio.sleep(60)
        except WebSocketDisconnect:
            break

def parse(st):
    parsed_dict = {}
    for key in st.keys():
        st_2 =dict(st[key])
        parsed_dict[key]=st_2

    return parsed_dict
        
            
app.mount("/", StaticFiles(directory="dist", html=True), name="react_app")