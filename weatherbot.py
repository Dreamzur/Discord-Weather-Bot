import nextcord
from nextcord.ext import commands
from config import TOKEN, API_KEY
import aiohttp

bot = commands.Bot(command_prefix="!", intents = nextcord.Intents.all())

#this is a test