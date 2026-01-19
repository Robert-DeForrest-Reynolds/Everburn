if __name__ != '__main__':
	from sys import exit
	exit(1)


from os import system
from asyncio import run, create_task
from sqlite3 import connect

from EverburnLauncher.IPC import Execute_Queue, User_Input_Loop
from EverburnLauncher.Utils import *
from EverburnLauncher.Logging import *
from EverburnLauncher.Everburn import Everburn


E = Everburn()


async def Main():
	ExecutionQueue = create_task(Execute_Queue(E))
	try:
		await User_Input_Loop(E)
		await Cleanup(E)
	finally:
		await E.OutputQueue.put(None)
		await ExecutionQueue # wait for ExecutionQueue to finish before closing out       


Connection = connect("MainEvent.db")

Cursor = Connection.cursor()

Cursor.execute("""
CREATE TABLE IF NOT EXISTS Fighters (
    FighterId   INTEGER PRIMARY KEY AUTOINCREMENT,
    OwnerId     TEXT NOT NULL,
    Name        TEXT NOT NULL,
    Level       INTEGER NOT NULL DEFAULT 1,
    CreatedAt   TEXT NOT NULL DEFAULT (datetime('now'))
);
""")


run(Main())

Connection.close()

Log(INFO, "Closing Everburn")

if E.Restart:
	Log(INFO, "Restarting Everburn...")
	system("launcher") # need to eventually pass bots that were alive to be revived