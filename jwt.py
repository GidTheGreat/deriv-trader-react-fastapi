from jose import jwt,JWTError
from datetime import datetime,timedelta
from schemas import settings
from fastapi import HTTPException,Request,Header,Cookie

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_email:str):
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_email, "exp": expire}
    token = jwt.encode(to_encode, settings.secret_key, 
                       algorithm=settings.algorithm)
    return token

def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return payload.get("sub")

def get_current_user_ws(access_token:str=Cookie(...)):
    payload = jwt.decode(access_token, settings.secret_key, algorithms=[settings.algorithm])
    return payload.get("sub")

def get_current_user(authorization: str = Header(...)):
    try:
        
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        print("payload is :",payload)
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_email
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")