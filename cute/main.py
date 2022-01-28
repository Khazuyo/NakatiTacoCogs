import dataclasses
import discord
import logging
import random

from datetime import datetime

from redbot.core import Config
from redbot.core import commands
from redbot.core import checks

from discord import Color, Embed

class Cutie(commands.Cog):

	def __init__(self, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.bot = bot
		self.logger = logging.getLogger("nakati.cutie")

		# Config setup (identifier isn't random btw :3)
		self.config = Config.get_conf(self, identifier=211803212005, force_registration=True,)

		default_global = {

		}
		self.config.register_global(**default_global)

		default_guild = {
			"message_history_depth": 100,
			"cutie_lifetime_seconds": 60,
			"cutie_last_picked_at": 0,
			"cutie_current_id": 0
		}
		self.config.register_guild(**default_guild)

	@commands.command()
	async def cutie(self, ctx):
		cutie_current_id = await self.config.guild(ctx.guild).cutie_current_id()
		cutie_lifetime_seconds = await self.config.guild(ctx.guild).cutie_lifetime_seconds()
		cutie_last_picked_at = await self.config.guild(ctx.guild).cutie_last_picked_at()
		
		# Read current-cutie-id, compare with command timestamp
		# Read last n messages from channel and collect user IDs
		# Pick a random ID
		# Set current-cutie-id
		# Announce!

		# Do we need to pick a new cutie?
		cutieExpired = datetime.now().timestamp() > (cutie_last_picked_at + cutie_lifetime_seconds)
		weNeedToPickSomeone = (cutie_current_id == 0) or cutieExpired

		cuteMember = None

		if weNeedToPickSomeone:
			await ctx.send("Picking a new cutie...")

			message_history_depth = await self.config.guild(ctx.guild).message_history_depth()

			allNLastAuthors = {}
			async for msg in ctx.channel.history(limit=int(message_history_depth)):
				# Don't crown yourself!
				if msg.author.bot:
					continue

				allNLastAuthors[msg.author.id] = msg.author

			if len(allNLastAuthors) < 1:
				await ctx.send("Nobody posted anything here yet!")
				return

			else:
				cuteMember = random.choice(list(allNLastAuthors.values()))
				cutie_last_picked_at = datetime.now().timestamp()

				await self.config.guild(ctx.guild).cutie_current_id.set(cuteMember.id)
				await self.config.guild(ctx.guild).cutie_last_picked_at.set(cutie_last_picked_at)

		else:
			cuteMember = ctx.guild.get_member(cutie_current_id)

			# Member could have left!
			if cuteMember == None:
				await ctx.send("Cute member managed to escape! Please try again! :O")
                                await self.config.guild(ctx.guild).cutie_current_id.set(0)
				return

		# Look for a color role and extract the color used
		embedColor = Color.orange()
		for role in cuteMember.roles:
			if "color-" in role.name:
				embedColor = role.color
				break

		try:
			embed = discord.Embed(
				title=cuteMember.display_name, 
				description="... is the cutie of the server!",
				color=embedColor
			)

			timeToNextPick = (cutie_last_picked_at + cutie_lifetime_seconds) - datetime.now().timestamp();
			if timeToNextPick < 0:
				timeToNextPick = 0

			# Neat and simple way to do it using division with remainder
			# https://stackoverflow.com/questions/27779677/how-to-format-elapsed-time-from-seconds-to-hours-minutes-seconds-and-milliseco
			remainingHours, rem = divmod(timeToNextPick, 3600)
			remainingMinutes, remainingSeconds = divmod(rem, 60)
			remainingTime = ""

			if remainingHours > 0:
				remainingTime += "{:0>2}h ".format(int(remainingHours))

			if remainingMinutes > 0:
				remainingTime += "{:0>2}m ".format(int(remainingMinutes))

			if remainingSeconds > 0:
				remainingTime += "{:05.2f}s".format(remainingSeconds)

			embed.set_footer(text="Will be able to pick a new cutie in {time}".format(time=remainingTime))
			embed.set_thumbnail(url=cuteMember.avatar_url)

			await ctx.send(embed=embed)

		except discord.errors.HTTPException as httpEx:
			#await ctx.send("The current server cutie is:\n\n**{}**".format(cuteMember.display_name))
			await ctx.send("Discord seems to have a hiccup - can you slow down a bit please and check <https://discordstatus.com>? Thanks and sowwy ;w; <3")
			self.logger.warning(str(httpEx))

	@commands.command()
	@checks.admin_or_permissions(manage_guild=True)
	async def cutiestats(self, ctx):
		cutie_current_id = await self.config.guild(ctx.guild).cutie_current_id()
		cutie_lifetime_seconds = await self.config.guild(ctx.guild).cutie_lifetime_seconds()
		cutie_last_picked_at = await self.config.guild(ctx.guild).cutie_last_picked_at()
		message_history_depth = await self.config.guild(ctx.guild).message_history_depth()

		await ctx.send(
			"Current Cutie: {}\nLifetime: {}\nLast Picked: {}\nDepth: {}\nRemaining Lifetime: {}"
				.format(
					cutie_current_id, 
					cutie_lifetime_seconds, 
					cutie_last_picked_at, 
					message_history_depth,
					(cutie_last_picked_at + cutie_lifetime_seconds) - datetime.now().timestamp() 
				)
			)

	@commands.group()
	@checks.admin_or_permissions(manage_guild=True)
	async def cutieset(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Invalid Subcommand")

	@cutieset.command()
	@checks.admin_or_permissions(manage_guild=True)
	async def lifetime(self, ctx, time_in_seconds: int):
		if time_in_seconds < 0:
			await ctx.send("The time must be 0 or greater!")
			return

		await self.config.guild(ctx.guild).cutie_lifetime_seconds.set(time_in_seconds)
		await ctx.tick()

	@cutieset.command()
	@checks.admin_or_permissions(manage_guild=True)
	async def depth(self, ctx, depth_in_messages: int):
		if depth_in_messages < 1:
			await ctx.send("Depth must be at least 1 to make any sense at all")
			return

		await self.config.guild(ctx.guild).message_history_depth.set(depth_in_messages)
		await ctx.tick()
