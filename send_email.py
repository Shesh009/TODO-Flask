import os

from dotenv import load_dotenv  # pip install python-dotenv
load_dotenv()


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP2GO server settings
smtp_server = 'mail.smtp2go.com'
smtp_port = 2525 # SMTP2GO port number
smtp_username = os.getenv("USERNAME_SMTP")
smtp_password = os.getenv("PASSWORD_SMTP")

# Sender and recipient email addresses
sender_email = os.getenv("EMAIL_NEW")

# Email content
def send_email(subject, receiver_email, l):
    body = f'''\
        <html>
        <body>
            <p>Hello there,</p>
            <p>I hope you are well.</p>
            <p>I just wanted to drop you a quick note to remind you that the following tasks are pending which are to be completed by <strong>next 4 days</strong> .
            <br>
            <p><strong>{l}</strong></p>
            <br>
            <p>Best regards</p>
        </body>
        </html>
        '''

    # Create MIMEText object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print('Email sent successfully!')
    except Exception as e:
        print('Error sending email:', str(e))
    finally:
        server.quit()

if __name__ == "__main__":
    print(sender_email,smtp_username,smtp_password) 
    send_email(
        subject="Tasks to be done in 4 days",
        # name="John Doe",
        receiver_email="akulasheshu4@gmail.com",
        # due_date="11, Aug 2022",
        # invoice_no="INV-21-12-009",
        # amount="5",
        l='HIII sfuhsdufbieuhfu'
    )