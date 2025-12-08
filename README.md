# About project

This is a discord bot created to play music on your voice channel.

## Required permissions

1. General permissions
    - View Channels
2. Text permissions:
    - Send Messages
    - Send Messages in Threads
    - Manage Messages
    - Embed Links
    - Use Slash Commands
3. Voice permissions:
    - Connect
    - Speak

Permission integer (checksum): 277028563968

## Usage

Write '?help' on a channel that the bot can see to get description and arguments of the available commands.

## Setup

Make sure you have Python >= 3.12 installed in your environment

With uv:

```sh
uv <venv name>
```
create a python virtual environment

```sh
uv sync
```
install dependencies

```sh
uv run python main.py
```
run the bot

### Important!
Before running make sure to rename file .env.example to .env and paste the discord token there.