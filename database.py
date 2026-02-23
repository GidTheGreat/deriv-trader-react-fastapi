import psycopg2
from psycopg2.extras import RealDictCursor
import global_vars
from schemas import settings

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

