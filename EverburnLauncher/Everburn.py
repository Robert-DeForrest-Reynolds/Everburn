from subprocess import Popen
from asyncio import Queue
from sys import platform
from os.path import join

from EverburnLauncher.Utils import *
from EverburnLauncher.Logging import *


class Everburn:
	def __init__(Self):
		EverLog("Starting Everburn...")
		Self.Alive:bool = True
		Self.Restart:bool = False
		Self.Bots:dict[str:Popen|None] = {}
		Self.Tokens:dict[str:str] = {}
		Self.OutputQueue: Queue = Queue()
		Self.StdoutTasks: dict[str, object] = {}
		Self.Platform = platform
		if Self.Platform == "linux":
			Self.PyPath = join(".venv", "bin", "python3")
		else:
			Self.PyPath = join(".venv", "Scripts", "python")

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