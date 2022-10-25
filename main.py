import interactions
import secret

bot = interactions.Client(token=secret.token)
bot.load("interactions.ext.enhanced")
bot.load("cogs.rolebuttons")

bot.start()