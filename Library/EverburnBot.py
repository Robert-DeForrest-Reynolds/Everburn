from logging import getLogger, Formatter, Logger
from logging.handlers import RotatingFileHandler


from discord import Intents, Guild
from discord import Interaction as DiscordInteraction
from discord import Member as DiscordMember
from discord.ext.commands import Bot as DiscordBot
from discord.ext.commands import Context as DiscordContext

from sys import argv, stdin
from sqlite3 import connect
from os.path import join, exists
from asyncio import get_running_loop, to_thread
from itertools import count

from Library.Panel import Panel
from EverburnLauncher.Logging import INFO, ERROR


class EverburnBot:
	def __init__(Self) -> None:
		Self.Token = argv[1]
		Self.Name = argv[2]
		if "Testing" in Self.Name:
			Self.Testing = True
		else:
			Self.Testing = False
		Self.Setup_Logger()
		Self.Send(Self.Name)
		Self.Alive = True # Controls async loops state
		Self.Setup = None
		Self.ViewContent:list = []
		Self.TheGreatHearth:Guild = None
		Self.EphemeralTimeout = 60 * 15
		Self.Requests = {}
		Self.RequestCounter = count(1)
		if exists(join("Data", "Desmond.db")):
			Self.DesmondDB = connect(join("Data", "Desmond.db"))

		I = Intents.all()
		I.message_content = True
		Self.Bot = DiscordBot(command_prefix='.', intents=I, help_command=None, description='description', case_insensitive=True)
	
		Self.Panel:Panel = Panel
		Self.PanelInstance:Panel = None
		Self.PanelCallback = None
		Self.Command = Self.Name.lower()

		Self.Testers = [
			
		]

		Self.Admins = [
			713798389908897822, # Zach (TheMadDM)
			897410636819083304, # Robert (Cavan)
		]

		Self.ProtectedGuildIDs = [
			1459985287055937793, # The Great Hearth
		]


		@Self.Bot.event
		async def on_ready() -> None:
			Self.TheGreatHearth = Self.Bot.get_guild(1459985287055937793)
			LogMessage = f"{Self.Bot.user} has connected to Discord!"
			Self.Logger.info(LogMessage)

			Self.Bot.loop.create_task(Self.Read_Stdin_Loop())
			if Self.Setup:
				await Self.Setup()

		Self.Send(f"Command Prefix: {Self.Name}")
		@Self.Bot.command(name=f"{Self.Name}_sync")
		async def sync(InitialContext:DiscordContext):
			if not await Self.Validate_Context(InitialContext): return
			await Self.Bot.tree.sync()
			await InitialContext.message.channel.send("Synced command tree")


		@Self.Bot.command(name=f"{Self.Name}_unsync")
		async def unsync(InitialContext:DiscordContext):
			if not await Self.Validate_Context(InitialContext): return
			Self.Bot.tree.clear_commands(guild=None)
			await Self.Bot.tree.sync()
			await InitialContext.message.channel.send("Unsynced command tree")


	async def Dev_Channel_Gate(Self, Interaction:DiscordInteraction):
		if Interaction.user.id in Self.Testers + Self.Admins:
			return True
		else:
			await Interaction.response.defer(ephemeral=True)
			await Interaction.delete_original_response()
			return False


	async def Validate_Context(Self, InitialContext:DiscordContext) -> None:
		if InitialContext.guild == None:
			await InitialContext.send("Please do not message The Great Heart's bots.\n" \
			"Continuous messages will result in a ban from using the bot, and could result in a ban from the server altogether.")
			return False
		if InitialContext.guild.id not in Self.ProtectedGuildIDs: return False
		if InitialContext.message.author.id not in Self.Admins: return False
		return True


	async def Validate_Interaction(Self, Interaction:DiscordInteraction) -> None:
		if Interaction.guild == None:
			await Interaction.response.send_message("Please do not message The Great Heart's bots.\n" \
			"Continuous messages will result in a ban from using the bot, and could result in a ban from the server altogether.")
			return False
		if Interaction.guild.id not in Self.ProtectedGuildIDs: return False
		if Interaction.user.id not in Self.Admins: return False
		return True


	async def Read_Stdin_Loop(Self):
		Loop = get_running_loop()
		Self.Send(f"Online, and listening...")
		while Self.Alive:
			Line = await to_thread(stdin.readline)
			if not Line:
				return

			Line = Line.strip()

			if Line == "stop":
				Self.Send(f"Everburn is closing {Self.Name}...")
				Self.Alive = False
				await Self.Bot.close()
				return
			else:
				RequestSplit = Line.split("~")
				RequestID = RequestSplit[0]
				Data = RequestSplit[1]
				Split = Data.split(",")
				Handler = Self.Requests[RequestID](Split)
				Self.Requests.pop(RequestID)


	def Get_Wallet(Self, Member:DiscordMember) -> float:
		Cursor = Self.DesmondDB.cursor()
		Cursor.execute("SELECT * FROM Players WHERE ID=?", (Member.id,))
		Row = Cursor.fetchone()
		Wallet = Row[2]
		return Wallet
	

	def Add_To_Wallet(Self, Member:DiscordMember, Amount:float) -> float:
		NewWallet = Self.Get_Wallet(Member) + Amount
		Cursor = Self.DesmondDB.cursor()
		Cursor.execute("UPDATE Players SET Wallet = ? WHERE ID=?", (NewWallet, Member.id))
		Self.DesmondDB.commit()
	

	def Subject_From_Wallet(Self, Member:DiscordMember, Amount:float) -> float:
		NewWallet = Self.Get_Wallet(Member) - Amount
		Cursor = Self.DesmondDB.cursor()
		Cursor.execute("UPDATE Players SET Wallet = ? WHERE ID=?", (NewWallet, Member.id))
		Self.DesmondDB.commit()
	

	def Apply_Wallet(Self, Member:DiscordMember, NewAmount:float) -> float:
		Cursor = Self.DesmondDB.cursor()
		Cursor.execute("UPDATE Players SET Wallet = ? WHERE ID=?", (NewAmount, Member.id))
		Self.DesmondDB.commit()
		
	
	def Transact(Self, Member:DiscordMember, FundsAfterPurchase:float) -> bool:
		Cursor = Self.DesmondDB.cursor()
		Cursor.execute("UPDATE Players SET Wallet = ? WHERE ID=?", (FundsAfterPurchase,Member.id))
		Self.DesmondDB.commit()
		

	def Get_Player_Data(Self, Member:DiscordMember):
		Self.Send(f"GET_PLAYER|{Member.id}")
		Cursor = Self.DesmondDB.cursor()
		Cursor.execute("SELECT * FROM Players WHERE ID=?", (Member.id,))
		Row = Cursor.fetchone()
		Data = {
			"ID":Row[0],
			"Name":Row[1],
			"Wallet":Row[2],
			"Fighter Count":Row[3],
			"Created At":Row[4],
		}
		return Data


	def Setup_Logger(Self):
		FileHandler = RotatingFileHandler(join('Logs', f'{Self.Name}.log'), 32 * 1024 * 1024, 5, encoding='utf-8',)
		DateTimeFormat = '%Y-%m-%d %H:%M:%S'
		MoglyFormatter = Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', DateTimeFormat, style='{')
		FileHandler.setFormatter(MoglyFormatter)

		DiscordLogger:Logger = getLogger('discord')
		DiscordLogger.setLevel(10) # 10 = DEBUG
		for Handler in list(DiscordLogger.handlers):
			DiscordLogger.removeHandler(Handler)
		DiscordLogger.addHandler(FileHandler)
		DiscordLogger.propagate = False

		for Child in DiscordLogger.getChildren():
			for Handler in list(Child.handlers):
				Child.removeHandler(Handler)
			Child.addHandler(FileHandler)
			Child.propagate = False

		Self.Logger = getLogger()
		Self.Logger.setLevel(20) # 20 = INFO
		Self.Logger.propagate = False
		Self.Logger.addHandler(FileHandler)

		Self.Send("Logger is setup")


	def Send(Self, Message:str, Type:str=INFO):
		"""Send IPC message to Everburn"""
		Self.Log(Message)
		print(f"{Type}:{Message}", flush=True)

	
	def Log(Self, Message:str, Level:int=None):
		"""Log to a file"""
		if Level:
			Self.Logger.log(Level, Message)
		else:
			Self.Logger.info(Message)