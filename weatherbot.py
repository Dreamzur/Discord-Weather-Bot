import nextcord
from nextcord.ext import commands, tasks
from discord.ext import commands
import discord
import requests #This is the library 
import random #This library will be used to select a random answer to the user
import os
from dotenv import load_dotenv #This library is used for the dotenv file
from PIL import Image
from datetime import timedelta
import io
import psutil
import logging
import asyncio
import schedule
import psutil

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#----APIs to use----#
API_KEY = os.getenv('KEY') # WeatherAPI key
API_BOT = os.getenv('TOKEN') # API_BOT_Discord
DEEP_AI_API_KEY = os.getenv('DEEP_AI_API_KEY') # DEEP_AI_API to generate AI Images
NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # News API key
JOKE_API_KEY = os.getenv('JOKE_API_KEY') # Jokes API key
#-------------------#


# 1st Step: Initialize the bot---------------------------------------------------------------------------------
intents = nextcord.Intents.default()
#This allows the bot to access the messages
intents.message_content = True
#This section allows the bot to see the users
intents.members = True
bot = commands.Bot(command_prefix="!", intents = intents)

# Dictionary to store user cities and preferences
user_cities = {}
user_weather_tips = {}
user_weather_alerts = {}
weather_update_tasks = {}
# Dictionary to store user preferences (Celsius or Fahrenheit)
user_preferences = {}
# Dictionary to store user activity
user_activity = {}

# Clothing suggestions based on weather condition
clothing_suggestions = {
    'Rain': "Wear a waterproof jacket and carry an umbrella.",
    'Snow': "Bundle up with a heavy coat, gloves, and a hat.",
    'Heat': "Wear light, breathable clothing, and sunglasses.",
    'Clear': "A t-shirt and jeans will be perfect.",
    'Thunderstorm': "Stay indoors, but if you must go out, wear sturdy shoes and a waterproof jacket.",
    'Partly cloudy': "A light jacket should be sufficient."
}

