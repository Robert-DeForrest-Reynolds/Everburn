from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Library.EverburnBot import EverburnBot
    
from discord import Interaction as DiscordInteraction
from discord import Member as DiscordMember
from discord.ui import Button as DiscordButton
from discord.ext.commands import Context as DiscordContext
from discord import Embed
from discord.ui import View
from asyncio import create_task

from sys import getrefcount


class Panel:
    def __init__(Self, InitialContext:DiscordContext, Bot:EverburnBot) -> None:
        Self.Bot = Bot
        Self.Bot.PanelInstance = Self
        Self.User:DiscordMember = InitialContext.author
        Self.View = None
        Self.Title = f"Hi {Self.User.name}!"
        Self.Task = create_task(Self.Send_Panel(InitialContext))


    def __del__(Self):
        Self.Bot.Log(f"{Self.User.name}'s Panel Cleaned up")


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


    async def Add_Field(Self, Name:str, Value:str, Inline=False):
        Self.Embed.add_field(name=Name, value=Value, inline=Inline)


    async def Reply_Panel(Self, Interaction:DiscordInteraction):
        # Self.Bot.Log(f"References: {getrefcount(Self)}")

        LogMessage = f"{Self.User.name} called for a dashboard"
        Self.Bot.Log(LogMessage)

        Self.View = View(timeout=144000)
        Self.Embed = Embed(title=Self.Title)


        for Content in Self.Bot.ViewContent:
            Self.View.add_item(Content)

        await Interaction.response.edit_message(view=Self.View, embed=Self.Embed)


    async def Send_Panel(Self, InitialContext:DiscordContext):
        Self.Bot.Log(f"References: {getrefcount(Self)}")

        LogMessage = f"{Self.User.name} called for a dashboard"
        Self.Bot.Log(LogMessage)

        Self.View = View(timeout=144000)
        Self.Embed = Embed(title=Self.Title)


        for Content in Self.Bot.ViewContent:
            Self.View.add_item(Content)


        await InitialContext.message.delete()

        await InitialContext.channel.send(view=Self.View, embed=Self.Embed)

