from .main import Cutie

async def setup(bot,):
    await bot.add_cog(Cutie(bot))
