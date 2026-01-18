from logging import getLogger, Formatter,  DEBUG, INFO, Logger, basicConfig
from logging.handlers import RotatingFileHandler
from discord import Intents
from discord.ext.commands import Bot as DiscordBot
from sys import argv
from discord.ext.commands import Context as DiscordContext
from discord import Game as DiscordGame
from sys import stdin
from asyncio import get_running_loop, to_thread


class EverburnBot:
	def __init__(Self) -> None:
		Self.Token = argv[1]
		Self.Name = argv[2]
		Self.Alive = True # Controls async loops state

		I = Intents.all()
		I.message_content = True
		Self.Bot = DiscordBot(command_prefix='.', intents=I, help_command=None, description='description', case_insensitive=True)
	
		Self.Dashboard = None
		Self.Command = "EverburnBot"

		Self.Admins = [
		]

		Self.ProtectedGuildIDs = [
			1459985287055937793, # The Great Hearth
		]

		Self.Setup_Logger()


		@Self.Bot.event
		async def on_ready() -> None:
			LogMessage = f"{Self.Bot.user} has connected to Discord!"
			Self.Logger.info(LogMessage)

			await Self.Bot.change_presence(activity=DiscordGame(f'.{Self.Command}'))
			Self.Bot.loop.create_task(Self.Read_Stdin_Loop())


		@Self.Bot.command(name="sync")
		async def sync(Context:DiscordContext):
			if Context.message.author.id not in Self.Admins: return
			await Self.Bot.tree.sync()


		if Self.Dashboard:
			@Self.Bot.command(aliases=[f"{Self.Name.lower()}"])
			async def Send_Dashboard(InitialContext:DiscordContext) -> None:
				if InitialContext.guild.id not in Self.ProtectedGuildIDs: return
				User = InitialContext.message.author
				Self.Dashboard(User, InitialContext, Self)
				Self.Logger.info(f"{User.name}'s Dashboard sequence finished.")


	def Output(Self, Message:str): print(Message, flush=True)


	async def Read_Stdin_Loop(Self):
		Loop = get_running_loop()
		Self.Output(f"Online, and listening...")
		while Self.Alive:
			Line = await to_thread(stdin.readline)
			if not Line:
				return

			Command = Line.strip()

			if Command == "stop":
				Self.Log(f"Everburn is closing {Self.Name}...")
				Self.Alive = False
				await Self.Bot.close()
				return


	def Setup_Logger(Self):
		FileHandler = RotatingFileHandler(f'Logs\\{Self.Name}.log', 32 * 1024 * 1024, 5, encoding='utf-8',)
		DateTimeFormat = '%Y-%m-%d %H:%M:%S'
		MoglyFormatter = Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', DateTimeFormat, style='{')
		FileHandler.setFormatter(MoglyFormatter)

		Self.Logger = getLogger()
		Self.Logger.setLevel(INFO)
		for handler in list(Self.Logger.handlers):
			Self.Logger.removeHandler(handler)
		Self.Logger.propagate = False
		Self.Logger.addHandler(FileHandler)

		DiscordLogger:Logger = getLogger('discord')
		DiscordLogger.setLevel(DEBUG)
		for Handler in list(DiscordLogger.handlers):
			DiscordLogger.removeHandler(Handler)
		DiscordLogger.addHandler(FileHandler)
		DiscordLogger.propagate = False

		for Child in DiscordLogger.getChildren():
			for Handler in list(Child.handlers):
				Child.removeHandler(Handler)
			Child.addHandler(FileHandler)
			Child.propagate = False

		Self.Log("Logger is setup")

	
	def Log(Self, Message:str, Level:int=None):
		if Level:
			Self.Logger.log(Level, Message)
		else:
			Self.Logger.info(Message)