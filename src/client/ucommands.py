import discord
from src.client.client_setup import client


async def get_username(user_id):
  try:
    user = await client.fetch_user(user_id)
    username = user.name
    return username
  except discord.NotFound:
    return None


async def get_pfp(user_id):
  user = await client.fetch_user(user_id)
  if user:
    return user.avatar.url
  else:
    return None
