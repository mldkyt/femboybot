
import os
import discord
from utils.blocked import db_add_blocked_server, db_add_blocked_user, db_remove_blocked_server, db_remove_blocked_user

ADMIN_GUILD = os.getenv("ADMIN_GUILD") or 0
OWNER_ID = os.getenv("OWNER_ID") or 0

print(f'ADMIN_GUILD {ADMIN_GUILD}')
print(f'OWNER_ID    {OWNER_ID}')


class AdminCommands(discord.Cog):

    def __init__(self, bot: discord.Bot):
        super().__init__()
        self.bot = bot

    admin_subcommand = discord.SlashCommandGroup(
        name="admin", description="Manage the bot", guild_ids=[ADMIN_GUILD])

    blocklist_subcommand = discord.SlashCommandGroup(
        name="blocklist", description="Manage the blocklist", parent=admin_subcommand)

    @blocklist_subcommand.command(name="add_user", description="Add a user to the blocklist")
    async def blocklist_add_user(self, ctx: discord.Interaction, user: discord.User, reason: str):
        if ctx.user.id != int(OWNER_ID):
            await ctx.response.send_message("You do not have permission", ephemeral=True)
            return
        db_add_blocked_user(user.id, reason)
        await ctx.response.send_message(f"User {user.mention} has been added to the blocklist")

    @blocklist_subcommand.command(name="remove_user", description="Remove a user from the blocklist")
    async def blocklist_remove_user(self, ctx: discord.Interaction, user: discord.User):
        if ctx.user.id != int(OWNER_ID):
            await ctx.response.send_message("You do not have permission", ephemeral=True)
            return
        db_remove_blocked_user(user.id)
        await ctx.response.send_message(f"User {user.mention} has been removed from the blocklist")

    @blocklist_subcommand.command(name="add_guild", description="Add a guild to the blocklist")
    async def blocklist_add_guild(self, ctx: discord.Interaction, guild: discord.Guild, reason: str):
        if ctx.user.id != int(OWNER_ID):
            await ctx.response.send_message("You do not have permission", ephemeral=True)
            return
        db_add_blocked_server(guild.id, reason)
        await ctx.response.send_message(f"Guild {guild.name} has been added to the blocklist")

    @blocklist_subcommand.command(name="remove_guild", description="Remove a guild from the blocklist")
    async def blocklist_remove_guild(self, ctx: discord.Interaction, guild: discord.Guild):
        if ctx.user.id != int(OWNER_ID):
            await ctx.response.send_message("You do not have permission", ephemeral=True)
            return
        db_remove_blocked_server(guild.id)
        await ctx.response.send_message(f"Guild {guild.name} has been removed from the blocklist")
