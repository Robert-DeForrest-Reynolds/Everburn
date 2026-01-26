from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from EverburnLauncher.__main__ import Everburn
 

from subprocess import Popen, PIPE, STDOUT
from asyncio import create_task, sleep

from EverburnLauncher.Logging import *
from EverburnLauncher.IPC import Announce, Read_Stdout_Loop, Send


async def Cleanup(E:Everburn):
	EverLog("Cleaning up...")
	Announce(E.Bots, "stop")
	while True:
		Safe = True
		Bot:Popen
		for Bot in E.Bots.values():
			if Bot and Bot.poll() is None:
				Safe = False
				break
		if Safe:
			EverLog("Finished cleaning up")
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
		EverLog("Selection input was not a digit", ERROR)
		return None


def Start_Bot(E:Everburn, Arguments:list[str]) -> None | str:
	Selection = Validate_Selection(E, Arguments[0])
	if Selection == None: return
	BotName:str = list(E.Bots.keys())[Selection]
	BotNameFormatted = BotName.replace(" ", "")
	BotToken = E.Tokens[BotName]
	if E.Platform == 'linux':
		CallCommand = [E.PyPath, '-B', '-m', f'Bots.{BotNameFormatted.replace("Testing", "")}', BotToken, BotNameFormatted.replace]
	else:
		CallCommand = f"{E.PyPath} -B -m Bots.{BotNameFormatted.replace("Testing", "")} {BotToken} {BotNameFormatted}"
	BotInstance = Popen(CallCommand,
						stdin=PIPE,
						stdout=PIPE,
						stderr=STDOUT,
						text=True)
	E.StdoutTasks[BotName] = create_task(Read_Stdout_Loop(E, BotName, BotInstance))
	E.Bots[BotName] = BotInstance
	EverLog(f"Starting {BotName}...")

	
def Stop_Bot(E:Everburn, Arguments:list[str]) -> None | str:
	if not Arguments:
		EverLog("No arguments given to start command.", ERROR)
		return
	Selection = Validate_Selection(E, Arguments[0])
	if Selection == None: return
	BotName = list(E.Bots.keys())[Selection]
	Send(BotName, E.Bots[BotName], "stop")
	EverLog(f"Stopping {BotName}...")


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
	
	EverLog("Report:\n" + Report + "\n-------")