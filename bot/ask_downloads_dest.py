import os
from config import updateDataDict, writeJSON
from tkinter import Tk, Label, Button
from tkinter import filedialog as fd


# Ask user to specify download destination folder
def askDownloadDestFolder():
    chrome_options = None
    downloads_path = None
    # Ask user to choose the downloads destination folder
    window = Tk()
    window.title('Select Downloads Destination folder')
    window.geometry('300x300')
    lbl = Label(window, text='Select Downloads Destination folder')
    lbl.grid(column=0, row=0)
    def clicked():
        downloads_path = fd.askdirectory() # show an "Open" dialog box and return the path to the selected file
        if os.name == 'nt':  # Windows
            downloads_path = downloads_path.replace('/', '\\')
        print(downloads_path)
        window.destroy()
    btn = Button(window, text='Select Folder', command=clicked)
    btn.grid(column=0, row=1)
    window.mainloop()
    # Update init.json
    writeJSON(updateDataDict('init_data', 'downloads_dir',downloads_path), 'init')


# Main
if __name__ == '__main__':
    askDownloadDestFolder()