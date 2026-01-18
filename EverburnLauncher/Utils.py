from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from EverburnLauncher.__main__ import Everburn



from subprocess import Popen, PIPE, STDOUT
from sys import exit
from os import system
from asyncio import Queue, to_thread, create_task, sleep

from EverburnLauncher.IPC import Announce, Read_Stdout_Loop, Send


async def Cleanup(Bots: dict[str, Popen | None]):
	print("Cleaning up...")
	Announce(Bots, "stop")
	while True:
		Safe = True
		for Bot in Bots.values():
			if Bot and Bot.poll() is None:
				Safe = False
				break
		if Safe:
			print("Finished cleaning up")
			return
		await sleep(0.1)


def Validate_Selection(Selection:str) -> None | str:
	if Selection.isdigit():
		BotSelection = int(Selection)
		return BotSelection - 1
	else:
		print("ERROR: Selection input was not a digit")
		return None


def Start_Bot(E:Everburn, Arguments:list[str]) -> None | str:
	Selection = Validate_Selection(Arguments[0])
	if Selection == None: return
	BotName = list(E.Bots.keys())[Selection]
	BotToken = E.Tokens[BotName]
	CallCommand = f".venv\\Scripts\\python.exe -B Bots\\{BotName}\\Bot\\Commence.py {BotToken} {BotName}"
	BotInstance = Popen(CallCommand,
						stdin=PIPE,
						stdout=PIPE,
						stderr=STDOUT,
						text=True)
	E.StdoutTasks[BotName] = create_task(Read_Stdout_Loop(E, BotName, BotInstance))
	E.Bots[BotName] = BotInstance
	print(f"Started {BotName}")
	Generate_Report(E)

	
def Stop_Bot(E:Everburn, Arguments:list[str]) -> None | str:
	Selection = Validate_Selection(Arguments[0])
	if Selection == None: return
	BotName = list(E.Bots.keys())[Selection]
	Send(E.Bots[BotName], "stop")


def Restart(Arguments:list[str]):
	if len(Arguments) == 0:
		print("Restarting Everburn...")
		system("launcher")
		exit()


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

	IndexBuffer = 6
	for Index, Name in enumerate(Names):
		BotSelectionNumber = Index+1
		Report += f"({BotSelectionNumber}) " + " " * (IndexBuffer - len(f"({BotSelectionNumber}) "))
		Report += Name + " " * (NamesLength - len(Name)) + " ~ " + Statuses[Index] + TokenStatuses[Index] + "\n"
	
	print(Report)