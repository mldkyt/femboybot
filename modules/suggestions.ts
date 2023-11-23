import {
  ButtonInteraction,
  CacheType,
  Channel,
  ChatInputCommandInteraction,
  GuildMember,
  Message,
  Role,
  SlashCommandBuilder,
  SlashCommandSubcommandsOnlyBuilder,
} from "discord.js";
import { Module } from "./type";
import { addBugReport, addSuggestion } from "../data/feedback";

export class Suggestions implements Module {
  onRoleEdit(before: Role, after: Role): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onChannelCreate(role: Channel): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onChannelEdit(before: Channel, after: Channel): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onChannelDelete(role: Channel): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onMessageDelete(msg: Message<boolean>): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onMessageEdit(
    before: Message<boolean>,
    after: Message<boolean>
  ): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onMemberJoin(member: GuildMember): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onMemberEdit(before: GuildMember, after: GuildMember): Promise<void> {
    throw new Error("Method not implemented.");
  }
  onMemberLeave(member: GuildMember): Promise<void> {
    throw new Error("Method not implemented.");
  }
  commands: SlashCommandBuilder[] | SlashCommandSubcommandsOnlyBuilder[] = [
    new SlashCommandBuilder()
      .setName("feedback")
      .setDescription("Send feedback to the Discord bot owner")
      .addSubcommand((subcommand) =>
        subcommand
          .setName("suggest")
          .setDescription("Suggest a feature to be added to the bot")
          .addStringOption((option) =>
            option
              .setName("suggestion")
              .setDescription("The suggestion you want to send")
              .setRequired(true)
          )
      )
      .addSubcommand((subcommand) =>
        subcommand
          .setName("bug")
          .setDescription("Create a bug report")
          .addStringOption((option) =>
            option
              .setName("bug")
              .setDescription("The bug you want to report")
              .setRequired(true)
          )
      ),
  ];
  async onMessage(msg: Message): Promise<void> {}
  async onSlashCommand(
    interaction: ChatInputCommandInteraction<CacheType>
  ): Promise<void> {
    if (interaction.commandName !== "feedback") return;
    switch (interaction.options.getSubcommand(true)) {
      case "suggest":
        const a = interaction.options.getString("suggestion", true);
        addSuggestion(interaction.user.username, a);
        await interaction.reply({
          content: "Your suggestion has been sent!",
          ephemeral: true,
        });
        break;
      case "bug":
        const b = interaction.options.getString("bug", true);
        addBugReport(interaction.user.username, b);
        await interaction.reply({
          content: "Your bug report has been sent!",
          ephemeral: true,
        });
        break;
    }
  }
  async onButtonClick(
    interaction: ButtonInteraction<CacheType>
  ): Promise<void> {}

  async onRoleCreate(role: Role): Promise<void> {}
  async onRoleDelete(role: Role): Promise<void> {}
}