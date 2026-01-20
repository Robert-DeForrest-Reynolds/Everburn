from subprocess import Popen
from asyncio import Queue

from sqlite3 import connect

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

		
		Self.DesmondDB = connect("Desmond.db")
		Self.DesmondCursor = Self.DesmondDB.cursor()
		Self.DesmondCursor.execute("""
		CREATE TABLE IF NOT EXISTS Players (
			ID   		INTEGER PRIMARY KEY,
			Name        TEXT NOT NULL,
			CreatedAt   TEXT NOT NULL DEFAULT (datetime('now'))
		);
		""")
		Self.DesmondDB.commit()


		Self.MainEventDB = connect("MainEvent.db")

		Self.MainEventCursor = Self.MainEventDB.cursor()
		Self.MainEventCursor.execute("""
		CREATE TABLE IF NOT EXISTS Fighters (
			FighterId   INTEGER PRIMARY KEY AUTOINCREMENT,
			OwnerId     TEXT NOT NULL,
			Name        TEXT NOT NULL,
			Level       INTEGER NOT NULL DEFAULT 1,
			CreatedAt   TEXT NOT NULL DEFAULT (datetime('now'))
		);
		""")
		Self.MainEventDB.commit()


	def Exit(Self):
		Self.Alive = False