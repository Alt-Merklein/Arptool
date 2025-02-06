import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from time import sleep

DEFAULT_SERVER = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587
DEBUG = 0
TIMEOUT_MINUTES = 15

class Mailer:
    def __init__(self, config: Config):
        self.config = config
        self.sender = config.config["mail"]["sender_email"]
        self.password = config.config["mail"]["sender_password"]
        self.receiver = config.config["mail"]["receiver_email"]
        self.sent = False

    def set_subject(self, subject):
        self.subject = subject
    
    def set_text_body(self, text):
        self.body = text
    
    def send_mail(self):
        if (self.sent == True):
            logging.warning("Already sent an email recently, aborting operation")
            return
        self.sent = True
        msg = MIMEMultipart()
        msg["From"] = self.sender
        msg["To"] = self.receiver
        msg["Subject"] = self.subject
        msg.attach(MIMEText(self.body, "plain"))

        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(DEFAULT_SERVER, DEFAULT_SMTP_PORT)
            print("Connected to SMTP server")
            if (DEBUG):
                server.set_debuglevel(1)
            server.starttls(context=context)
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receiver, msg.as_string())
            server.quit()
            logging.info(f"Warning email sent to admin")
        except Exception as e:
            logging.error(f"Failed to send email")

        finally:
            # Wait before being able to send other mails
            sleep(TIMEOUT_MINUTES * 60) 
            self.sent = False

if __name__ == "__main__":
    print("Started testing module mail")
    # Test
    config = Config("config.yaml")
    mailer = Mailer(config)
    mailer.set_subject("Warning about arp table")
    mailer.set_text_body("You are receiving this email because an issue has been found with the arp table. Check session logs")
    mailer.send_mail()
    print("Finished testing module mail")