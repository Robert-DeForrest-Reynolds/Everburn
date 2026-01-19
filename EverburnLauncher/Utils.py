from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from EverburnLauncher.__main__ import Everburn



from subprocess import Popen, PIPE, STDOUT
from sys import exit
from asyncio import create_task, sleep

from EverburnLauncher.Logging import *
from EverburnLauncher.IPC import Announce, Read_Stdout_Loop, Send


async def Cleanup(E:Everburn):
	Log(INFO, "Cleaning up...")
	Announce(E.Bots, "stop")
	while True:
		Safe = True
		for Bot in E.Bots.values():
			if Bot and Bot.poll() is None:
				Safe = False
				break
		if Safe:
			Log(INFO, "Finished cleaning up")
			return
		await sleep(0.1)


def Validate_Selection(E:Everburn, Selection:str) -> None | str:
	if Selection.isdigit():
		BotSelection = int(Selection)
		return BotSelection - 1
	elif Selection == "*":
		for Index, Name in enumerate(E.Bots.keys()):
			if E.Bots[Name] == None and "Testing" not in Name:
				Start_Bot(E, [str(Index+1)])
	else:
		Log(ERROR, "Selection input was not a digit")
		return None


def Start_Bot(E:Everburn, Arguments:list[str]) -> None | str:
	Selection = Validate_Selection(E, Arguments[0])
	if Selection == None: return
	BotName:str = list(E.Bots.keys())[Selection]
	BotNameFormatted = BotName.replace(" ", "").replace("Testing", "")
	BotToken = E.Tokens[BotName]
	CallCommand = f".venv\\Scripts\\python.exe -B -m Bots.{BotNameFormatted} {BotToken} {BotNameFormatted}"
	BotInstance = Popen(CallCommand,
						stdin=PIPE,
						stdout=PIPE,
						stderr=STDOUT,
						text=True)
	E.StdoutTasks[BotName] = create_task(Read_Stdout_Loop(E, BotName, BotInstance))
	E.Bots[BotName] = BotInstance
	Log(INFO, f"Starting {BotName}...")

	
def Stop_Bot(E:Everburn, Arguments:list[str]) -> None | str:
	if not Arguments:
		Log(ERROR, "No arguments given to start command.")
		return
	Selection = Validate_Selection(E, Arguments[0])
	if Selection == None: return
	BotName = list(E.Bots.keys())[Selection]
	Send(E.Bots[BotName], "stop")
	Log(INFO, f"Stopping {BotName}...")


def Restart(E:Everburn, Arguments:list[str]):
	if len(Arguments) == 0:
		Announce(E.Bots, "stop")
		E.Restart = True
		E.Alive = False


def Generate_Report(E:Everburn) -> str:
	Report = ""
	Names = []
	Statuses = []
	TokenStatuses = []
	
	NamesLength = 0
	for Name, Process in E.Bots.items():
		NameLength = len(Name)
		if NameLength > NamesLength:
			NamesLength = NameLength

		Names.append(Name)
		Statuses.append("✅" if Process else "❌")
		TokenStatuses.append(" (TOKEN MISSING)" if E.Tokens[Name] == "MISSING" else "")

	IndexBuffer = 6 # Default amount of spaces appended before name of bot
	for Index, Name in enumerate(Names):
		BotSelectionNumber = Index+1
		Report += f"({BotSelectionNumber}) " + " " * (IndexBuffer - len(f"({BotSelectionNumber}) "))
		Report += Name + " " * (NamesLength - len(Name)) + " ~ " + Statuses[Index] + TokenStatuses[Index] + "\n"
	
	Log(INFO, "Report:\n" + Report + "\n-------")