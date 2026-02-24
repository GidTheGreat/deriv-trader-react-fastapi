import psycopg2
from psycopg2.extras import RealDictCursor
import global_vars
from schemas import settings
from encrypt_decrypt import decrypt_token

def database_conn():
    try:
        conn = psycopg2.connect(host=settings.host,database=settings.database,
                                user=settings.user_database,password=settings.password,
                                cursor_factory=RealDictCursor)
        print("Connected to database")
        cursor = conn.cursor()
        
        return conn,cursor
    except Exception as e:
        print(e)

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