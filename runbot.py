from multiprocessing import Process
import asyncio
from bot.main import main

def start_worker(status_messages, token):
    asyncio.run(main(status_messages, token)) 
    
def spawn_bot(token, status_messages):
    
    proc = Process(target=start_worker,args=(status_messages,token))
    proc.start()
    return proc