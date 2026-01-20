from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from EverburnLauncher.__main__ import Everburn


from subprocess import Popen
from asyncio import to_thread
from EverburnLauncher.Logging import *


def Announce(Bots:dict[str:Popen], Line: str):
	Bot:Popen
	for Bot in Bots.values():
		if Bot and Bot.poll() is None:
			Bot.stdin.write(Line + "\n")
			Bot.stdin.flush()


def Send(Bot:Popen, Line: str):
	Bot.stdin.write(Line + "\n")
	Bot.stdin.flush()


async def Execute_Queue(E:Everburn):
	while True:
		Line:str = await E.OutputQueue.get()
		if Line is None:
			return
		Split = Line.split(":")
		BotName = Split[0]
		Message = Split[1]
		if Message == "Process End": E.Bots[BotName] = None
		if Message == "stopped": E.Bots[BotName] = None
		print(Line)


async def Read_Stdout_Loop(E:Everburn, ProcessName:str, Process:Popen):
	while E.Alive:
		Line = await to_thread(Process.stdout.readline)  # blocking read in thread
		if not Line:
			await E.OutputQueue.put(f"{ProcessName}:Process End")
			return
		await E.OutputQueue.put(f"{ProcessName}:{Line.rstrip()}")


async def User_Input_Loop(E:Everburn):
	while E.Alive:
		UserLine = await to_thread(input)  # reads console without blocking event loop
		UserLine = UserLine.rstrip("\n")
		Arguments = UserLine.split(" ")
		Command = Arguments[0]
		if Command in E.Commands.keys():
			E.Commands[Command](Arguments[1:])
		else:
			EverLog("Invalid command.", ERROR)