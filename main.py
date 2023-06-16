import os
import discord
import asyncio
from discord.ext import commands
from src.api.urequests import get_profile_data, upd_assign
from src.client.keep_alive import keep_alive
from src.client.client_setup import client
from src.database.db_updates import db_update, db_save
from src.utils.messages import simple_embed, unsuccessful


# Flags for verification
class VerifyFlags(commands.FlagConverter):
  username: str = commands.flag(description='Username')


# For user restricted commands
def restrict_to_user(user_id):

  async def predicate(ctx):
    return ctx.author.id == user_id

  return commands.check(predicate)


"""
Events
"""


@client.event
async def on_ready():
  # Initialized
  await client.change_presence(
    activity=discord.Activity(type=discord.ActivityType.watching, name="You"))
  print("We have logged on {0.user}".format(client))

  await asyncio.sleep(3)

  # Sync all commands
  try:
    synced = await client.tree.sync()
    print("Synced {} commands".format(len(synced)))
  except Exception as e:
    print(e)
    print("Worked")


@client.event
async def on_message(message):
  if message.author == client.user:
    return
  print("{}: {}".format(message.author, message.content))


"""
Public Commands
"""


# Verify command
@client.hybrid_command(description="Verify your account")
async def verify(message, flags: VerifyFlags):
  data = get_profile_data(flags.username, message.author)

  if not data["successful"]:
    u_embed = await unsuccessful(flags.username, message.author.name)
    await message.send(embed=u_embed)
    #await message.send("**Verification Unsuccessful**\n{}".format(data["cause"]))
    return

  db_update(data, message.author.id)
  msg = "Successfully linked and verified your account!\n"
  msg += "Username: `{}`\n".format(data["username"])
  msg += "Profile: `{}`".format(data["profile"])
  s_embed = await simple_embed("Success", msg)
  await message.send(embed=s_embed)

  try:
    await message.author.edit(nick=data["username"])
  except:
    print("Cannot change nickname for users with higher roles than the bot")


# Update command
@client.hybrid_command(description="Update your stats")
async def update(message):
  data = upd_assign(message.author)
  if not data:
    await message.send("**Update Unsuccessful**\nVerify first")
    return
  """
  if data["username"] != client.get_user(message.author.id):
    await message.send(
      "**Update Unsuccessful**\nDiscord username has changed\nVerify first")
    return
  """
  db_update(data, message.author.id)
  await message.send("**Updated user data**")


# Ping command
@client.hybrid_command(description="Tests the bot's response time.")
async def ping(message):
  s_embed = await simple_embed("Ping",
                               "{} ms".format(round(client.latency * 1000)))
  await message.send(embed=s_embed)


"""
Restricted Commands
"""


# Message command
@restrict_to_user(444295171434217473)
@client.hybrid_command(description="Send a message to a user")
async def send_msg(ctx, user_id: str, *, message: str):
  if not isinstance(ctx.channel, discord.DMChannel):
    return
  user = client.get_user(int(user_id))
  if user is None:
    return
  await ctx.send("**Message Sent:**\n{}".format(message))
  await user.send(message)


# Save current database to text file
@restrict_to_user(444295171434217473)
@client.hybrid_command(description="Save database to text file")
async def save_db(message):
  db_save()
  await message.send("**Saved**")


# Retrieves current database as text file
@restrict_to_user(444295171434217473)
@client.hybrid_command(description="Retrieves database as a text file")
async def get_db(message):
  try:
    with open('db_contents.txt', 'rb') as file:
      await message.author.send(file=discord.File(file, 'db_contents.txt'))
  except FileNotFoundError:
    await message.send("**Database file not found.**")
  await message.send("**Sent**")


keep_alive()
client.run(os.getenv('TOKEN'))
