import os
from replit import db
from src.client.client_setup import client


# Updates database with corresponding data
def db_update(data, user_id):
  user_id = str(user_id)
  if user_id not in db.keys():
    db[user_id] = data
  else:
    temp = db[user_id]
    temp.update(data)
    db[user_id] = temp


# Retrieves data given user_id key
def get_data(user_id):
  return db.get(str(user_id), None)


# Saves database into a file where contents can be seen
def db_save():
  data = dict(db)
  file_path = os.path.join('src', 'database', 'db_contents.txt')
  with open(file_path, 'w') as file:
    msg = ""
    for key, value in data.items():
      msg += str(key) + " (" + str(client.get_user(int(key))) + "):\n"
      for v_key, v_value in value.items():
        msg += "    {0:20}\t{1}\n".format(v_key + ":", v_value)
      msg += "\n\n"
    file.write(msg)
