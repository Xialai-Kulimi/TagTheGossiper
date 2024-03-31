"""
Discord-Bot-Module template. For detailed usages,
 check https://interactions-py.github.io/interactions.py/

Copyright (C) 2024  __retr0.init__

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import interactions
from interactions import Button, ButtonStyle, listen
from interactions.api.events import Component


# Use the following method to import the internal module in the current same directory
from . import internal_t

# Import the os module to get the parent path to the local files
import os

# aiofiles module is recommended for file operation
import aiofiles

# You can listen to the interactions.py event
from interactions.api.events import MessageCreate, InteractionCreate

# You can create a background task
from interactions import Task, IntervalTrigger

from rich.console import Console

console = Console()

"""
Replace the ModuleName with any name you'd like
"""


# defining and sending the button
button = Button(
    custom_id="kulimi_TagTheGossiper_give_gossiper_role",
    style=ButtonStyle.GREEN,
    label="點擊獲得吃瓜觀光團身份組",
)


class ModuleName(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="tag_the_gossiper",
        description="吃瓜觀光團相關指令",
    )
    # module_group: interactions.SlashCommand = module_base.group(
    #     name="replace_your_command_group_here",
    #     description="Replace here for the group command descriptions",
    # )

    # @module_group.subcommand(
    #     "ping", sub_cmd_description="Replace the description of this command"
    # )
    # @interactions.slash_option(
    #     name="option_name",
    #     description="Option description",
    #     required=True,
    #     opt_type=interactions.OptionType.STRING,
    # )
    # async def module_group_ping(self, ctx: interactions.SlashContext, option_name: str):
    #     await ctx.send(f"Pong {option_name}!")
    #     internal_t.internal_t_testfunc()

    @module_base.subcommand(
        "send_role_giver", sub_cmd_description="傳送獲得吃瓜觀光團的獲得按鈕到此頻道"
    )
    # @interactions.slash_option(
    #     name="option_name",
    #     description="Option description",
    #     required=True,
    #     opt_type=interactions.OptionType.STRING,
    # )
    async def module_group_pong(self, ctx: interactions.SlashContext):
        # The local file path is inside the directory of the module's main script file
        # async with aiofiles.open(
        #     f"{os.path.dirname(__file__)}/example_file.txt"
        # ) as afp:
        #     file_content: str = await afp.read()
        # await ctx.send(f"Pong {option_name}!\nFile content: {file_content}")
        # internal_t.internal_t_testfunc()
        await ctx.channel.send(
            embed=interactions.Embed(title="點擊下方按鈕獲得吃瓜觀光團身份組"),
            components=[button],
        )

    # @interactions.listen(InteractionCreate)
    # async def on_interactioncreate(self, event: InteractionCreate):
    #     """
    #     Event listener when a new interaction is created
    #     """
    #     console.log(event.interaction)
    #     console.log(event)

    # @interactions.listen(MessageCreate)
    # async def on_messagecreate(self, event: MessageCreate):
    #     """
    #     Event listener when a new message is created
    #     """
    #     console.log(
    #         f"User {event.message.author.display_name} sent '{event.message.content}'"
    #     )
    @interactions.component_callback("kulimi_TagTheGossiper_give_gossiper_role")
    async def my_callback(ctx: interactions.ComponentContext):
            await ctx.send("You clicked it!")


    # You can even create a background task to run as you wish.
    # Refer to https://interactions-py.github.io/interactions.py/Guides/40%20Tasks/ for guides
    # Refer to https://interactions-py.github.io/interactions.py/API%20Reference/API%20Reference/models/Internal/tasks/ for detailed APIs
    # @Task.create(IntervalTrigger(minutes=1))
    # async def task_everyminute(self):
    #     channel: interactions.TYPE_MESSAGEABLE_CHANNEL = self.bot.get_guild(
    #         1234567890
    #     ).get_channel(1234567890)
    #     await channel.send("Background task send every one minute")
    #     print("Background Task send every one minute")

    # # The command to start the task
    # @module_base.subcommand(
    #     "start_task", sub_cmd_description="Start the background task"
    # )
    # async def module_base_starttask(self, ctx: interactions.SlashContext):
    #     self.task_everyminute.start()
    #     await ctx.send("Task started")
