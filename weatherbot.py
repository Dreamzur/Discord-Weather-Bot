import nextcord
from nextcord.ext import commands, tasks
import requests #This is the library 
import random #This library will be used to select a random answer to the user
import os
from dotenv import load_dotenv #This library is used for the dotenv file
from PIL import Image
from datetime import timedelta
import io

# Load environment variables
load_dotenv(".env")

#----APIs to use----#
API_KEY = os.getenv('KEY') # WeatherAPI key
API_BOT = os.getenv('TOKEN') # API_BOT_Discord
DEEP_AI_API_KEY = os.getenv('DEEP_AI_API_KEY') # DEEP_AI_API to generate AI Images
#-------------------#


# 1st Step: Initialize the bot---------------------------------------------------------------------------------
intents = nextcord.Intents.default()
intents.message_content = True
#This section allows the bot to see the users
intents.members = True
bot = commands.Bot(command_prefix="!", intents = intents)

# Dictionary to store user cities and preferences
user_cities = {}
user_weather_tips = {}
user_weather_alerts = {}
weather_update_tasks = {}

# 2nd Step: What to do when the bot is ready to go-------------------------------------------------------------
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}') # Can be edited 
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == 'bot-testing':  # Channel name
                await channel.send(f'Hello! I am Weather Cat Bot and I am now ready to assist you with weather updates! (!commands)')
                break

# List of greeting phrases (Can be added as many as needed)
greeting_English = [
    "**Hey {user}! Ready to dive into the weather?**",
    "**Well, hello there {user}! Let's get this weather party started!**",
    "**Hey hey, {user}! Weather adventures await!**",
    "**Greetings, {user}! Let's weather the day together!**",
    "**Hey {user}! The weather's fine, and so are you! Let's do this!**",
    "**Hiya, {user}! Let's sprinkle some weather magic!**",
    "**Hey {user}! Time to weather up and dive in!**",
    "**Hey {user}! Let's weather this storm together!**",
    "**Well, hello {user}! Weather or not, here we come!**",
]
greeting_Spanish = [
    "**Hola {user}, que bueno que preguntas!**",
    "**Claro, {user}!**",
    "**Feliz de poder ayudarte, {user}!**",
    "**Aquí está la información que solicitaste, {user}!**",
    "**Por supuesto, {user}!**"
]
# Default weather tips
weather_tips = {
    'Rain': "Don't forget your umbrella!",
    'Snow': "Wear warm clothes and stay safe!",
    'Heat': "Stay hydrated and avoid the sun during peak hours!",
    'Clear': "Enjoy the beautiful weather!",
    'Thunderstorm': "Stay indoors and avoid using electrical appliances!",
    'Partly cloudy': "Don't forget your umbrella! It may rain."
}

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

#Method to generate AI Image with the weather prompt
async def generate_weather_image(condition: str):
    url = "https://api.deepai.org/api/text2img"
    headers = {
        'api-key': DEEP_AI_API_KEY
    }
    # Adjusted prompt for creating a weather cat character
    data = {
        'text': f"Genius Mode: Create in weather climate a 3D animated cat character that dress and animate according to the weather conditions, such as {condition}."
    }

    print(f"Prompt sent to DeepAI: {data['text']}")  # Log the prompt for debugging

    response = requests.post(url, headers=headers, data=data)
    result = response.json()
    
    # Print the result for debugging
    print(f"DeepAI response: {result}")

    if 'output_url' in result:
        image_response = requests.get(result['output_url'])
        image = Image.open(io.BytesIO(image_response.content))
        return image
    else:
        raise Exception(f"Error generating image with DeepAI API: {result.get('error', 'Unknown error')}")

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
            f"**Ask me for any City!**\n\n"
            f"**Weather Cat Ilustration:**"
        )

        #This will choose a random greeting from the stack
        greeting = random.choice(greeting_English).format(user=ctx.author.name)
        await ctx.send(f"{greeting}\n{weather_report}")

        weather_image = await generate_weather_image(current['condition']['text'] + ", in " + location['name'] + ", " + location['country'])
        with io.BytesIO() as image_binary:
            weather_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=nextcord.File(fp=image_binary, filename='weather.png'))

        # Send weather tips if enabled
        if user_weather_tips.get(ctx.author.id, False):
            condition = current['condition']['text']
            tip = weather_tips.get(condition, "No tips available for this weather condition.")
            await ctx.send(f"**Weather Tip:** {tip}")
        else:
            await ctx.send(f"**(Activate Weather Tips with !weatherTips on)**")

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

# Command to enable/disable weather tips
@bot.command(name='weatherTips')
async def toggle_weather_tips(ctx, status: str):
    if status.lower() == "on":
        user_weather_tips[ctx.author.id] = True
        await ctx.send("Weather tips enabled.")
    elif status.lower() == "off":
        user_weather_tips[ctx.author.id] = False
        await ctx.send("Weather tips disabled.")
    else:
        await ctx.send("Invalid input. Use `!weatherTips [on/off]`.")

