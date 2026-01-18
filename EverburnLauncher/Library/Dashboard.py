from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from EverburnLauncher.Library.EverburnBot import EverburnBot
    
from discord import Interaction as DiscordInteraction
from discord import Member as DiscordMember
from discord.ui import Button as DiscordButton
from discord import Embed
from discord.ui import View
from asyncio import create_task

from sys import getrefcount


class Dashboard:
    def __init__(Self, User:DiscordMember, Interaction:DiscordInteraction, Bot:EverburnBot) -> None:
        Self.Bot = Bot
        Self.User = User
        Self.View = None
        Self.Task = create_task(Self.Send_Panel(Interaction))


    def __del__(Self):
        Self.Bot.Log(f"{Self.User.name}'s Dashboard Cleaned up")


    async def Referesh_Panel(Self):
        for Item in Self.View.children:
            Item.callback = None
        Self.View.clear_items()


    async def New_Panel(Self, Interaction:DiscordInteraction):
        await Self.Referesh_Panel()
        await Self.Send_Panel(Interaction)


    async def Cleanup_Panel(Self, Interaction:DiscordInteraction):
        await Self.Referesh_Panel()
        await Interaction.response.send_message("Bye bye")
        Self.View.stop()
        Self.Task.cancel()
        Self.Task = None


    async def Send_Panel(Self, Interaction:DiscordInteraction):
        Self.Bot.Log(f"References: {getrefcount(Self)}")

        LogMessage = f"{Self.User.name} called for a dashboard"
        Self.Bot.Log(LogMessage)

        Self.View = View(timeout=144000)
        Self.Embed = Embed(title=f"Hi {Self.User.name}!")

        await Interaction.message.delete()

        await Interaction.channel.send(view=Self.View, embed=Self.Embed)

