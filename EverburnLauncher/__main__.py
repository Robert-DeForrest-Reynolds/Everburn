if __name__ != '__main__':
	from sys import exit
	exit(1)

from os import system
from subprocess import Popen
from asyncio import Queue, run, create_task

from EverburnLauncher.IPC import Execute_Queue, User_Input_Loop
from EverburnLauncher.Utils import *


class Everburn:
	def __init__(Self):
		Self.Log("Starting Everburn...")
		Self.Alive:bool = True
		Self.Restart:bool = False
		Self.Bots:dict[str:Popen|None] = {}
		Self.Tokens:dict[str:str] = {}
		Self.OutputQueue: Queue = Queue()
		Self.StdoutTasks: dict[str, object] = {}

		Self.Commands = {
			"start": lambda Arguments: Start_Bot(Self, Arguments),
			"stop": lambda Arguments: Stop_Bot(Self, Arguments),
			"report": lambda Arguments: Generate_Report(Self),
			"restart": lambda Arguments: Restart(E, Arguments),
			"exit": lambda Arguments: Self.Exit(),
		}

		with open("Tokens.txt") as TokensFile:
			for Line in TokensFile.readlines():
				Line = Line.strip()
				if Line == "": continue
				Split = Line.split(" = ")
				Self.Tokens.update({Split[0]:Split[1]})
				Self.Bots.update({Split[0]:None})


	def Exit(Self):
		Self.Alive = False


	def Log(Self, Message:str):
		print(f"Everburn:{Message}")


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

E.Log("Closing Everburn")

if E.Restart:
	E.Log("Restarting Everburn...")
	system("launcher") # need to eventually pass bots that were alive to be revived