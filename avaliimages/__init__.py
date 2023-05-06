from .avaliimages import AvaliImages

async def setup(bot):
    await bot.add_cog(AvaliImages(bot))
