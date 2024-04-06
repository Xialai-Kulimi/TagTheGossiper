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
    check,
    has_role,
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

MAX_MEMBER_PER_ROLE = 100

avaliable_suffix = [""] + [str(i + 2) for i in range(500)]

JUDGE_ROLE_ID = 1210108577008853012


async def check_is_admin(ctx: interactions.SlashContext):

    return ctx.author.has_role(JUDGE_ROLE_ID) or ctx.author.id in ctx.bot.owner_ids


class Config(BaseModel):
    gossiper_base: str = "吃瓜观光团"


def load_config() -> Config:
    try:
        with open("config.json", "r") as f:
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


def get_all_gossiper_roles(guild: interactions.Guild) -> list[interactions.Role]:
    config = load_config()
    return [role for role in guild.roles if config.gossiper_base in role.name]


async def create_new_gossiper_role(guild: interactions.Guild) -> interactions.Role:
    config = load_config()

    role = None
    for role in get_all_gossiper_roles(guild):
        if role.name.endswith(avaliable_suffix[0]):
            avaliable_suffix.pop(0)

    if role:
        new_role = await guild.create_role(
            name=config.gossiper_base + avaliable_suffix[0],
            color=role.color,
            permissions=role.permissions,
            hoist=role.hoist,
            mentionable=role.mentionable,
            icon=role.icon,
            reason="吃瓜觀光團模組：利用原有的吃瓜觀光團身份組建立新的身份組",
        )
        await new_role.move(
            role.position, reason="吃瓜觀光團模組：將新的吃瓜觀光團身份組移到該有的位置"
        )

    if not role:
        new_role = await guild.create_role(
            name=config.gossiper_base + avaliable_suffix[0],
            permissions=0,
            hoist=False,
            mentionable=False,
            icon=None,
            reason="吃瓜觀光團模組：建立新的吃瓜觀光團身份組",
        )

    return new_role


async def add_gossiper_role(
    guild: interactions.Guild, member: interactions.Member
) -> interactions.Role:
    for role in get_all_gossiper_roles(guild):
        if len(role.members) < MAX_MEMBER_PER_ROLE:
            await member.add_role(role)
            return role

    # no valid role exist, create new role
    role = await create_new_gossiper_role(guild)
    await member.add_role(role)
    return role


async def fix_gossiper_role(guild: interactions.Guild):

    add_gossiper_role_list = []
    for role in get_all_gossiper_roles(guild):
        if len(role.members) > MAX_MEMBER_PER_ROLE:
            current_gossiper_role_list = role.members[MAX_MEMBER_PER_ROLE:]
            add_gossiper_role_list += current_gossiper_role_list
            for member in current_gossiper_role_list:
                await member.remove_role(role)

    for member in add_gossiper_role_list:
        await add_gossiper_role(guild, member)


class Gossiper(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="tag_the_gossiper",
        description="吃瓜觀光團相關指令",
        checks=[check_is_admin],
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
        await modal_ctx.defer(edit_origin=True, ephemeral=True)

        config.gossiper_base = new_base
        save_config(config)
        await ctx.respond(f"已設定，新的設定如下\n```py\n{config}\n```", ephemeral=True)

    @module_base.subcommand(
        "send_role_giver", sub_cmd_description="傳送獲得吃瓜觀光團的獲得按鈕到此頻道"
    )
    async def send_role_giver(self, ctx: interactions.SlashContext):

        await ctx.channel.send(
            embed=interactions.Embed(title="點擊下方按鈕獲得吃瓜觀光團身份組"),
            components=[button],
        )
        await ctx.respond("已傳送獲得吃瓜觀光團按鈕到此頻道", ephemeral=True)

    @module_base.subcommand(
        "tag", sub_cmd_description="提及所有吃瓜觀光團身份組"
    )
    async def tag(self, ctx: interactions.SlashContext):

        await ctx.respond(
            f"{' '.join([r.mention for r in get_all_gossiper_roles(ctx.guild)])}"
        )

    @interactions.component_callback("kulimi_TagTheGossiper_give_gossiper_role")
    async def handle_give_gossiper_role(self, ctx: interactions.ComponentContext):
        config = load_config()

        # check if author need add role
        for role in ctx.author.roles:
            if config.gossiper_base in role.name:
                await ctx.respond(
                    f"你已經有一個吃瓜觀光團身份組了（{role.mention}）", ephemeral=True
                )
                return

        role = await add_gossiper_role(ctx.guild, ctx.author)
        if role:
            await ctx.respond(
                f"成功添加吃瓜觀光團身份組「{role.mention}」", ephemeral=True
            )
        else:
            await ctx.respond("添加失敗，請向管理員聯絡", ephemeral=True)
        # clean current gossiper roles
        await fix_gossiper_role(ctx.guild)
