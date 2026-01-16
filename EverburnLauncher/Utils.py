from subprocess import Popen, CompletedProcess
from sys import exit
from os import system

def Start_Bot(Bots:dict[str:CompletedProcess], Tokens:dict[str:str], Arguments:list[str]) -> None | str:
	if Arguments[0].isdigit():
		BotSelection = int(Arguments[0])
		print(BotSelection)
	else:
		return "ERROR: Selection input was not a digit"
	
	BotName = list(Bots.keys())[BotSelection-1]
	BotToken = Tokens[BotName]
	CallCommand = f".venv\\Scripts\\python.exe -B {BotName}\\Bot\\Commence.py {BotToken} {BotName}"
	BotInstance = Popen(CallCommand)


def Restart(Arguments:list[str]):
	if len(Arguments) == 0:
		print("Restarting Everburn...")
		system("launcher")
		exit()


def Generate_Report(Bots:dict[str:CompletedProcess], Tokens:dict[str:str]) -> str:
	Report = ""
	Names = []
	Statuses = []
	TokenStatuses = []
	
	NamesLength = 0
	for Name, Process in Bots.items():
		NameLength = len(Name)
		if NameLength > NamesLength:
			NamesLength = NameLength

		Names.append(Name)
		Statuses.append("✅" if Process else "❌")
		TokenStatuses.append(" (TOKEN MISSING)" if Tokens[Name] == "MISSING" else "")

	IndexBuffer = 6
	for Index, Name in enumerate(Names):
		BotSelectionNumber = Index+1
		Report += f"({BotSelectionNumber}) " + " " * (IndexBuffer - len(f"({BotSelectionNumber}) "))
		Report += Name + " " * (NamesLength - len(Name)) + " ~ " + Statuses[Index] + TokenStatuses[Index] + "\n"
	
	print(Report)