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
from interactions import (
    Button,
    ButtonStyle,
    ModalContext,
    Modal,
    ShortText,
)
from interactions.api.events import Component

# Use the following method to import the internal module in the current same directory
from . import internal_t
from pydantic import BaseModel

# You can listen to the interactions.py event
from interactions.api.events import MessageCreate, InteractionCreate

# You can create a background task

from rich.console import Console
import json

console = Console()


class Config(BaseModel):
    gossiper_base: str = "吃瓜观光团"


def load_config() -> Config:
    with open("config.json", "rw") as f:
        try:
            config = Config.model_validate_json(f.read())
        except Exception as e:
            console.log(f"[red] Error occur: {e} when load_config")
            config = Config()

    return config


def save_config(config: Config):
    with open("config.json", "w") as f:
        f.write(config.model_dump_json(indent=4))


# defining and sending the button
button = Button(
    custom_id="kulimi_TagTheGossiper_give_gossiper_role",
    style=ButtonStyle.GREEN,
    label="點擊獲得吃瓜觀光團身份組",
)


@interactions.component_callback("kulimi_TagTheGossiper_give_gossiper_role")
async def my_callback(ctx: interactions.ComponentContext):
    await ctx.send("You clicked it!")


class Gossiper(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="tag_the_gossiper", description="吃瓜觀光團相關指令"
    )

    @module_base.subcommand("config", sub_cmd_description="設定吃瓜觀光團的相關設定")
    async def config(self, ctx: interactions.SlashContext):

        config = load_config()
        my_modal = Modal(
            ShortText(
                label="設定共用基底，會將所有包含共同基底的身份組視為吃瓜觀光團身份組",
                custom_id="new_base",
                placeholder=f"目前為「{config.gossiper_base}」",
            ),
            title="吃瓜觀光團設定",
        )
        await ctx.send_modal(modal=my_modal)

        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)

        new_base = modal_ctx.responses["new_base"]

        config.gossiper_base = new_base
        save_config(config)
        await ctx.send(f"{config}", ephemeral=True)

    @module_base.subcommand(
        "send_role_giver", sub_cmd_description="傳送獲得吃瓜觀光團的獲得按鈕到此頻道"
    )
    
    async def send_role_giver(self, ctx: interactions.SlashContext):
    
        await ctx.respond(
            embed=interactions.Embed(title="點擊下方按鈕獲得吃瓜觀光團身份組"),
            components=[button],
        )

    