import random
import discord
import re

from redbot.core import commands, Config, checks
from discord import Color, Embed

class AvaliImages(commands.Cog):

    def __init__(self, bot):
        def_config_guild = {
            "images": {
                "default": {

                }
            }
        }
        
        self.bot = bot
        self.cfg = Config.get_conf(self, identifier=0x7855fd624d31)
        self.cfg.register_guild(**def_config_guild)

    # *********
    # Functions
    # *********

    def addErroneousPost(self, errorDictionary, msgRef, errorKey, error):
        if not msgRef.jump_url in errorDictionary:
            errorDictionary[msgRef.jump_url] = {}

        errorDictionary[msgRef.jump_url]['poster'] = msgRef.author

        errorDictionary[msgRef.jump_url]['errors'] = {}
        errorDictionary[msgRef.jump_url]['errors'][errorKey] = error

        print("{u} => {e}".format(u=msgRef.jump_url, e=errorKey))

    # ********
    # Commands
    # ********

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def chirp(self, context: commands.Context):
        """
        Picks a random image from the image database and posts it.
        """
        imageDB = await self.cfg.guild(context.guild).images()

        # Pick default for now
        imageList = imageDB["default"]
        keyURLs = list(imageList)

        if len(keyURLs) < 1:
            await context.send("No images in db, please sync first!")
            return

        selectedURL = keyURLs[random.randint(0, len(keyURLs) - 1)]
        selectedRecord = imageList[selectedURL]

        try:
            embed = discord.Embed(
                title=selectedRecord["title"], 
                url=selectedRecord["source"],
                description="By {artist}"
                    .format(
                        artist=selectedRecord["artist"]
                    ), 
                color=Color.orange()
            )
            embed.set_image(url=selectedURL)
            embed.set_footer(text="Posted by {name} | Requested by {req}".format(name=selectedRecord["poster"], req=context.author.display_name))

            await context.send(embed=embed)

            # print("Posting image: " + selectedURL)

        except discord.errors.HTTPException as httpEx:
            await context.send("*hiccup* Whoopsie...\nImage: {u}".format(u=selectedURL))
            print(str(httpEx))

    @commands.group()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)
    async def chirpset(self, ctx: commands.Context):
        """Configure the Avali images cog"""
        pass

    @chirpset.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)
    async def syncdb(self, context: commands.Context):
        """
        Update the images database based on images found in the current channel.
        The images / messages must have a specific format, it must contain
        Title: A title that describes the image
        Author: The artist of the image
        Description: An optional description (e.g. this is Nya sleeping)
        """

        # Kill the messenger so it doesn't get processed
        await context.message.delete()

        posts = [message async for message in context.channel.history(limit=1000)]
        
        newDB = {}
        numRecordsAdded = 0

        malformedPosts = {}

        autoDestroyAfter = 30.0

        # Regular Expressions for checking and parsing
        fileExtRegEx = re.compile("^https?://.*?\\.(?:png|jpg|jpeg|gif)$", re.IGNORECASE)
        parseTitle = re.compile("^[Tt]itle: (.*?)$")
        parseArtist = re.compile("^[Aa]rtist: (.*?)$")
        parseSource = re.compile("^[Ss]ource:\\s+(https?://.*?)$")

        # Post format:
        # 
        # 1 attachment (png, jpg, jpeg, gif)
        # 
        # Fields:
        # 
        # Title: <Some title>
        # Artist: <Artist credit or "Unknown"
        # Source: <Source URL>
        await context.send("Alright, processing posts. This might take a bit, please be patient!", delete_after=autoDestroyAfter)

        try:
            for post in posts:
                if post.author == self.bot.user:
                    await post.delete()
                    continue

                if len(post.attachments) != 1:
                    self.addErroneousPost(
                        malformedPosts, 
                        post,
                        'attachments', 
                        "Post has {a} attachments, exactly 1 required".format(a=len(post.attachments))
                    )
                    continue

                imageAttachment = post.attachments[0]

                if fileExtRegEx.match(imageAttachment.url) == None:
                    self.addErroneousPost(
                        malformedPosts, 
                        post,
                        'format', 
                        "Image format not allowed"
                    )
                    continue

                fieldTitle = ""
                fieldArtist = ""
                fieldSource = ""

                postFields = post.content.split("\n")
                for field in postFields:

                    # Look for the Title field
                    matchObj = parseTitle.search(field)
                    if matchObj != None:
                        fieldTitle = matchObj.group(1)
                        continue

                    # Look for the Artist field
                    matchObj = parseArtist.search(field)
                    if matchObj != None:
                        fieldArtist = matchObj.group(1)
                        continue                    

                    # Look for the Title field
                    matchObj = parseSource.search(field)
                    if matchObj != None:
                        fieldSource = matchObj.group(1)
                        continue

                # Parsing done, check if mandatory fields are present
                fieldsMissing = False

                if len(fieldTitle) < 1:
                    fieldsMissing = True
                    self.addErroneousPost(
                        malformedPosts, 
                        post,
                        'title', 
                        "Title field is empty or malformed"
                    )

                if len(fieldArtist) < 1:
                    fieldsMissing = True
                    self.addErroneousPost(
                        malformedPosts, 
                        post,
                        'artist', 
                        "Artist field is empty or malformed"
                    )

                if len(fieldSource) < 1:
                    fieldsMissing = True
                    self.addErroneousPost(
                        malformedPosts, 
                        post,
                        'source', 
                        "Source field is empty or malformed"
                    )

                if fieldsMissing:
                    continue

                newDB[imageAttachment.url] = {
                    "title": fieldTitle,
                    "artist": fieldArtist,
                    "source": fieldSource,
                    "poster": post.author.display_name
                }

                numRecordsAdded = numRecordsAdded + 1

        except discord.Forbidden as f:
            await context.send("I'm missing some permissions. Make sure I can use and clear (manage_messages) reactions here.")
            return
        #except Exception as ex:
        #    await context.send("I could not parse the posts: {e}".format(e=ex))
        #    return

        if(len(malformedPosts) > 0):
            await context.send(
                "{n} records contain errors:"
                    .format(
                        n=len(malformedPosts)
                    )
            )

            maxPostsPerMessage = 5

            currentMsgNum = 1
            currentPost = ""

            for jumpUrl, data in malformedPosts.items():

                errors = ', '.join(list(data['errors'].values()))

                currentPost = currentPost + "> <@{i}> {j}\n> {e}\n\n".format(
                    i=data['poster'].id,
                    j=jumpUrl, 
                    e=errors
                )

                if currentMsgNum >= maxPostsPerMessage:
                    await context.send(currentPost)
                    currentPost = ""
                    currentMsgNum = 0

                currentMsgNum = currentMsgNum + 1

            # There might still be a remainder of messages if the number
            # of erroneous posts is < maxPostsPerMessage so send those too
            if(len(currentPost) > 0):
                await context.send(currentPost)

        # "default" is the only category right now.
        _n = {"default": newDB}
        
        await self.cfg.guild(context.guild).images.set(_n)
        await context.send(
            "Updated. Synced {n} records"
                .format(
                    n=numRecordsAdded
                )
        )

    @chirpset.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)
    async def dumpurls(self, context: commands.Context):
        """Quickly extract all image URLs"""
        imageDB = await self.cfg.guild(context.guild).images()

        # Pick default for now
        imageList = imageDB["default"]
        imageIndex = 0
        currentPost = ""

        for url in imageList:
            currentPost = currentPost + "URL: {u}\nTitle: {t}\nArtist: {a}\nSource: {s}\nPoster: {p}\n-----\n".format(
                u=url,
                t=imageList[url]['title'], 
                a=imageList[url]['artist'], 
                s=imageList[url]['source'], 
                p=imageList[url]['poster']
            )

            if imageIndex % 4 == 0:
                imageIndex = 0
                await context.send(currentPost)
                currentPost = ""

            imageIndex = imageIndex + 1
