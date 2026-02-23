from multiprocessing import Process
import asyncio
from bot.main import main

def start_worker():
    asyncio.run(main()) 

def spawn_bot():
    proc = Process(target=start_worker)
    proc.start()
    return proc