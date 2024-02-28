
import discord

from utils.settings import get_setting, set_setting
from discord.ext import commands as cmds


class SettingsCommands(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()

    settings_subcommand = discord.SlashCommandGroup(
        name="settings", description="Settings for your server")

    @settings_subcommand.command(name="logging_channel", description="Set the logging channel")
    @cmds.guild_only()
    @cmds.has_guild_permissions(manage_guild=True)
    async def settings_logging_channel(self, ctx: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            setting = get_setting(ctx.guild.id, 'logging_channel', '0')
            if setting == '0':
                await ctx.response.send_message("No logging channel set")
            else:
                await ctx.response.send_message(f"Logging channel is set to <#{setting}>")
        else:
            set_setting(ctx.guild.id, 'logging_channel', str(channel.id))
            await ctx.response.send_message(f"Logging channel set to {channel.mention}")