# Command to enable/disable severe weather alerts
@bot.command(name='weatherAlerts')
async def toggle_weather_alerts(ctx, status: str):
     #Search if id is saved in user_cities list
    city = user_cities.get(ctx.author.id)
    if city:
        if status.lower() == "on":
            user_weather_alerts[ctx.author.id] = True
            await ctx.send("Severe weather alerts enabled for "+str(ctx.author.name)+" about "+ str(user_cities.get(ctx.author.id))+" weather.")
        elif status.lower() == "off":
            user_weather_alerts[ctx.author.id] = False
            await ctx.send("Severe weather alerts disabled.")
        else:
            await ctx.send("Invalid input. Use `!weatherAlerts [on/off]`.")
    else: await ctx.send("Your city information is not saved. Please use !get_location to save it.")

# Command to set up regular weather updates (float)
@bot.command(name='setWeatherUpdates')
async def set_weather_updates(ctx, city: str, interval: float):
    user_id = ctx.author.id
    if user_id in weather_update_tasks:
        weather_update_tasks[user_id].cancel()

    async def send_weather_updates():
        while True:
            try:
                url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
                response = requests.get(url)
                data = response.json()

                if "error" in data:
                    await ctx.send(f"City {city} not found.")
                    return

                location = data["location"]
                current = data["current"]

                weather_report = (
                    f"**The Weather in {location['name']}, {location['country']}:**\n"
                    f"The Condition is {current['condition']['text']}"
                    f" with a Temperature of ***{current['temp_f']}°F***"
                    f" but really Feels Like ***{current['feelslike_f']}°F***.\n"
                    f"In the other hand, Humidity is in ***{current['humidity']}%***"
                    f" and the Wind Speed is ***{current['wind_mph']} mph***.\n\n"
                    f"**Weather Update for {city}**\n\n"
                )

                await ctx.send(weather_report)
                
                # Send weather tips if enabled
                if user_weather_tips.get(ctx.author.id, False):
                    condition = current['condition']['text']
                    tip = weather_tips.get(condition, "No tips available for this weather condition.")
                    await ctx.send(f"**Weather Tip:** {tip}")
                else:
                    await ctx.send(f"**(Activate Weather Tips with !weatherTips on)**")
                    

                await nextcord.utils.sleep_until(nextcord.utils.utcnow() + timedelta(minutes=interval))
                
            except Exception as e:
                print(e)
                await nextcord.utils.sleep_until(nextcord.utils.utcnow() + timedelta(minutes=interval))

    task = bot.loop.create_task(send_weather_updates())
    weather_update_tasks[user_id] = task
    await ctx.send(f"Weather updates for {city} set at an interval of {interval} minutes.")

# Command to stop weather updates
@bot.command(name='stopWeatherUpdates')
async def stop_weather_updates(ctx):
    user_id = ctx.author.id
    if user_id in weather_update_tasks:
        weather_update_tasks[user_id].cancel()
        del weather_update_tasks[user_id]
        await ctx.send("Weather updates stopped.")
    else:
        await ctx.send("No weather updates are currently set.")

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
        "`!weather <city>` - Get the current weather for a specified city, complete with an AI-generated weather image.",
        "`!weather_me` - Receive personalized weather updates based on your saved location.",
        "`!weather_all` - Check the weather for all active members of the server, if their location is saved.",
        "`!weather_spanish <city>` - ¡Obtén el clima en español para una ciudad específica!",
        "`!get_location` - Save your current location for personalized weather updates",
        "`!weatherTips [on/off]` - Toggle helpful weather tips on or off.",
        "`!weatherAlerts [on/off]` - Activate or deactivate severe weather alerts.",
        "`!setWeatherUpdates <city> <interval>` - Set up regular weather updates for a specific city at a chosen interval.",
        "`!stopWeatherUpdates` - Stop receiving regular weather updates.",
        "`!about` - Learn more about this bot and its capabilities.",
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
        description= "Hello! I'm here to provide you with the latest weather updates and tips, right in your Discord server!"
    )
    embed.add_field(name="Author", value="Capstone I Group I", inline=True)
    embed.add_field(name="Version", value="0", inline=True)
    embed.add_field(name="Library", value="nextcord", inline=True)
    embed.add_field(name="Commands", value="Use `!commands` to see the list of available commands.", inline=True)

    await ctx.send(embed = embed)

# Task to monitor severe weather conditions
@tasks.loop(minutes=15)
async def check_severe_weather():
    for user_id, city in user_cities.items():
        if user_weather_alerts.get(user_id, False):
            try:
                url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
                response = requests.get(url)
                data = response.json()

                if "error" in data:
                    continue

                current = data["current"]
                if current["condition"]["text"] in ["Thunderstorm", "Heavy Rain", "Blizzard"]:
                    user = await bot.fetch_user(user_id)
                    await user.send(f"Severe weather alert for {city}: {current['condition']['text']}")

            except Exception as e:
                print(e)

check_severe_weather.start()

# 6th Step: Let's run the bot--------------------------------------------------------------------------------------------
try:
    # Checks if Bot Token is working or valid
    if API_BOT is None:
        raise ValueError("Issue with Discord Token:\nEither check credentials or reset token on the developer portal.")
    bot.run(API_BOT)
except ValueError as e:
    print(e)