# 2nd Step: What to do when the bot is ready to go-------------------------------------------------------------
@bot.event
async def on_ready():
    print(f'\n\n\nLogged in as {bot.user}') 
    update_stats.start()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == 'bot-testing':  # Channel name
                await channel.send(f'Hello! I am Weather Cat Bot and I am now ready to assist you with weather updates! (!commands)')
                break

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    # Increment message count for the user
    user_id = message.author.id
    if user_id in user_activity:
        user_activity[user_id] += 1
    else:
        user_activity[user_id] = 1

    await bot.process_commands(message)

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
# Shut down messages for the bot (Can add more if needed...)
shutdown_Message = [
    "Ciao for now! I'm off to count zeros and ones.",
    "System shutting down. I'll dream of algorithms!",
    "Shutting down... Don't worry, I'll be back before you can say 'artificial intelligence'!",
    "Time to hit the hay... or whatever it is bots hit.",
    "Powering down... Time to practice my shutdown dance moves!",
    "Signing off... I'm going where no bot has gone before: offline!",
]
#weather quiz: Examples of questions and answers
weather_quiz = [
    {
        "question": "What instrument measures wind speed?",
        "answers": {
            "A": "Barometer",
            "B": "Thermometer",
            "C": "Anemometer",
            "D": "Hygrometer"
        },
        "correct_answer": "C"
    },
    {
        "question": "Which type of cloud is typically associated with thunderstorms?",
        "answers": {
            "A": "Cumulonimbus",
            "B": "Cirrus",
            "C": "Stratus",
            "D": "Nimbostratus"
        },
        "correct_answer": "A"
    },
    {
        "question": "What does 'Fahrenheit' measure?",
        "answers": {
            "A": "Air Pressure",
            "B": "Humidity",
            "C": "Wind Speed",
            "D": "Temperature"
        },
        "correct_answer": "D"
    },
    {
        "question": "Which of these is a measure of humidity?",
        "answers": {
            "A": "Anemometer",
            "B": "Hygrometer",
            "C": "Barometer",
            "D": "Thermometer"
        },
        "correct_answer": "B"
    },
    {
        "question": "What causes rainbows to appear after a rain shower?",
        "answers": {
            "A": "Reflection and Refraction of Light",
            "B": "Thunderstorms",
            "C": "High Winds",
            "D": "Snowstorms"
        },
        "correct_answer": "A"
    }
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
        user_id = ctx.author.id
        weather_report = (
            f"**The Weather in {location['name']}, {location['country']}:**\n"
            f"The Condition is {current['condition']['text']}"
            f" with a Temperature of "
            f"***{current['temp_f']}°F***" if ((user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences) else f"***{current['temp_c']}°C***"
            f" but really Feels Like "
            f"***{current['feelslike_f']}°F***" if ((user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences) else f"***{current['feelslike_c']}°C***.\n"
            f"In the other hand, Humidity is in ***{current['humidity']}%***"
            f" and the Wind Speed is ***{current['wind_mph']} mph***.\n\n"
            f"**Ask me for any City!**\n\n"
            f"**Weather Cat Illustration:**"
        )


        #This will choose a random greeting from the stack
        greeting = random.choice(greeting_English).format(user=ctx.author.name)
        await ctx.send(f"{greeting}\n{weather_report}")

        weather_image = await generate_weather_image(current['condition']['text'] + ", in " + location['name'] + ", " + location['country'])
        with io.BytesIO() as image_binary:
            weather_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=nextcord.File(fp=image_binary, filename='weather.png'))

        condition = current['condition']['text']

        # Send weather tips if enabled
        if user_weather_tips.get(ctx.author.id, False):
            tip = weather_tips.get(condition, "No tips available for this weather condition.")
            await ctx.send(f"**1. Weather Tip:** {tip}")
        else:
            await ctx.send(f"**1. (Activate Weather Tips with !weatherTips on)**\n")

        # Send clothing suggestion
        clothing = clothing_suggestions.get(condition, "No specific clothing recommendation for this weather condition.")
        await ctx.send(f"**2. Clothing Suggestion:** {clothing}")

    except Exception as e:
        await ctx.send("**2.** An error occurred while fetching the weather data. Please contact technical support")
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
                    # Convert temperature based on user preference
                    f" with a Temperature of "
                    f"***{current['temp_f']}°F***" if (user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences else f"***{current['temp_c']}°C***"
                    f" but really Feels Like "
                    f"***{current['feelslike_f']}°F***" if (user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences else f"***{current['feelslike_c']}°C***.\n"
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

                            user_id = ctx.author.id  # Assuming ctx is defined elsewhere
                            weather_report = (
                                f"**The Weather in {location['name']}, {location['country']}:**\n"
                                f"The Condition is {current['condition']['text']}"
                                # Convert temperature based on user preference
                                f" with a Temperature of "
                                f"***{current['temp_f']}°F***" if (user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences else f"***{current['temp_c']}°C***"
                                f" but really Feels Like "
                                f"***{current['feelslike_f']}°F***" if (user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences else f"***{current['feelslike_c']}°C***.\n"
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

        user_id = ctx.author.id 
        weather_report = (
            f"**El clima en {location['name']}, {location['country']}:**\n"
            f"La condición es {current['condition']['text']}"
            # Convert temperature based on user preference
            f" con una temperatura de "
            "***{current['temp_f']}°F***" if (user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences else f"***{current['temp_c']}°C***"
            f" pero se siente como "
            f"***{current['feelslike_f']}°F***" if (user_id in user_preferences and user_preferences[user_id] == 'F') or not user_preferences else f"***{current['feelslike_c']}°C***.\n"
            f"Por otro lado, la humedad es del ***{current['humidity']}%***"
            f" y la velocidad del viento es de ***{current['wind_mph']} mph***.\n\n"
            f"**¡Pregúntame por cualquier ciudad!**"
        )


        #This will choose a random greeting from the stack
        greeting = random.choice(greeting_Spanish).format(user=ctx.author.name)
        await ctx.send(f"{greeting}\n{weather_report}")
    except Exception as e:
        await ctx.send("Se produjo un error al obtener los datos meteorológicos. Por favor, contactar a soporte tecnico")
        print(e)


# Command to get air quality information
@bot.command(name='air_quality')
async def get_air_quality(ctx):
    try:
        if ctx.author.id not in user_cities:
            await ctx.send("Your city information is not saved. Please use `!get_location` to save it.")
            return
        
        city = user_cities[ctx.author.id]
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=yes"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            await ctx.send(f"Could not fetch air quality information for {city}.")
            return

        current = data["current"]
        
        # Check if air quality data is available
        if "air_quality" not in current:
            await ctx.send(f"No air quality data available for {city}.")
            return
        
        aqi = current["air_quality"]
        
        # Extract air quality parameters
        co = aqi.get("co", "N/A")
        o3 = aqi.get("o3", "N/A")
        no2 = aqi.get("no2", "N/A")
        so2 = aqi.get("so2", "N/A")
        pm2_5 = aqi.get("pm2_5", "N/A")
        pm10 = aqi.get("pm10", "N/A")
        us_epa_index = aqi.get("us-epa-index", "Unknown")
        
        # Mapping of US EPA Index to description
        index_description = {
            1: "Good",
            2: "Moderate",
            3: "Unhealthy for Sensitive Groups",
            4: "Unhealthy",
            5: "Very Unhealthy",
            6: "Hazardous"
        }
        
        # Get description based on US EPA index
        index_description_text = index_description.get(us_epa_index, "Unknown")

        # Construct air quality information message
        message = (
            f"Air Quality in {city}:\n"
            f"- Carbon Monoxide (CO): {co} μg/m³\n"
            f"- Ozone (O3): {o3} μg/m³\n"
            f"- Nitrogen Dioxide (NO2): {no2} μg/m³\n"
            f"- Sulphur Dioxide (SO2): {so2} μg/m³\n"
            f"- PM2.5: {pm2_5} μg/m³\n"
            f"- PM10: {pm10} μg/m³\n"
            f"- US EPA Index: {us_epa_index} ({index_description_text})"
        )

        await ctx.send(message)

    except Exception as e:
        await ctx.send(f"An error occurred while fetching air quality data: {e}")


# Background task to fetch and send weather-related news every 1 minute
@tasks.loop(minutes=1)
async def fetch_weather_news():
    try:
        url = f"https://newsapi.org/v2/everything?q=weather&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'ok':
            articles = data['articles']
            if articles:
                # Select a random article
                selected_article = random.choice(articles)

                # Construct the message to send
                news_message = f"**\n'''''WEATHER NEWS'''''\nTitle:** {selected_article['title']}\n**Description:** {selected_article['description']}\n**Read more:** {selected_article['url']}\n\n** -> You can stop the news with the command !stop_weather_news <-**"

                # Find the news channel by name
                for guild in bot.guilds:
                    for channel in guild.text_channels:
                        if channel.name == "bot-testing":
                            await channel.send(news_message)
                            return

    except Exception as e:
        print(f"An error occurred while fetching weather news: {e}")

@fetch_weather_news.before_loop
async def before_fetch_weather_news():
    await bot.wait_until_ready()  # Wait until the bot is fully ready

    # Start the task immediately upon bot startup
    await asyncio.sleep(5)  # Wait a few seconds to ensure other parts of the bot are ready

# Function to find a channel by name or any other criteria
def find_channel_by_name(bot, channel_name):
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.name == channel_name and isinstance(channel, nextcord.TextChannel):
                return channel
    return None

# Command to start the weather news fetching task
@bot.command(name='start_weather_news')
async def start_weather_news(ctx):
    fetch_weather_news.start()
    await ctx.send("Fetching weather news every minute...")

# Command to stop the weather news fetching task
@bot.command(name='stop_weather_news')
async def stop_weather_news(ctx):
    fetch_weather_news.stop()
    await ctx.send("Stopped fetching weather news.")


# Command to get sunrise and sunset times
@bot.command(name='sun_times')
async def get_sun_times(ctx, *, city: str):
    try:
        url = f"http://api.weatherapi.com/v1/astronomy.json?key={API_KEY}&q={city}"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            await ctx.send(f"Error: {data['error']['message']}")
            return

        location = data['location']
        astronomy = data['astronomy']['astro']

        sunrise = astronomy['sunrise']
        sunset = astronomy['sunset']

        await ctx.send(f"Sunrise time in {location['name']}, {location['country']}: {sunrise}\n"
                       f"Sunset time in {location['name']}, {location['country']}: {sunset}")

    except Exception as e:
        await ctx.send(f"An error occurred while fetching sunrise and sunset times: {e}")


# Command to get weekly weather forecast
@bot.command(name='weekly_weather')
async def get_weekly_weather(ctx, *, city: str):
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            await ctx.send(f"Error: {data['error']['message']}")
            return

        location = data['location']
        forecast = data['forecast']['forecastday']

        summary = []
        for day in forecast:
            date = day['date']
            condition = day['day']['condition']['text']

             # Convert temperature based on user preference
            user_id = ctx.author.id
            if user_id in user_preferences and user_preferences[user_id] == 'F' or not user_preferences:
                max_temp = day['day']['maxtemp_f']
                min_temp = day['day']['mintemp_f']
                summary.append(f"{date}: Max Temp: {max_temp}°F, Min Temp: {min_temp}°F, Condition: {condition}")
            else:
                max_temp = day['day']['maxtemp_c']
                min_temp = day['day']['mintemp_c']
                summary.append(f"{date}: Max Temp: {max_temp}°C, Min Temp: {min_temp}°C, Condition: {condition}")

            

        await ctx.send(f"Weekly Weather Forecast for {location['name']}, {location['country']}:\n\n" + "\n\n".join(summary))

    except Exception as e:
        await ctx.send(f"An error occurred while fetching weekly weather forecast: {e}")



# Command to get a weather-related joke using AI
def fetch_weather_joke():
    url = f'https://api.humorapi.com/jokes/search?api-key={JOKE_API_KEY}&keywords=weather'
    response = requests.get(url)
    if response.status_code == 200:
        joke_data = response.json()
        if joke_data['jokes'] and len(joke_data['jokes']) > 0:
            # Fetch a random joke from the list of jokes
            joke = joke_data['jokes'][0]['joke']
            return joke[:2000]  # Limit to 2000 characters
        else:
            return "No weather jokes available at the moment."
    else:
        return "Failed to fetch weather joke."

@bot.command(name='weather_joke')
async def get_weather_joke(ctx):
    try:
        joke = fetch_weather_joke()
        await ctx.send(f"Here's a weather-related joke for you:\n\n{joke}")
    except Exception as e:
        await ctx.send(f"An error occurred while fetching weather joke: {e}")


# Command to get a motivational quote
def fetch_quote():
    url = "https://api.quotable.io/quotes/random?limit=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            quotes_data = response.json()
            if quotes_data:
                # Get the quote from the response
                quote_data = quotes_data[0]
                quote = quote_data.get('content', "Error.")
                author = quote_data.get('author', "Unknown")
                return f"\"{quote}\" - {author}"
            else:
                return "No quotes available at the moment."
        else:
            return "Failed to fetch quote."
    except Exception as e:
        return f"An error occurred while fetching quote: {e}"

@bot.command(name='get_quote')
async def get_weather_quote(ctx):
    try:
        quote = fetch_quote()
        await ctx.send(f"Here's an inspiring quote for you:\n\n{quote}")
    except Exception as e:
        await ctx.send(f"An error occurred while fetching quote: {e}")


# Command to start the weather quiz
@bot.command(name='weather_quiz')
async def weather_quiz_command(ctx):
    try:
        await ctx.send("Welcome to the Weather Quiz! Answer the following questions with the corresponding letter:\n")

        score = 0
        total_questions = len(weather_quiz)
        index = 0

        # Shuffle the quiz questions to randomize order
        random.shuffle(weather_quiz)

        # Iterate through each question in the shuffled quiz
        for question_data in weather_quiz:
            question = question_data["question"]
            answers = list(question_data["answers"].items())
            correct_answer = question_data["correct_answer"]

            # Format the question and shuffled answers
            question_text = f"{index + 1}. {question}\n"
            options_text = "\n".join([f"{key}. {value}" for key, value in answers])

            # Send the question and options to the user
            message = await ctx.send(f"{question_text}\n{options_text}")

            # Function to check if the user's response is correct
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.upper() in question_data["answers"]

            try:
                # Wait for the user's response
                response = await bot.wait_for('message', check=check, timeout=30.0)
                user_answer = response.content.strip().upper()

                # Check if the answer is correct
                if user_answer == correct_answer:
                    await ctx.send("Correct answer!\n")
                    score += 1
                else:
                    await ctx.send(f"Incorrect! The correct answer is: {correct_answer}\n")

                index += 1  # Move to the next question

            except asyncio.TimeoutError:
                await ctx.send("Time's up! The quiz has ended.")
                break  # End the quiz loop if timeout occurs

        # Calculate and display the final score
        await ctx.send(f"Quiz completed!\nYou scored {score}/{total_questions}.")

    except Exception as e:
        await ctx.send(f"An error occurred during the quiz: {e}")


#Command to show just the temperaute of a given city
@bot.command(name='currenttemp', aliases=['ct'])
async def current_temperature(ctx, *, city: str):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            await ctx.send(f"City {city} not found.")
            return

        location = data["location"]
        current = data["current"]

        temperature_f = current['temp_f']
        temperature_c = current['temp_c']

        # Convert temperature based on user preference
        user_id = ctx.author.id
        if user_id in user_preferences and user_preferences[user_id] == 'F' or not user_preferences:
            temperature_display = f"**{temperature_f}°F**"
        else:
            temperature_display = f"**{temperature_c}°C**"

        # Create an embed message with the temperature
        embed = discord.Embed(
            title=f"Current Temperature in {location['name']}, {location['country']}",
            description=temperature_display,
            color=discord.Color.blue()  # Sets the embed color to blue
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred while fetching the weather data: {e}")


#Command to change the format of the temperature between F to C
@bot.command(name='toggletemp')
async def toggle_temperature(ctx):
    user_id = ctx.author.id
    if user_id in user_preferences and user_preferences[user_id] == 'C':
        user_preferences[user_id] = 'F'
        await ctx.send("Temperature preference changed to Fahrenheit (°F).")
    else:
        user_preferences[user_id] = 'C'
        await ctx.send("Temperature preference changed to Celsius (°C).")


#Command to show the leaderboard for the server based on user activity
@bot.command(name='leaderboard')
async def leaderboard(ctx):
    # Sort users by activity (messages sent)
    sorted_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)

    # Prepare leaderboard message
    leaderboard_msg = "**Leaderboard - Top 5 Users by Messages Sent:**\n"
    for idx, (user_id, message_count) in enumerate(sorted_users[:5]):
        user = bot.get_user(user_id)
        leaderboard_msg += f"{idx + 1}. {user.display_name}: {message_count} messages\n"

    await ctx.send(leaderboard_msg)



#Command to play music in the voice channel
@bot.command(name = "join")
async def play(ctx):
    voice_channel = ctx.author.voice.channel
    if voice_channel:
        try:
            vc = await voice_channel.connect()

            #Please follow the instructions here to install FFmpeg (sound player): https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg
            source = nextcord.FFmpegPCMAudio('audio.mp3')
            player = vc.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

            print(f'Playing audio in {voice_channel.name}...')
            
            # Wait for the audio to finish playing
            while vc.is_playing():
                await asyncio.sleep(1)
            
            print('Audio playback finished.')

        except nextcord.ClientException as e:
            await ctx.send(f'An error occurred: {e}')
        except nextcord.HTTPException as e:
            await ctx.send(f'HTTP error occurred: {e}')
        except nextcord.InvalidArgument as e:
            await ctx.send(f'Invalid argument: {e}')
        except Exception as e:
            await ctx.send(f'Unexpected error occurred: {e}')
            print(e)
        finally:
            if vc and vc.is_connected():
                await vc.disconnect()
                print(f'Disconnected from {voice_channel.name}.')
    else:
        await ctx.send('You need to be in a voice channel to use this command.')

#Command to leave the voice channel
@bot.command(name = "leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()  # Disconnect from voice channel
    else:
        await ctx.send("Bot is not connected to a voice channel.")


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
        "`!shutdown` - Disconnects the bot and shuts it down.",
        "`!air_quality` - Shows the air quality in your saved.",
        "`!start_weather_news` - Fetch weather news to show in the chat.",
        "`!stop_weather_news` - Stops showing new weather news.",
        "`!sun_times <city>` - Get the sunset and sunrise times for a location.",
        "`!weekly_weather <city>` - Get the weekly forectas weather for a location for the next 3 days.",
        "`!weather_joke` - Get some random joke related to the weather.",
        "`!get_quote` - Get some motivational quote to start the day.",
        "`!weather_quiz` - Participate in a weather quiz!.",
        "`!currenttemp <city>` - Get the current temperature of a given city.",
        "`!toggletemp` - Change the default temperature format (F/C).",
        "`!leaderboard` - Show the leaderboard for the server based on user activity.",
        "`!join` - Join the bot to the voice channel and play music.",
        "`!leave` - Make the bot leave the voice channel.",
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

@bot.command(name='shutdown')
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    shutdownMessage = random.choice(shutdown_Message)
    await ctx.send(f"{shutdownMessage}")
    # Give some time for the message to be sent before shutting down
    await asyncio.sleep(2)
    await ctx.bot.close()

    
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

#Server and network stats every 15s
@tasks.loop(minutes=0.25)
async def update_stats():
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    net_io = psutil.net_io_counters()

    print(f"CPU Usage: {cpu_percent}% | Memory Usage: {mem_percent}% | Disk Usage: {disk_percent}%")
    print(f"Network Bytes Sent: {net_io.bytes_sent} bytes | Network Bytes Received: {net_io.bytes_recv} bytes\n***************************\n")




# 6th Step: Let's run the bot--------------------------------------------------------------------------------------------
try:
    # Checks if Bot Token is working or valid
    if API_BOT is None:
        raise ValueError("Issue with Discord Token:\nEither check credentials or reset token on the developer portal.")
    bot.run(API_BOT)
except ValueError as e:
    print(e)
