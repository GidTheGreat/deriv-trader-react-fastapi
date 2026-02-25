from jose import jwt,JWTError
from datetime import datetime,timedelta
from fastapi import HTTPException,Request,Header,Cookie
import global_vars

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_email:str):
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_email, "exp": expire}
    token = jwt.encode(to_encode, global_vars.SECRET_KEY, 
                       algorithm=global_vars.ALGORITHM)
    return token

def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    payload = jwt.decode(token, global_vars.SECRET_KEY, algorithms=[global_vars.ALGORITHM])
    return payload.get("sub")

def get_current_user_ws(access_token:str=Cookie(...)):
    payload = jwt.decode(access_token, global_vars.SECRET_KEY, algorithms=[global_vars.ALGORITHM])
    return payload.get("sub")

def get_current_user(authorization: str = Header(...)):
    try:
        
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        payload = jwt.decode(token, global_vars.SECRET_KEY, algorithms=[global_vars.ALGORITHM])
        user_email = payload.get("sub")
        print("payload is :",payload)
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_email
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")