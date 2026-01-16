from subprocess import Popen
from sys import exit
from os import system


def Validate_Selection(Selection) -> None | str:
	if Selection.isdigit():
		BotSelection = int(Selection)
		return BotSelection - 1
	else:
		print("ERROR: Selection input was not a digit")
		return None


def Start_Bot(Bots:dict[str:Popen], Tokens:dict[str:str], Arguments:list[str]) -> None | str:
	Selection = Validate_Selection(Arguments[0])
	if Selection == None: return
	BotName = list(Bots.keys())[Selection]
	BotToken = Tokens[BotName]
	CallCommand = f".venv\\Scripts\\python.exe -B Bots\\{BotName}\\Bot\\Commence.py {BotToken} {BotName}"
	BotInstance = Popen(CallCommand)
	Bots[BotName] = BotInstance
	print(f"Started {BotName}")
	Generate_Report(Bots, Tokens)

	
def Stop_Bot(Bots:dict[str:Popen], Arguments:list[str]) -> None | str:
	Selection = Validate_Selection(Arguments[0])
	if Selection == None: return
	BotName = list(Bots.keys())[Selection]
	if Bots[BotName] != None:
		Bots[BotName].kill()
		Bots[BotName] = None
		print(f"Stopped {BotName}")


def Restart(Arguments:list[str]):
	if len(Arguments) == 0:
		print("Restarting Everburn...")
		system("launcher")
		exit()


def Generate_Report(Bots:dict[str:Popen], Tokens:dict[str:str]) -> str:
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