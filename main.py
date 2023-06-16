import os
import discord
import asyncio
from discord.ext import commands
from src.api.urequests import get_profile_data, upd_assign
from src.client.client_setup import client
from src.client.keep_alive import keep_alive
from src.client.ucommands import get_username
from src.database.db_updates import db_update, db_save
from src.utils.messages import simple_embed, unsuccessful, rate_limit


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
@commands.cooldown(1, 5, commands.BucketType.user)
async def on_ready():
  # Initialized
  await client.change_presence(
    activity=discord.Activity(type=discord.ActivityType.watching, name="You"))
  print("We have logged on {0.user}".format(client))

  max_retries = 3  # Maximum number of retries
  retries = 0

  # Sync all commands
  while True:
    try:
      synced = await client.tree.sync()
      print("Synced {} commands".format(len(synced)))
      break  # Break the loop if synchronization is successful
    except Exception as e:
      print(e)
      retries += 1
      if retries >= max_retries:
        raise Exception(
          "Command synchronization failed after maximum retries.")
      print("Retry in 3 seconds...")
      await asyncio.sleep(3)  # Wait for 5 seconds before retrying

    print("Worked")


@client.event
@commands.cooldown(1, 5, commands.BucketType.user)
async def on_message(message):
  if message.author == client.user:
    return
  print("{}: {}".format(message.author, message.content))


@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(embed=await rate_limit(error.retry_after))


"""
Public Commands
"""


# Verify command
@client.hybrid_command(description="Verify your account")
@commands.cooldown(1, 5, commands.BucketType.user)
async def verify(message, flags: VerifyFlags):
  data = get_profile_data(flags.username, message.author)

  if not data["successful"]:
    u_embed = await unsuccessful(flags.username, message.author.name)
    await message.send(embed=u_embed)
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
@commands.cooldown(1, 60, commands.BucketType.user)
async def update(message):
  data = upd_assign(message.author)
  if not data:
    u_embed = await unsuccessful(None, message.author.name)
    await message.send(embed=u_embed)
    return
  db_update(data, message.author.id)
  s_embed = await simple_embed("Success", "Updated your user data")
  await message.send(embed=s_embed)


# Ping command
@client.hybrid_command(description="Tests the bot's response time.")
@commands.cooldown(1, 5, commands.BucketType.user)
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
    s_embed = await simple_embed("**Incorrect Channel**", "Dummy Sazzy!",
                                 discord.Color.red())
    await ctx.send(embed=s_embed)
    return
  user = client.get_user(int(user_id))
  if user is None:
    s_embed = await simple_embed("**Invalid User**", str(user_id))
    await ctx.send(embed=s_embed)
    return
  s_embed = await simple_embed(
    "**Message Sent to {}**".format(await get_username(user_id)), message)
  await ctx.send(embed=s_embed)
  await user.send(message)


# Sync command
@restrict_to_user(444295171434217473)
@client.hybrid_command(description="Sync all commands")
async def sync(message):
  try:
    synced = await client.tree.sync()
    s_embed = await simple_embed("**Success**",
                                 f"Synced {len(synced)} commands")
    await message.send(embed=s_embed)
  except Exception as e:
    s_embed = await simple_embed("**Error**", "Failure to sync commands",
                                 discord.Color.red())
    await message.send(embed=s_embed)
    print(e)


# Save current database to text file
@restrict_to_user(444295171434217473)
@client.hybrid_command(description="Save database to text file")
async def save_db(message):
  db_save()
  s_embed = await simple_embed("**Success**", "Save complete")
  await message.send(embed=s_embed)


# Retrieves current database as text file
@restrict_to_user(444295171434217473)
@client.hybrid_command(description="Retrieves database as a text file")
async def get_db(message):
  try:
    file_path = os.path.join('src', 'database', 'db_contents.txt')
    with open(file_path, 'rb') as file:
      await message.author.send(file=discord.File(file, 'db_contents.txt'))
  except FileNotFoundError:
    s_embed = await simple_embed("**Error**", "Database file not found",
                                 discord.Color.red())
    await message.send(embed=s_embed)
    return
  s_embed = await simple_embed("**Success**", "Sent")
  await message.send(embed=s_embed)


keep_alive()
client.run(os.getenv('TOKEN'))
