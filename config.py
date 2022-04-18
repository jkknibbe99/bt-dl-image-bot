import json

# Data
init_data = {
    'bot_path': 'bot.py' 
}

login_data = {
    'login_url': 'https://buildertrend.net/',
    'username': 'joshua@engelsmahomes.com',
    'password': 'Reelbassfisher1'
}

chromedriver_data = {
    'version': 100,
    'directory': '/'
}

# Main
if __name__ == '__main__':
    # Serializing json 
    json_object = json.dumps(init_data, indent = 4)
  
    # Writing to init.json
    with open("init.json", "w") as outfile:
        outfile.write(json_object)