from fastapi import FastAPI,Request,Response,Body,Depends, HTTPException,Form
from fastapi.middleware.cors import CORSMiddleware
from websockets.asyncio.client import connect
import json
from schemas import UserFeedback
from database import database_conn
from jwt import create_access_token,get_current_user_from_cookie
from schemas import settings
from fastapi.responses import JSONResponse
import global_vars
from contextlib import asynccontextmanager
from database import database_conn
from encrypt_decrypt import encrypt_token,decrypt_token
import psycopg2
import asyncio
from runbot import spawn_bot
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    try:
        global_vars.db_connection, global_vars.db_cursor = database_conn()
    except Exception as error:
        print(error)
    
    yield  # this is where the app “lives”
    print("Shutting down")

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"])


def get_token(token_dict=Body(...)):
    if isinstance(token_dict,dict):
        return token_dict["token"]
    
    else:
        return json.loads(token_dict)["token"]

async def handle_db_update(email,name,ecrypted_token,plain_token):
    global_vars.db_cursor.execute("SELECT * FROM deriv_users")
    data=global_vars.db_cursor.fetchone()
    if not data:
        global_vars.db_cursor.execute("INSERT INTO deriv_users (name,email,token) VALUES(%s,%s,%s)",
                              (name,email,ecrypted_token))
    else:
        global_vars.db_cursor.execute("SELECT token FROM deriv_users WHERE email=%s",(email,))
        token_from_db = global_vars.db_cursor.fetchone()
        decrypted_token = decrypt_token(token_from_db['token'])
        print("type of token received",plain_token,
             "db:" ,decrypted_token)
        if token_from_db and  plain_token!= decrypted_token:
            print('updating token')
            global_vars.db_cursor.execute(
                "UPDATE deriv_users SET token=%s WHERE email=%s",(ecrypted_token,email)
            )
        elif not token_from_db:
            global_vars.db_cursor.execute("INSERT INTO deriv_users (name,email,token) VALUES(%s,%s,%s)",
                              (name,email,ecrypted_token))
            
    global_vars.db_connection.commit()

    

@app.post("/login_token")
async def validate_token(req: Request,token: str = Depends(get_token)):
    deriv_url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    print(token)
    """
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
            encrypted_token =encrypt_token(token)
            await handle_db_update(email,name,encrypted_token,token)
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
    """

@app.post("/start_bot")
async def start_bot(current_user:str = Depends(get_current_user_from_cookie)):
    if current_user in global_vars.active_bots:
        return {"bot status":f"bot already running for {current_user}"}
    elif current_user not in global_vars.active_bots:
        spawned_bot_process = spawn_bot()
        global_vars.active_bots[current_user]=spawned_bot_process
        return {"bot status":f"bot started for {current_user}"}
    
@app.post("/stop_bot")
async def stop_bot(current_user:str = Depends(get_current_user_from_cookie)):
    if current_user not in global_vars.active_bots:
        return {"bot status":f"no bot running for {current_user}"}
    elif current_user in global_vars.active_bots:
        global_vars.active_bots[current_user].terminate()
        global_vars.active_bots[current_user].join()
        del global_vars.active_bots[current_user]
        return {"bot status":f"bot stopped for {current_user}"}

@app.post("/logout")
async def logout():
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie(
        key="access_token",  # same name used when setting it
        path="/"
    )
    return response
    
    
