import smtplib, ssl
from config import getDataValue

# Send an email
def sendEmail(subject: str, message: str):
    # Create a secure SSL context
    port = 465  # For SSL
    context = ssl.create_default_context()

    # Create message string
    message_str = 'Subject: {}\n\n{}'.format(subject, message)

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        sender_email = getDataValue('status_email_data', 'sender')
        password = getDataValue('status_email_data', 'password')
        receiver_email = getDataValue('status_email_data', 'receiver')
        try:
            server.login(sender_email, password)
        except smtplib.SMTPAuthenticationError as e:
            print(e)
            print(sender_email, password)
        server.sendmail(sender_email, receiver_email, message_str)
