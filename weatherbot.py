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


# 1st Step: Initialize the bot---------------------------------------------------------------------------------
intents = nextcord.Intents.default()
intents.message_content = True
#This section allows the bot to see the users
intents.members = True
bot = commands.Bot(command_prefix="!", intents = intents)

# Dictionary to store user cities
user_cities = {}

# 2nd Step: What to do when the bot is ready to go-------------------------------------------------------------
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}') # Can be edited 

# List of greeting phrases (Can be added as many as needed)
greeting_English = [
    "**Hey, I'm glad you asked, {user}!**",
    "**Sure thing, {user}!**",
    "**Happy to help, {user}!**",
    "**Absolutely, {user}!**",
    "**Of course, {user}!**"
]
greeting_Spanish = [
    "**Hola {user}, que bueno que preguntas!**",
    "**Claro, {user}!**",
    "**Feliz de poder ayudarte, {user}!**",
    "**Aquí está la información que solicitaste, {user}!**",
    "**Por supuesto, {user}!**"
]

# 3rd Step: Get user's location from saved list or add it if needed----------------------------------------------
@bot.command(name='get_location')
async def get_location(ctx):
    #Check if the author.id is already saved in user_cities list, which means that the user has entered the city where lives before
    if ctx.author.id in user_cities:
        await ctx.send("Your city information is already saved.")
        return
    await ctx.send("Please enter your city:")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        #Try to save the city of the user in the list
        response = await bot.wait_for('message', check=check, timeout=30.0)
        city = response.content
        user_cities[ctx.author.id] = city
        await ctx.send(f"Your city ({city}) has been saved.")
    except nextcord.ext.commands.errors.CommandInvokeError as e:
        await ctx.send("Error occurred. Please try again.")
        print(e)
    except Exception as e:
        await ctx.send("No response or timeout. Please try again.")
        print(e)


# 4th Step: Command to get weather information------------------------------------------------------------------
@bot.command(name='weather')
async def get_weather(ctx, *, city: str): #Get info of the weather of the given city
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
        greeting = random.choice(greeting_English).format(user=ctx.author.name)
        await ctx.send(f"{greeting}\n{weather_report}")
    except Exception as e:
        await ctx.send("An error occurred while fetching the weather data. Please contact @stewpidest")
        print(e)


# ------------5th Step: Add default commands------------------#-----------------------------------------------------
# COMMAND to get weather information based on user's location previously saved using id
@bot.command(name='weather_me')
async def get_weather_by_location(ctx):
    #Search if id is saved in user_cities list
    city = user_cities.get(ctx.author.id)
    if not city:
        await ctx.send("Your city information is not saved. Please use !get_location to save it.")
        return
    await get_weather(ctx, city=city)

# COMMAND to get weather information for all active members of the server
@bot.command(name='weather_all')
async def get_weather_for_all(ctx):
    try:
        members = ctx.guild.members
        weather_info = []

        #Find every member's city
        for member in members:
            if not member.bot:  # Skip bot accounts
                #If member has saved the city in the list, get the city name
                city = user_cities.get(member.id)
                if not city:
                    weather_info.append(f"{member.display_name}: City information not saved.")
                else:
                    try:
                        # Get weather information for the provided city
                        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
                        weather_response = requests.get(url)
                        weather_data = weather_response.json()

                        if "error" in weather_data:
                            weather_info.append(f"{member.display_name}: City {city} not found.")
                        else:
                            location = weather_data["location"]
                            current = weather_data["current"]

                            weather_report = (
                                f"**The Weather in {location['name']}, {location['country']}:**\n"
                                f"The Condition is {current['condition']['text']}"
                                f" with a Temperature of ***{current['temp_f']}°F***"
                                f" but really Feels Like ***{current['feelslike_f']}°F***.\n"
                                f"In the other hand, Humidity is in ***{current['humidity']}%***"
                                f" and the Wind Speed is ***{current['wind_mph']} mph***.\n\n"
                            )
                            weather_info.append(f"{member.display_name}: {weather_report}")
                    except Exception as e:
                        weather_info.append(f"{member.display_name}: An error occurred while fetching weather data.")
                        print(e)

        if weather_info:
            await ctx.send("\n\n".join(weather_info))
        else:
            await ctx.send("No weather information available for active members.")
            
    except Exception as e:
        await ctx.send("An error occurred while fetching weather information for all members.")
        print(e)


# COMMAND to get weather information in Spanish
@bot.command(name='weather_spanish')
async def get_weather_spanish(ctx, *, city: str):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&lang=es"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            await ctx.send(f"City {city} not found.")
            return

        location = data["location"]
        current = data["current"]

        weather_report = (
            f"**El clima en {location['name']}, {location['country']}:**\n"
            f"La condición es {current['condition']['text']}"
            f" con una temperatura de ***{current['temp_f']}°F***"
            f" pero se siente como ***{current['feelslike_f']}°F***.\n"
            f"Por otro lado, la humedad es del ***{current['humidity']}%***"
            f" y la velocidad del viento es de ***{current['wind_mph']} mph***.\n\n"
            f"**¡Pregúntame por cualquier ciudad!**"
        )

        #This will choose a random greeting from the stack
        greeting = random.choice(greeting_Spanish).format(user=ctx.author.name)
        await ctx.send(f"{greeting}\n{weather_report}")
    except Exception as e:
        await ctx.send("Se produjo un error al obtener los datos meteorológicos. Por favor, contacta a @stewpidest")
        print(e)


#Help COMMAND: This command shows the list of all default commands
@bot.command(name='commands')
async def show_commands(ctx):
    commands_list = [
        "`!weather <city>` - Get the current weather for a specified city.",
        "`!weather_me` - Get the weather based on your location (If it is saved).",
        "`!weather_all` - Get the weather for all active members of the server (If it is saved).",
        "`!weather_spanish <city>` - Get the weather in Spanish for a specified city.",
        "`!get_location` - Save your current location.",
        # Add more commands here as needed
    ]
    commands_text = "**Here are the commands you can use:**\n\n"
    commands_text += "\n".join([f"• {cmd}" for cmd in commands_list])
    await ctx.send(commands_text)

#About Me COMMAND: This command shows information on the bot itself
@bot.command(name='about')
async def about_command(ctx):
    embed = nextcord.Embed(
        title= "About Me",
        description= "Hello! I'm your servers Weather Bot. Currently I'm under development so don't have many useful features as of yet."
    )
    embed.add_field(name="Author", value="Capstone I Group I", inline=True)
    embed.add_field(name="Version", value="0", inline=True)
    embed.add_field(name="Library", value="nextcord", inline=True)
    embed.add_field(name="Commands", value="Use `!commands` to see the list of available commands.", inline=True)

    await ctx.send(embed = embed)

# 6th Step: Let's run the bot--------------------------------------------------------------------------------------------
try:
    # Checks if Bot Token is working or valid
    if API_BOT is None:
        raise ValueError("Issue with Discord Token:\nEither check credentials or reset token on the developer portal.")
    bot.run(API_BOT)
except ValueError as e:
    print(e)
