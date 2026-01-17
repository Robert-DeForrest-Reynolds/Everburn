if __name__ != '__main__': exit()

from subprocess import Popen
from sys import exit
from asyncio import Queue, to_thread, run

print("Starting Everburn...")

Bots:dict[str:Popen|None] = {}
Tokens:dict[str:str] = {}
OutputQueue: Queue = Queue()

from EverburnLauncher.Utils import *


async def Read_Stdout_Loop(ProcessName:str, Process:Popen, OutputQueue:Queue):
	while True:
		Line = await to_thread(Process.stdout.readline)  # blocking read in thread
		if not Line:
			await OutputQueue.put(f"[{ProcessName}] <EOF>")
			return
		await OutputQueue.put(f"[{ProcessName}] {Line.rstrip()}")


async def Print_Loop(OutputQueue:Queue):
	while True:
		Line = await OutputQueue.get()
		if Line is None:
			return
		print(Line)


async def User_Input_Loop(Bots: dict[str, Popen]):
	while True:
		UserLine = await to_thread(input)  # reads console without blocking event loop
		UserLine = UserLine.rstrip("\n")
		print("Input command: ", UserLine)
		Arguments = UserLine.split(" ")
		Command = Arguments[0]
		if Command in Commands.keys():
			Commands[Command](Arguments[1:])
		else:
			print("Invalid command.")

		# Broadcast user input to all Bots (barebones)
		for Process in Bots.values():
			if Process != None:
				if Process.poll() is None:
					Process.stdin.write(UserLine + "\n")
					Process.stdin.flush()



Alive = True
Commands = {
	"start": lambda Arguments: Start_Bot(Bots, Tokens, Arguments),
	"stop": lambda Arguments: Stop_Bot(Bots, Tokens, Arguments),
	"report": lambda Arguments: Generate_Report(Bots, Tokens),
	"restart": lambda Arguments: Restart(Arguments),
	"send": lambda Arguments: Send(Bots, " ".join(Arguments)),
	"exit": exit,
}


with open("Tokens.txt") as TokensFile:
	for Line in TokensFile.readlines():
		Line = Line.strip()
		if Line == "": continue
		Split = Line.split(" = ")
		Tokens.update({Split[0]:Split[1]})
		Bots.update({Split[0]:None})


async def Main():
	await User_Input_Loop(Bots)

	await OutputQueue.put(None)

	for Process in Bots.values():
		if Process.poll() is None:
			Process.wait()

run(Main())