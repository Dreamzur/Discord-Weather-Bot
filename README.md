<div align="center">
<h1>Discord Weather Bot</h1>
<img border="1px" width="180" src="https://github.com/Dreamzur/Discord-Weather-Bot/assets/95004742/ea725f83-1aae-4de8-b765-074e2e286faa"/>
</div>

![Contributors](https://img.shields.io/github/contributors/Dreamzur/discord-weather-bot)
![Last Commit](https://img.shields.io/github/last-commit/Dreamzur/discord-weather-bot)

Welcome to the Discord Weather Bot! This bot provides a variety of weather-related functionalities to keep you updated on current weather conditions and forecasts. Below are the available commands and their descriptions.

## Table of Contents
- [About](#about)
- [Commands](#commands)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)

## About

This Discord Weather Bot is designed to provide accurate and timely weather updates directly within your Discord server. It uses advanced APIs to fetch current weather data and generates AI-based weather images for a more interactive experience. Whether you need to check the weather for a specific city or receive personalized updates, this bot has got you covered.

## Commands

### `!weather <city>`
Get the current weather for a specified city. The response includes an AI-generated weather image for a more visual experience.

### `!weather_me`
Receive personalized weather updates based on your saved location. Use the `!get_location` command to save your location first.

### `!weather_all`
Check the weather for all active members of the server who have saved their locations. This is a convenient way to get weather updates for everyone at once.

### `!weather_spanish <city>`
¡Obtén el clima en español para una ciudad específica! This command provides weather updates in Spanish for the specified city.

### `!get_location`
Save your current location for personalized weather updates. This location will be used for the `!weather_me` command.

### `!weatherTips [on/off]`
Toggle helpful weather tips on or off. When on, the bot will provide useful weather-related tips along with your weather updates.

### `!weatherAlerts [on/off]`
Activate or deactivate severe weather alerts. When activated, the bot will send alerts for severe weather conditions in your saved location.

### `!setWeatherUpdates <city> <interval>`
Set up regular weather updates for a specific city at a chosen interval. The interval can be specified in minutes, hours, or days.

### `!stopWeatherUpdates`
Stop receiving regular weather updates. This will cancel any scheduled updates you have set up with the `!setWeatherUpdates` command.

### `!about`
Learn more about this bot and its capabilities. This command provides an overview of the bot’s features and how to use them.

### `!shutdown`
Disconnects the bot and shuts it down. Use this command to safely turn off the bot when it's no longer needed.

## Usage Examples

- To get the current weather for London:
    ```
    !weather London
    ```

- To receive personalized weather updates:
    ```
    !weather_me
    ```

- To toggle weather tips on:
    ```
    !weatherTips on
    ```
    
## Getting Started

1. **Invite the Bot**: Invite the bot to your Discord server using the provided invitation link.
2. **Set Up Your Location**: Use the `!get_location` command to save your current location for personalized updates.
3. **Check Weather**: Use the various weather commands to check the current weather, set up regular updates, and more.
4. **Customize Alerts and Tips**: Toggle weather tips and severe weather alerts on or off as per your preference.


The bot is still under development!
