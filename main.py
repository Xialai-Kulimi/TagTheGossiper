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

import os

import aiofiles
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


path = f"{os.path.dirname(__file__)}/config.json"


async def load_config() -> Config:
    try:
        async with aiofiles.open(path, "r") as f:
            config = Config.model_validate_json(await f.read())
    except Exception as e:
        console.log(f"[red] Error occur: {e} when load_config")
        config = Config()

    return config


async def save_config(config: Config):
    async with aiofiles.open(path, "w") as f:
        await f.write(config.model_dump_json(indent=4))


# defining and sending the button
button = Button(
    custom_id="kulimi_TagTheGossiper_give_gossiper_role",
    style=ButtonStyle.GREEN,
    label="點擊獲得吃瓜觀光團身份組",
)


async def get_all_gossiper_roles(guild: interactions.Guild) -> list[interactions.Role]:
    config = await load_config()
    return [role for role in guild.roles if config.gossiper_base in role.name]


async def create_new_gossiper_role(guild: interactions.Guild) -> interactions.Role:
    config = await load_config()

    role = None
    for role in await get_all_gossiper_roles(guild):
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
            mentionable=True,
            icon=None,
            reason="吃瓜觀光團模組：建立新的吃瓜觀光團身份組",
        )

    return new_role


async def add_gossiper_role(
    guild: interactions.Guild, member: interactions.Member
) -> interactions.Role:
    for role in await get_all_gossiper_roles(guild):
        if len(role.members) < MAX_MEMBER_PER_ROLE:
            await member.add_role(role, reason="吃瓜觀光團模組：添加吃瓜觀光團身份組")
            return role

    # no valid role exist, create new role
    role = await create_new_gossiper_role(guild)
    await member.add_role(role)
    return role


async def fix_gossiper_role(guild: interactions.Guild) -> list[interactions.Member]:

    add_gossiper_role_list = []
    for role in await get_all_gossiper_roles(guild):
        if len(role.members) > MAX_MEMBER_PER_ROLE:
            current_gossiper_role_list = role.members[MAX_MEMBER_PER_ROLE:]
            add_gossiper_role_list += current_gossiper_role_list
            for member in current_gossiper_role_list:
                await member.remove_role(
                    role,
                    reason=f"吃瓜觀光團模組：此身份組（{role.name}）超過最大人數（{MAX_MEMBER_PER_ROLE}）",
                )

    for member in add_gossiper_role_list:
        await add_gossiper_role(guild, member)
    return add_gossiper_role_list


class Gossiper(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="tag_the_gossiper",
        description="吃瓜觀光團相關指令",
        checks=[check_is_admin],
    )

    @module_base.subcommand("help", sub_cmd_description="顯示關於吃瓜觀光團的介紹")
    async def help(self, ctx: interactions.SlashContext):
        config = await load_config()
        await ctx.respond(
            embed=interactions.Embed(
                title="吃瓜觀光團模組",
                description=f"""
吃瓜觀光團模組主要是為了解決吃瓜觀光團管理、新建、提及等等方面的不方便。

## 介紹
0. 只有法官可以使用本模組的指令。
1. 吃瓜觀光團身份組的判斷條件為身份組名稱包含共用基底，共用基底可以透過 `config` 指令設定，預設為「吃瓜观光团」，目前為「{config.gossiper_base}」
2. 每個吃瓜觀光團身份組最多應該只有{MAX_MEMBER_PER_ROLE}人。
3. 按下按鈕後，如果有低於一百人的吃瓜觀光團身份組，則直接將其加入該身份組
4. 如果沒有可用的身份組，將會用現有的吃瓜觀光團身份組建立新的吃瓜觀光團身份組。

## 指令
- `config`：設定吃瓜觀光團的設定，目前僅可設定吃瓜觀光團的共用基底。
- `send_role_giver`：在當前頻道傳送一個可以添加吃瓜觀光團身份組的按鈕。
- `tag`：提及所有的吃瓜觀光團身份組。
- `manual_fix`：為本群組的吃瓜觀光團身份組超出一百人的部分重新分配吃瓜觀光團身份組。

""",
                color=0xFF5252,
            )
        )

    @module_base.subcommand("config", sub_cmd_description="設定吃瓜觀光團的相關設定")
    async def config(self, ctx: interactions.SlashContext):

        config = await load_config()
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
        await save_config(config)
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
        "manual_fix", sub_cmd_description="手動修復所有成員的吃瓜觀光團身份組狀態"
    )
    async def manual_fix(self, ctx: interactions.SlashContext):
        effect_list = await fix_gossiper_role(ctx.guild)
        await ctx.respond(
            f"修復了{len(effect_list)}位成員的吃瓜觀光團身份組狀態。", ephemeral=True
        )

    @module_base.subcommand("tag", sub_cmd_description="提及所有吃瓜觀光團身份組")
    async def tag(self, ctx: interactions.SlashContext):

        await ctx.respond(
            f"{' '.join([r.mention for r in await get_all_gossiper_roles(ctx.guild)])}",
            allowed_mentions=interactions.AllowedMentions.all(),
        )

    @interactions.component_callback("kulimi_TagTheGossiper_give_gossiper_role")
    async def handle_give_gossiper_role(self, ctx: interactions.ComponentContext):
        config = await load_config()

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
