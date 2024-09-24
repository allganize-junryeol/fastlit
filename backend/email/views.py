import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ssl
from urllib.parse import urlparse

def parse_smtp_uri(smtp_uri):
    parsed = urlparse(smtp_uri)
    username, password = parsed.username, parsed.password
    smtp_server = parsed.hostname
    smtp_port = int(parsed.port) if parsed.port else 587 # 465 587
    
    return {
        "username": username,
        "password": password,
        "ip": smtp_server,
        "port": smtp_port
    }

def send_email(receiver_email, content):
    uri = os.getenv('SMTP_URI', 'smtp://parker@vgtech.co.kr:1234@smtp.gmail.com')
    smtp_data = parse_smtp_uri(uri)
    print(smtp_data)

    # Create message object instance
    msg = MIMEMultipart()

    # Setup the parameters of the message
    msg['From'] = smtp_data['username']
    msg['To'] = receiver_email
    msg['Subject'] = ""

    msg.attach(MIMEText(content, 'plain'))
    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_data['ip'], 465) as server:
    # with smtplib.SMTP(smtp_data['ip'], 587) as server:

        # server.ehlo() # Can be omitted
        # server.starttls(context=context) # Secure the connection
        # server.ehlo() # Can be omitted
    
        server.login(smtp_data['username'], smtp_data['password'])
        # server.verify("parker@vgtech.co.kr")
        
        # Send the email
        text = msg.as_string()
        server.sendmail(smtp_data['username'], receiver_email, text)
        
        print("Email sent successfully!")
                
send_email("parker@vgtech.co.kr", "Hello, this is a test email!")