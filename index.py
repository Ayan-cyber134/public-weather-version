import discord
from discord.ext import commands
import aiohttp

# IQAIR API and Bot Tome
DISCORD_TOKEN = 'bot token'
IQAIR_API_KEY =  'api'

# Base URL
IQAIR_API_URL = 'https://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key=' + IQAIR_API_KEY

DEFAULT_STATE = 'Baghdad'  # default state
DEFAULT_COUNTRY = 'Iraq'   # default country

# Set command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to fetch data from IQAir
async def fetch_iqair_data(city, state, country):
    url = IQAIR_API_URL.format(city=city, state=state, country=country)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

# Format the data in a fancy embed style
def format_iqair_data(data):
    if 'data' not in data:
        return "No data found for the specified location."

    location = f"{data['data']['city']}, {data['data']['state']}, {data['data']['country']}"
    current = data['data']['current']
    
    weather = current['weather']
    pollution = current['pollution']

    embed = discord.Embed(
        title=f"Air Quality & Weather in {location}",
        color=discord.Color.blue()
    )
    embed.add_field(name="🌡️ Temperature", value=f"{weather['tp']}°C", inline=True)
    embed.add_field(name="💨 Humidity", value=f"{weather['hu']}%", inline=True)
    embed.add_field(name="🌬️ Wind Speed", value=f"{weather['ws']} m/s", inline=True)
    embed.add_field(name="🌫️ AQI (US)", value=pollution['aqius'], inline=True)
    embed.add_field(name="🗓️ Updated", value=pollution['ts'], inline=False)
    embed.set_footer(text="Data provided by IQAir")
    return embed

# Command to fetch weather and air quality data
@bot.command()
async def weather(ctx, *args):
    """
    Fetch weather and air quality data.
    :param args: City name, optional state, and country
    """
    # Combine all arguments into a single city string
    city = " ".join(args[:-2]) if len(args) > 2 else args[0]
    state = args[-2] if len(args) > 1 else DEFAULT_STATE
    country = args[-1] if len(args) > 1 else DEFAULT_COUNTRY

    await ctx.send(f"Fetching data for {city}, {state}, {country}...")
    
    data = await fetch_iqair_data(city, state, country)
    if data and 'error' not in data:
        embed = format_iqair_data(data)
        await ctx.send(embed=embed)
    else:
        error_message = data.get('error', "Failed to fetch data. Please check your input or try again later.")
        await ctx.send(f"❌ {error_message}")

# Error handler for incorrect command usage
@weather.error
async def weather_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            embed=discord.Embed(
                title="❌ Incorrect Command Usage",
                description="Please use the command in the following format:\n"
                            "`:weather <city>` or `:weather <city> <state> <country>`",
                color=discord.Color.red()
            )
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            embed=discord.Embed(
                title="❌ Invalid Argument",
                description="Please provide valid arguments for the command.",
                color=discord.Color.red()
            )
        )
    else:
        await ctx.send(
            embed=discord.Embed(
                title="❌ Error",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
        )

# bot startup
bot.run(DISCORD_TOKEN)
