import json, os, sys
from pathlib import Path
from tkinter import Tk, Label, Text, Button, END
from ask_directory import askForDirectory

# Data
user_data = {
    'name': 'user_data',
    'description': 'User Data',
    'BuilderTrend Username': None,
    'BuilderTrend Password': None,
    'Downloads Directory': None,
    'Qty Images Per Daily Log': None
}

login_data = {
    'name': 'login_data',
    'description': 'Login Data',
    'login_url': 'https://buildertrend.net/',
}

chromedriver_data = {
    'name': 'chromedriver_data',
    'description': 'Chromedriver Data',
    'version': 100,
    'directory': '/chromedrivers/'  # This needs to be relative to the bot.py file
}


# Update a data dict value
def updateDataDict(dict_name: str, key, value):
    globals()[dict_name][key] = value
    return globals()[dict_name]


# Get a data value
def getDataValue(data_dict_name: str, key: str):
    data_dict = JSONtoDict(str(Path(os.path.dirname(__file__)).parent.absolute()) + '/data/' + data_dict_name + '.json')
    if data_dict:
        return data_dict[key]
    elif globals()[data_dict_name]:
        return globals()[data_dict_name][key]
    else:
        raise ValueError('No data exists for data_dict_name: ' + data_dict_name)


# Write a JSON from dict
def writeJSON(data_dict: dict, filename: str, user_enter_all: bool):
    # Look through dict for null values
    if user_enter_all:
        info_needed = True
    else:
        info_needed = False
        for key in data_dict:
            if data_dict[key] is None:
                info_needed = True
                break
    while info_needed:
        info_needed = False
        for key in data_dict:
            if (data_dict[key] is None or user_enter_all) and (key != 'description' and key != 'name'):
                if key.lower().find('directory') > -1:  # If the key needs a path to a directory
                    data_dict[key] = askForDirectory('Downloads Directory', data_dict[key])
                else:  # Ask for text input for all other keys
                    window = Tk()
                    window.title(data_dict['description'] + ' | ' + key)
                    window.geometry('400x100')
                    lbl = Label(window, text='Please enter ' + key + ': ')
                    txt = Text(window, height = 1, width = 100)
                    txt.insert(END, data_dict[key]) if data_dict[key] is not None else ''
                    def setInput(e):
                        input = txt.get('1.0', 'end-1c').replace('\n', '')
                        if input:
                            try:
                                input = int(input)
                            except:
                                pass
                            data_dict[key] = input
                            window.destroy()
                    window.bind('<Return>', setInput)  # Bind Enter button to setInput()
                    btn = Button(window, text='Submit', command=lambda:setInput(''))
                    lbl.pack()
                    txt.pack()
                    btn.pack()
                    window.state('zoomed')  # Maximize tk window
                    txt.focus()
                    window.mainloop()
            if data_dict[key] is None or data_dict[key] == '':
                info_needed = True
        user_enter_all = False

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
    user_json_data = JSONtoDict(str(Path(os.path.dirname(__file__)).parent.absolute()) + '/data/user_data.json')
    if user_json_data is None:
        writeJSON(user_data, 'user_data', True)
    else:
        user_data = user_json_data
        user_data_string = ''
        for key in user_data:
            if key == 'name':
                pass
            elif key == 'description':
                user_data_string += user_data[key] + '\n\n'
            else:
                user_data_string += key + ':   ' + str(user_data[key]) + '\n\n'
        window = Tk()
        window.title('User Data')
        data_lbl = Label(window, text=user_data_string)
        lbl = Label(window, text='\nWould you like to reset your data?')
        def yes():
            window.destroy()
            writeJSON(data_dict=user_data, filename='user_data', user_enter_all=True)
        def no(*args):
            sys.exit()
        yes_btn = Button(window, text='Yes', command=yes)
        no_btn = Button(window, text='No', command=no)
        data_lbl.pack()
        lbl.pack()
        yes_btn.pack()
        no_btn.pack()
        no_btn.focus()
        window.bind('<Return>', no)  # Bind Enter button to no()
        window.state('zoomed')  # Maximize tk window
        window.mainloop()