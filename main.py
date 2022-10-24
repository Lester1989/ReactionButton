import interactions


bot = interactions.Client(token="your_secret_bot_token")
bot.load("interactions.ext.enhanced")


bot.start()