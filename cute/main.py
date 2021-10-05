import dataclasses
import discord
import logging
import random

from redbot.core import Config
from redbot.core import commands

class Cute(commands.Cog):

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
			"cutie_id": 0
		}
		self.config.register_guild(**default_guild)

	@commands.command()
	async def cutie(self, ctx):
		current_cutie_id = await self.config.guild(ctx.guild).current_cutie_id()
		cutie_lifetime_seconds = await self.config.guild(ctx.guild).cutie_lifetime_seconds()
		cutie_last_picked_at = await self.config.guild(ctx.guild).cutie_last_picked_at()
		
		# Read current-cutie-id, compare with command timestamp
		# Read last n messages from channel and collect user IDs
		# Pick a random ID
		# Set current-cutie-id
		# Announce!

		# Do we need to pick a new cutie?
		cutieExpired = (cutie_last_picked_at + cutie_lifetime_seconds) > datetime.now().timestamp()
		weNeedToPickSomeone = (current_cutie_id == 0) or cutieExpired

		nameOfCutie = ""

		if weNeedToPickSomeone:
			message_history_depth = self.config.guild(ctx.guild).message_history_depth()

			allNLastAuthors = {}
			async for msg in ctx.channel.history(limit=message_history_depth):
				allNLastAuthors[msg.author.id] = msg.author

			if len(allNLastAuthors) < 1:
				nameOfCutie = "Nobody"

			else:
				newCutie = random.choice(allNLastAuthors.values())

				if newCutie == self.bot:
					nameOfCutie = "I"
				else:
					nameOfCutie = newCutie.display_name

				self.config.guild(ctx.guild).current_cutie_id.set(newCutie.id)
				self.config.guild(ctx.guild).cutie_last_picked_at.set(datetime.now().timestamp())

		else:
			# Just get the user's name
			try:
				cutieUser = ctx.guild.fetch_user(current_cutie_id)
				nameOfCutie = cutieUser.display_name
			except NotFound:
				nameOfCutie = "Anonymous"

		cutieAnnouncement = "{} is the Cutie of the Server right now!".format(nameOfCutie)

		await ctx.send(cutieAnnouncement)