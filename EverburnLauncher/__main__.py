if __name__ != '__main__': exit()

from subprocess import run, CompletedProcess
from sys import exit

print("Starting Everburn...")

Bots:dict[str:CompletedProcess|None] = {}
Tokens:dict[str:str] = {}

from EverburnLauncher.Utils import *

Alive = True
Commands = {
	"start": lambda Arguments: Start_Bot(Bots, Tokens, Arguments),
	"report": lambda Arguments: Generate_Report(Bots, Tokens),
	"restart": lambda Arguments: Restart(Arguments),
	"exit": exit,
}


with open("Tokens.txt") as TokensFile:
	for Line in TokensFile.readlines():
		Line = Line.strip()
		if Line == "": continue
		Split = Line.split(" = ")
		Tokens.update({Split[0]:Split[1]})
		Bots.update({Split[0]:None})


while Alive:
	AdminInput = input()
	print("Input command: ", AdminInput)
	try:
		Arguments = AdminInput.split(" ")
		Command = Arguments[0]
		Commands[Command](Arguments[1:])
	except KeyError:
		print("Invalid command.")