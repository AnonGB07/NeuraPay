import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from concurrent.futures import ThreadPoolExecutor
import time
import random
import logging
import queue
import threading
from typing import List
from datetime import datetime
import re
import os

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_sender.log'),
        logging.StreamHandler()
    ]
)

class EmailSender:
    def __init__(self, smtp_configs: List[dict], max_workers: int = 5):
        """
        Initialize EmailSender with multiple SMTP configurations
        """
        self.smtp_configs = smtp_configs
        self.connection_pool = queue.Queue()
        self.max_workers = max_workers
        self.lock = threading.Lock()
        self.sent_count = 0
        self.failed_count = 0
        self.priority_map = {
            1: '1 (High)',  # High priority
            2: '3 (Normal)',  # Normal priority
            3: '5 (Low)'  # Low priority
        }
        logging.info("Initialized EmailSender with %d SMTP configurations", len(smtp_configs))

    def create_smtp_connection(self, config: dict) -> smtplib.SMTP:
        """
        Create and return SMTP connection
        """
        logging.info("Creating SMTP connection for %s", config['username'])
        try:
            context = ssl.create_default_context()
            smtp = smtplib.SMTP(config['host'], config['port'])
            smtp.starttls(context=context)
            smtp.login(config['username'], config['password'])
            logging.info("SMTP connection established for %s", config['username'])
            return smtp
        except Exception as e:
            logging.error("Failed to create SMTP connection for %s: %s", config['username'], str(e))
            return None

    def get_smtp_connection(self) -> smtplib.SMTP:
        """
        Get SMTP connection from pool or create new one
        """
        try:
            smtp = self.connection_pool.get_nowait()
            logging.info("Retrieved SMTP connection from pool")
            return smtp
        except queue.Empty:
            config = random.choice(self.smtp_configs)
            return self.create_smtp_connection(config)

    def return_smtp_connection(self, smtp: smtplib.SMTP):
        """
        Return SMTP connection to pool
        """
        logging.info("Returning SMTP connection to pool")
        self.connection_pool.put(smtp)

    def read_html_template(self, file_path: str) -> str:
        """
        Read HTML email template from file
        """
        logging.info("Reading HTML template from %s", file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                logging.info("Successfully read HTML template")
                return content
        except Exception as e:
            logging.error("Failed to read HTML template: %s", str(e))
            raise

    def read_recipients(self, file_path: str) -> List[str]:
        """
        Read recipient emails from file
        """
        logging.info("Reading recipients from %s", file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                recipients = [line.strip() for line in file if line.strip()]
                logging.info("Read %d recipients", len(recipients))
                return recipients
        except Exception as e:
            logging.error("Failed to read recipients: %s", str(e))
            raise

    def read_image(self, file_path: str) -> bytes:
        """
        Read image file for attachment
        """
        logging.info("Reading image from %s", file_path)
        try:
            with open(file_path, 'rb') as file:
                image_data = file.read()
                logging.info("Successfully read image")
                return image_data
        except Exception as e:
            logging.error("Failed to read image file: %s", str(e))
            raise

    def extract_username(self, email: str) -> str:
        """
        Extract and format username from email address
        """
        logging.info("Extracting username from email: %s", email)
        try:
            username = email.split('@')[0]
            username = re.sub(r'[^\w\.\_]', ' ', username)
            username = username.replace('.', ' ').replace('_', ' ').title()
            if len(username) < 2 or username.isspace():
                logging.info("Invalid username, defaulting to 'Valued Customer'")
                return "Valued Customer"
            logging.info("Extracted username: %s", username)
            return username.strip()
        except Exception as e:
            logging.error("Failed to extract username: %s", str(e))
            return "Valued Customer"

    def send_email(self, recipient: str, subject: str, html_content: str, sender: str, link: str, image_path: str, priority: int):
        """
        Send email to a single recipient with an attached image and priority
        """
        smtp = None
        try:
            logging.info("Preparing to send email to %s", recipient)
            smtp = self.get_smtp_connection()
            if not smtp:
                raise Exception("No SMTP connection available")

            msg = MIMEMultipart('related')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z')
            msg['X-Priority'] = self.priority_map.get(priority, '3 (Normal)')

            username = self.extract_username(recipient)
            personalized_content = html_content.replace('{username}', username).replace('{link}', link)
            logging.info("Personalized email content for %s", recipient)

            part = MIMEText(personalized_content, 'html')
            msg.attach(part)

            image_data = self.read_image(image_path)
            image = MIMEImage(image_data)
            image.add_header('Content-ID', '<logo>')
            image.add_header('Content-Disposition', 'inline', filename='logo.png')
            msg.attach(image)
            logging.info("Attached image for %s", recipient)

            smtp.send_message(msg)
            with self.lock:
                self.sent_count += 1
                logging.info("Successfully sent email to %s with priority %s", recipient, self.priority_map.get(priority, '3 (Normal)'))
            
            self.return_smtp_connection(smtp)
            smtp = None
            
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            with self.lock:
                self.failed_count += 1
                logging.error("Failed to send email to %s: %s", recipient, str(e))
        finally:
            if smtp:
                try:
                    smtp.quit()
                    logging.info("Closed SMTP connection for %s", recipient)
                except:
                    pass

    def send_bulk_emails(self, recipients: List[str], subject: str, html_content: str, sender: str, link: str, image_path: str, priority: int):
        """
        Send emails to all recipients using thread pool
        """
        logging.info("Starting bulk email sending to %d recipients with priority %s", len(recipients), self.priority_map.get(priority, '3 (Normal)'))
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.send_email, recipient, subject, html_content, sender, link, image_path, priority)
                for recipient in recipients
            ]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logging.error("Thread pool error: %s", str(e))

        logging.info("Bulk email sending completed. Sent: %d, Failed: %d", self.sent_count, self.failed_count)

def main():
    smtp_configs = [
        {
            'host': 'smtp.hostinger.com',
            'port': 465,
            'username': 'brian@swbwlawfirm.site',
            'password': 'Blacklizard10!'
        }
    ]

    logging.info("Validating file existence")
    for file in ['message.html', 'leads.txt', 'logo.png']:
        if not os.path.exists(file):
            logging.error("File %s does not exist", file)
            return

    sender = EmailSender(smtp_configs, max_workers=5)

    try:
        logging.info("Prompting for email priority")
        print("Select email priority:")
        print("1: High")
        print("2: Normal")
        print("3: Low")
        priority_input = input("Enter priority number (1, 2, or 3): ").strip()
        priority = int(priority_input) if priority_input in ['1', '2', '3'] else 2
        logging.info("Selected priority: %s", sender.priority_map.get(priority, '3 (Normal)'))

        html_content = sender.read_html_template('message.html')
        recipients = sender.read_recipients('leads.txt')
        clickable_link = 'https://www.microsoft.com'
        image_path = 'logo.png'

        sender.send_bulk_emails(
            recipients=recipients,
            subject='Explore Microsoft Services',
            html_content=html_content,
            sender='Microsoft <no-reply@microsoft.com>',
            link=clickable_link,
            image_path=image_path,
            priority=priority
        )

    except Exception as e:
        logging.error("Error in main execution: %s", str(e))

if __name__ == '__main__':
    main()
