from subprocess import Popen
from asyncio import Queue

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
			"restart": lambda Arguments: Restart(Self, Arguments),
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