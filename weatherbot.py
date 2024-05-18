import nextcord
from nextcord.ext import commands
import requests #This is the library 
import random #This library will be used to select a random answer to the user
import os
from dotenv import load_dotenv #This library is used for the dotenv file


# Load environment variables
load_dotenv(".env")

#----APIs to use----#
# WeatherAPI key
API_KEY = os.getenv('KEY')
# API_BOT_Discord
API_BOT = os.getenv('TOKEN')
#-------------------#


# 1st Step: Initialize the bot
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents = intents)

# 2nd Step: What to do when the bot is ready to go
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}') # Can be edited 

# List of greeting phrases (Can be added as many as needed)
greetings = [
    "**Hey, I'm glad you asked, {user}!**",
    "**Sure thing, {user}!**",
    "**Happy to help, {user}!**",
    "**Absolutely, {user}!**",
    "**Of course, {user}!**"
]


# 3rd Step: Command to get weather information
@bot.command(name='weather')
async def get_weather(ctx, *, city: str): #For now is done to write the city, it would be great to get that automatic instead. (Change)
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response = requests.get(url)
        data = response.json()

        #If does not found the city, show an error
        if "error" in data:
            await ctx.send(f"City {city} not found.") #The message can be edited
            return

        location = data["location"]
        current = data["current"]

        #Here it can be added as many as parameters necessary to show in the weather request
        weather_report = (
            f"**The Weather in {location['name']}, {location['country']}:**\n"
            f"The Condition is {current['condition']['text']}"
            f" with a Temperature of ***{current['temp_f']}°F***"
            f" but really Feels Like ***{current['feelslike_f']}°F***.\n"
            f"In the other hand, Humidity is in ***{current['humidity']}%***"
            f" and the Wind Speed is ***{current['wind_mph']} mph***.\n\n"
            f"**Ask me for any City!**"
        )

        #This will choose a random greeting from the stack
        greeting = random.choice(greetings).format(user=ctx.author.name)
        await ctx.send(f"{greeting}\n{weather_report}")
    except Exception as e:
        await ctx.send("An error occurred while fetching the weather data. Please contact @stewpidest")
        print(e)

# 4 Step: Let's run the bot :)
try:
    # Checks if Bot Token is working or valid
    if API_BOT is None:
        raise ValueError("Issue with Discord Token:\nEither check credentials or reset token on the developer portal.")
    bot.run(API_BOT)
except ValueError as e:
    print(e)
