import json, os
from pathlib import Path

# Data
init_data = {
    'bot_path': 'bot/bot.py',
    'downloads_dir': None
}

login_data = {
    'login_url': 'https://buildertrend.net/',
    'username': 'joshua@engelsmahomes.com',
    'password': 'Reelbassfisher1'
}

chromedriver_data = {
    'version': 100,
    'directory': '/chromedrivers/'  # This needs to be relative to the bot.py file
}


# Update a data dict value
def updateDataDict(dict_name: str, key, value):
    if dict_name == 'init_data':
        init_data[key] = value
        return init_data
    else:
        raise ValueError('Have not yet implemented functions for dict_name = ' + dict_name)


# Get a data value
def getDataValue(filename: str, key):
    if filename.find('.') > -1:
        if filename.endswith('.json'):
            filepath = str(Path(os.path.dirname(__file__)).parent.absolute()) + '/data/' + filename
        else:
            raise ValueError('Invalid filename given (' + filename + ')')
    else:
        filepath = str(Path(os.path.dirname(__file__)).parent.absolute()) + '/data/' + filename + '.json'


# Write a JSON from dict
def writeJSON(data_dict: dict, filename: str):
    # Serializing json 
    json_object = json.dumps(data_dict, indent = 4)
  
    # Writing to json
    if filename.find('.') > -1:
        if filename.endswith('.json'):
            filepath = str(Path(os.path.dirname(__file__)).parent.absolute()) + '/data/' + filename
        else:
            raise ValueError('Invalid filename given (' + filename + ')')
    else:
        filepath = str(Path(os.path.dirname(__file__)).parent.absolute()) + '/data/' + filename + '.json'
    with open(filepath, 'w') as outfile:
        outfile.write(json_object)


# Get a dict from json file
def JSONtoDict(filepath: str):
    try:
        with open(filepath) as json_file:
            data_from_json = json.load(json_file)
            return data_from_json
    except FileNotFoundError:
        return None


# Main
if __name__ == '__main__':
    writeJSON(init_data, 'init')  # write init.json