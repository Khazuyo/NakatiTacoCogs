import dataclasses
import discord
import logging
import random

from datetime import datetime

from redbot.core import Config
from redbot.core import commands
from redbot.core import checks

class Cutie(commands.Cog):

	def __init__(self, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.bot = bot

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
		cutieExpired = (cutie_last_picked_at + cutie_lifetime_seconds) > datetime.now().timestamp()
		weNeedToPickSomeone = (cutie_current_id == 0) or cutieExpired

		nameOfCutie = ""

		if weNeedToPickSomeone:
			await ctx.send("Picking a new cutie...")

			message_history_depth = await self.config.guild(ctx.guild).message_history_depth()

			allNLastAuthors = {}
			async for msg in ctx.channel.history(limit=int(message_history_depth)):
				allNLastAuthors[msg.author.id] = msg.author

			if len(allNLastAuthors) < 1:
				nameOfCutie = "Nobody"

			else:
				newCutie = random.choice(list(allNLastAuthors.values()))

				if newCutie == self.bot:
					nameOfCutie = "I"
				else:
					nameOfCutie = newCutie.display_name

				await self.config.guild(ctx.guild).cutie_current_id.set(newCutie.id)
				await self.config.guild(ctx.guild).cutie_last_picked_at.set(datetime.now().timestamp())

		else:
			# Just get the user's name
			cutieUser = ctx.guild.get_member(cutie_current_id)

			if cutieUser == None:
				nameOfCutie = "An anonymous snowflake"
			else:
				nameOfCutie = cutieUser.display_name

		cutieAnnouncement = "{} is the Cutie of the Server right now!".format(nameOfCutie)

		await ctx.send(cutieAnnouncement)

	@commands.command()
	@checks.admin_or_permissions(manage_guild=True)
	async def cutiestats(self, ctx):
		cutie_current_id = await self.config.guild(ctx.guild).cutie_current_id()
		cutie_lifetime_seconds = await self.config.guild(ctx.guild).cutie_lifetime_seconds()
		cutie_last_picked_at = await self.config.guild(ctx.guild).cutie_last_picked_at()
		message_history_depth = await self.config.guild(ctx.guild).message_history_depth()

		ctx.send(
			"Current Cutie: {}\nLifetime: {}\nLast Picked: {}\nDepth: {}"
				.format(
					cutie_current_id, 
					cutie_lifetime_seconds, 
					cutie_last_picked_at, 
					message_history_depth
					)
				)