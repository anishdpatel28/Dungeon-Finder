import discord
from src.client.ucommands import get_username, get_pfp


# Simple message embed
async def simple_embed(title, message_content):
  # Title and description
  embed = discord.Embed(title=title,
                        description=message_content,
                        color=discord.Color.blue())

  # Set the footer of the embed with the avatar URL
  embed.set_footer(text=f"by {await get_username(444295171434217473)}",
                   icon_url=await get_pfp(444295171434217473))

  return embed


# Unsuccessful message embed
async def unsuccessful(ign, username):
  # Title and description
  msg = "The player `{}` has not linked their Discord account to their Hypixel account.\n"
  msg += "Join Hypixel and follow these steps to set your Discord link:"
  embed = discord.Embed(title="Verification Required",
                        description=msg.format(ign),
                        color=discord.Color.red())

  # Instructions
  items = [
    "Click on `My Profile (Right Click)` in a Hypixel lobby",
    "Click on `Social Media`", "Left-click on `Discord`",
    "Paste this in the Minecraft ingame chat: `{}`".format(username)
  ]
  numbered_list = "\n".join(
    [f"{index}. {item}" for index, item in enumerate(items, start=1)])
  embed.add_field(name="", value=numbered_list, inline=False)

  # Gif with instructions
  gif_url = "https://media.discordapp.net/attachments/922202066653417512/1066476136953036800/tutorial.gif?width=800&height=450"
  embed.set_image(url=gif_url)

  # Set the footer of the embed with the avatar URL
  embed.set_footer(text=f"by {await get_username(444295171434217473)}",
                   icon_url=await get_pfp(444295171434217473))

  return embed
