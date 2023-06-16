import math
import requests
from src.database.db_updates import get_data


# Returns call for player's data based given IGN
def get_call(name):
  return f"https://sky.shiiyu.moe/api/v2/profile/{name}"


# Returns json data from Hypixel's API given username
def get_JSON(name):
  call = get_call(name)
  response = requests.get(call)
  if not response:
    return {"error": "Failure to request call"}
  return response.json()


# Retrieves profile data given username
def get_profile_data(name, user):
  data = dict()
  data["successful"] = False

  raw_data = get_JSON(name)
  if "error" in raw_data:
    data["cause"] = raw_data["error"]
    return data

  PROFILE_ID = ""
  profile_name = ""
  for i in raw_data["profiles"]:
    p = raw_data["profiles"][i]
    if p["current"] == True:
      PROFILE_ID = i
      profile_name = p["cute_name"]
      break
  if not PROFILE_ID:
    data["cause"] = "No profiles found"
    return data

  try:
    disc = raw_data["profiles"][PROFILE_ID]["data"]["social"]["DISCORD"]
    if str(disc) != str(user):
      data[
        "cause"] = "Your their Discord account `{}` does not match the account linked to your username `{}` on Hypixel.".format(
          user, disc)
      return data
  except:
    data["cause"] = "No Discord linked to profile"
    return data

  data["successful"] = True

  try:
    data["uuid"] = raw_data["profiles"][PROFILE_ID]["data"]["uuid"]
  except KeyError:
    pass

  try:
    data["username"] = raw_data["profiles"][PROFILE_ID]["data"]["display_name"]
  except KeyError:
    pass

  try:
    data["profile"] = profile_name
  except KeyError:
    pass

  try:
    data["cata"] = raw_data["profiles"][PROFILE_ID]["data"]["dungeons"][
      "catacombs"]["level"]["level"]
  except KeyError:
    pass

  try:
    data["secrets"] = raw_data["profiles"][PROFILE_ID]["data"]["dungeons"][
      "secrets_found"]
  except KeyError:
    pass

  try:
    data["combat"] = raw_data["profiles"][PROFILE_ID]["data"]["levels"][
      "combat"]["level"]
  except KeyError:
    pass

  try:
    data["skill_average"] = math.floor(
      raw_data["profiles"][PROFILE_ID]["data"]["average_level"] * 10) / 10
  except KeyError:
    pass

  try:
    data["weight"] = math.floor(raw_data["profiles"][PROFILE_ID]["data"]
                                ["weight"]["senither"]["overall"])
  except KeyError:
    pass

  return data


# Update user data
def upd_assign(user):
  try:
    data = get_data(user.id)
    get_profile_data(data["username"], user)
    return data
  except:
    return {}