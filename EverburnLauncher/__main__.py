if __name__ != '__main__':
	from sys import exit
	exit(1)


from os import system
from asyncio import run, create_task

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


run(Main())

Log(INFO, "Closing Everburn")

if E.Restart:
	Log(INFO, "Restarting Everburn...")
	system("launcher") # need to eventually pass bots that were alive to be revived