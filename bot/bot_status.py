import os, datetime
from pathlib import Path
from send_email import sendEmail

BOT_NAME = 'BuilderTrend Image Downloader'
STATUS_LOG_FILEPATH = os.path.join(Path(os.path.dirname(__file__)), 'status_log.txt')
STATUS_LOG_HEADER = BOT_NAME + ' | Status Log\n========================================='

# Add a new Status
def newStatus(message: str, error: bool):
    now = datetime.datetime.now()
    status_msg = '\n\n- ' + str(now) + ' - ' + ('ERROR: ' if error else 'STATUS: ') + message + '\n'
    # Write to status log
    with open(STATUS_LOG_FILEPATH, 'a') as f:
        f.write(status_msg)
    # Send status email
    if error:
        sendEmail(BOT_NAME+' Error', status_msg)
    else:
        sendEmail(BOT_NAME+' Success', status_msg)

# Main function (view or clear the status log)
def main():
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
    action = input('* ' + BOT_NAME + ' Status Log *\nWhat would you like to do?\n===================\nDisplay Status Log (D/d)\nClear Status Log (C/c)\n').lower()
    if action == 'd':  # Display log
        with open(STATUS_LOG_FILEPATH, 'r') as f:
            lines = f.readlines()
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
            # Print all status entries
            for line in lines:
                None if line == '\n' else print(line)
    elif action == 'c':  # Clear log
        with open(STATUS_LOG_FILEPATH, "w") as f:
            f.write(STATUS_LOG_HEADER)
        print('Status log cleared')

# Run Main function
if __name__ == '__main__':
    main()