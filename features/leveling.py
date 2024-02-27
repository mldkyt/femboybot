import asyncio
import datetime

import discord
from discord.ext import commands as commands_ext

from database import conn as db
from utils.blocked import is_blocked
from utils.settings import get_setting, set_setting


def db_init():
    cur = db.cursor()
    cur.execute(
        "create table if not exists leveling (guild_id int, user_id int, xp int)")
    cur.close()
    db.commit()


def db_calculate_multiplier(guild_id: int):
    multiplier = get_setting(guild_id, 'leveling_xp_multiplier', '1')
    weekend_event = get_setting(
        guild_id, 'weekend_event_enabled', 'false')
    weekend_event_multiplier = get_setting(
        guild_id, 'weekend_event_multiplier', '2')
    if weekend_event == 'true':
        if datetime.datetime.now().weekday() in [5, 6]:
            multiplier = str(int(multiplier) *
                             int(weekend_event_multiplier))

    return multiplier


def db_get_user_xp(guild_id: int, user_id: int):
    db_init()
    cur = db.cursor()
    cur.execute(
        'SELECT xp FROM leveling WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))
    data = cur.fetchone()
    cur.close()
    return data[0] if data else 0


def db_add_user_xp(guild_id: int, user_id: int, xp: int):
    db_init()
    cur = db.cursor()
    cur.execute(
        "SELECT xp FROM leveling WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
    data = cur.fetchone()
    if data:
        current_xp = data[0]
        multiplier = db_calculate_multiplier(guild_id)
        cur.execute("UPDATE leveling SET xp = ? WHERE guild_id = ? AND user_id = ?",
                    (current_xp + (xp * int(multiplier)), guild_id, user_id))
    else:
        cur.execute(
            "INSERT INTO leveling (guild_id, user_id, xp) VALUES (?, ?, ?)", (guild_id, user_id, xp))
    cur.close()
    db.commit()


def get_xp_for_level(level: int):
    current = 0
    xp = 500
    iter = 0
    while current < level:
        if iter >= 10000000:
            raise OverflowError('Iteration limit reached.')
        xp *= 2
        current += 1
        iter += 1

    return xp


def get_level_for_xp(xp: int):
    current = 0
    level = 0
    iter = 0
    while current < xp:
        if iter >= 10000000:
            raise OverflowError('Iteration limit reached.')
        current += 500 * (2 ** level)
        level += 1
        iter += 1

    return level


async def update_roles_for_member(guild: discord.Guild, member: discord.Member):
    xp = db_get_user_xp(guild.id, member.id)
    level = get_level_for_xp(xp)

    for i in range(1, level + 1):  # Add missing roles
        role_id = get_setting(guild.id, f'leveling_reward_{i}', '0')
        if role_id != '0':
            role = guild.get_role(int(role_id))
            if role is not None and role not in member.roles:
                await member.add_roles(role)

    for i in range(level + 1, 100):  # Remove excess roles
        role_id = get_setting(guild.id, f'leveling_reward_{i}', '0')
        if role_id != '0':
            role = guild.get_role(int(role_id))
            if role is not None and role in member.roles:
                await member.remove_roles(role)


class Leveling(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        super().__init__()

    @discord.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        before_level = get_level_for_xp(
            db_get_user_xp(msg.guild.id, msg.author.id))
        db_add_user_xp(msg.guild.id, msg.author.id, len(msg.content))
        after_level = get_level_for_xp(
            db_get_user_xp(msg.guild.id, msg.author.id))
        await update_roles_for_member(msg.guild, msg.author)

        if before_level != after_level:
            msg2 = await msg.channel.send(
                f'Congratulations, {msg.author.mention}! You have reached level {after_level}!')
            await msg2.delete(delay=5)

    @discord.slash_command(name='level', description='Get the level of a user')
    @commands_ext.guild_only()
    @is_blocked()
    async def get_level(self, ctx: discord.Interaction, user: discord.User = None):
        user = user or ctx.user

        level = get_level_for_xp(db_get_user_xp(ctx.guild.id, user.id))

        await ctx.response.send_message(
            f'{user.mention} is level {level}.\nThe multiplier is currently `{str(db_calculate_multiplier(ctx.guild.id))}x`.',
            ephemeral=True)

    leveling_subcommand = discord.SlashCommandGroup(
        name='leveling', description='Leveling settings')

    @leveling_subcommand.command(name="list", description="List the leveling settings")
    @commands_ext.has_permissions(manage_guild=True)
    @commands_ext.guild_only()
    @is_blocked()
    async def list_settings(self, ctx: discord.Interaction):
        leveling_xp_multiplier = get_setting(
            ctx.guild.id, 'leveling_xp_multiplier', '1')
        weekend_event_enabled = get_setting(
            ctx.guild.id, 'weekend_event_enabled', 'false')
        weekend_event_multiplier = get_setting(
            ctx.guild.id, 'weekend_event_multiplier', '2')

        embed = discord.Embed(title='Leveling settings',
                              color=discord.Color.blurple())
        embed.add_field(name='Leveling multiplier',
                        value=f'`{leveling_xp_multiplier}x`')
        embed.add_field(name='Weekend event', value=weekend_event_enabled)
        embed.add_field(name='Weekend event multiplier',
                        value=f'`{weekend_event_multiplier}x`')

        await ctx.response.send_message(embed=embed, ephemeral=True)

    @leveling_subcommand.command(name='multiplier', description='Set the leveling multiplier')
    @commands_ext.has_permissions(manage_guild=True)
    @commands_ext.guild_only()
    @discord.option(name="multiplier", description="The multiplier to set", type=int)
    @is_blocked()
    async def set_multiplier(self, ctx: discord.Interaction, multiplier: int):
        set_setting(ctx.guild.id, 'leveling_xp_multiplier', str(multiplier))
        await ctx.response.send_message(f'Successfully set the leveling multiplier to {multiplier}.', ephemeral=True)

    @leveling_subcommand.command(name='weekend_event', description='Set the weekend event')
    @commands_ext.has_permissions(manage_guild=True)
    @commands_ext.guild_only()
    @discord.option(name="enabled", description="Whether the weekend event is enabled", type=bool)
    @is_blocked()
    async def set_weekend_event(self, ctx: discord.Interaction, enabled: bool):
        set_setting(ctx.guild.id, 'weekend_event_enabled',
                    str(enabled).lower())
        await ctx.response.send_message(f'Successfully set the weekend event to {enabled}.', ephemeral=True)

    @leveling_subcommand.command(name='weekend_event_multiplier', description='Set the weekend event multiplier')
    @commands_ext.has_permissions(manage_guild=True)
    @commands_ext.guild_only()
    @discord.option(name="weekend_event_multiplier", description="The multiplier to set", type=int)
    @is_blocked()
    async def set_weekend_event_multiplier(self, ctx: discord.Interaction, weekend_event_multiplier: int):
        set_setting(ctx.guild.id, 'weekend_event_multiplier',
                    str(weekend_event_multiplier))
        await ctx.response.send_message(f'Successfully set the weekend event multiplier to {weekend_event_multiplier}.',
                                        ephemeral=True)

    @leveling_subcommand.command(name='set_reward', description='Set a role for a level')
    @commands_ext.has_permissions(manage_guild=True)
    @commands_ext.guild_only()
    @discord.option(name="level", description="The level to set the reward for", type=int)
    @discord.option(name='role', description='The role to set', type=discord.Role)
    @is_blocked()
    async def set_reward(self, ctx: discord.Interaction, level: int, role: discord.Role):
        set_setting(ctx.guild.id, f'leveling_reward_{level}', str(role.id))
        await ctx.response.send_message(f'Successfully set the reward for level {level} to {role.mention}.',
                                        ephemeral=True)

    @leveling_subcommand.command(name='remove_reward', description='Remove a role for a level')
    @commands_ext.has_permissions(manage_guild=True)
    @commands_ext.guild_only()
    @discord.option(name="level", description="The level to remove the reward for", type=int)
    @is_blocked()
    async def remove_reward(self, ctx: discord.Interaction, level: int):
        set_setting(ctx.guild.id, f'leveling_reward_{level}', '0')
        await ctx.response.send_message(f'Successfully removed the reward for level {level}.', ephemeral=True)
