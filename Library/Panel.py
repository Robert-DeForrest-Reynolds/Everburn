from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Library.EverburnBot import EverburnBot as EB
	
from discord import Interaction as DiscordInteraction
from discord import Member as DiscordMember
from discord.ui import View
from asyncio import Task


class Panel:
	def __init__(Self, User:DiscordMember, EverburnBot:EB) -> None:
		Self.User = User
		Self.EverburnBot:EB = EverburnBot
		Self.ViewTimeout = 60*5
		Self.View = View(timeout=Self.ViewTimeout)
		Self.View.on_timeout = Self.Cleanup_Panel
		Self.Embed = None
		Self.Task:Task
		Self.OriginInteraction:DiscordInteraction


	def __del__(Self):
		Self.EverburnBot.Send(f"{Self.User.name}'s called __del__ on panel")


	async def Referesh_Panel(Self):
		for Item in Self.View.children:
			Item.callback = None
		Self.View.clear_items()
		Self.EverburnBot.Send("Finished Refreshing panel")


	async def Cleanup_Panel(Self):
		for Item in Self.View.children:
			Item.callback = None
		Self.View.clear_items()
		Self.View.stop()
		Self.View.on_timeout = None
		if Self.Task and not Self.Task.done():
			Self.Task.cancel()
		Self.Task = None
		OriginalMessage = await Self.OriginInteraction.original_response()
		await OriginalMessage.delete()
		Self.EverburnBot.Send(f"Cleaned up {Self.User.name}'s panel")

