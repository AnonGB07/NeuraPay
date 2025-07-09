import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from concurrent.futures import ThreadPoolExecutor
import time
import random
import logging
import threading
from typing import List
from datetime import datetime
import re
import os
import socket

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
    def __init__(self, smtp_config: dict, max_workers: int = 5):
        """
        Initialize EmailSender with a single SMTP configuration
        """
        self.smtp_config = smtp_config
        self.max_workers = max_workers
        self.lock = threading.Lock()
        self.sent_count = 0
        self.failed_count = 0
        self.priority_map = {
            1: '1 (High)',  # High priority
            2: '3 (Normal)',  # Normal priority
            3: '5 (Low)'  # Low priority
        }
        logging.info("Initialized EmailSender with SMTP configuration for %s", smtp_config['username'])
        self.validate_smtp_config()
        self.test_smtp_connection()

    def validate_smtp_config(self):
        """
        Validate SMTP configuration
        """
        logging.info("Validating SMTP configuration")
        required_fields = ['host', 'port', 'username', 'password']
        if not all(key in self.smtp_config for key in required_fields):
            logging.error("Invalid SMTP config: missing required fields %s", required_fields)
            raise ValueError("SMTP config must include host, port, username, and password")
        if self.smtp_config['port'] not in [465, 587]:
            logging.error("Invalid SMTP port %d: must be 465 or 587", self.smtp_config['port'])
            raise ValueError("SMTP port must be 465 or 587")
        logging.info("SMTP configuration validated successfully")

    def test_smtp_connection(self):
        """
        Test SMTP connection before sending emails
        """
        logging.info("Testing SMTP connection for %s on port %d", self.smtp_config['username'], self.smtp_config['port'])
        try:
            # Test DNS resolution
            socket.gethostbyname(self.smtp_config['host'])
            logging.info("DNS resolution successful for host %s", self.smtp_config['host'])
            
            # Test SMTP connection
            context = ssl.create_default_context()
            port = self.smtp_config['port']
            if port == 465:
                smtp = smtplib.SMTP_SSL(self.smtp_config['host'], port, context=context)
                logging.info("Established SSL/TLS connection for %s on port 465", self.smtp_config['username'])
            else:  # port 587
                smtp = smtplib.SMTP(self.smtp_config['host'], port)
                smtp.starttls(context=context)
                logging.info("Upgraded to STARTTLS connection for %s on port 587", self.smtp_config['username'])
            smtp.login(self.smtp_config['username'], self.smtp_config['password'])
            logging.info("SMTP login successful for %s", self.smtp_config['username'])
            smtp.quit()
            logging.info("SMTP test connection closed successfully")
        except socket.gaierror as e:
            logging.error("DNS resolution failed for host %s: %s", self.smtp_config['host'], str(e))
            raise ValueError(f"Cannot resolve SMTP host {self.smtp_config['host']}. Check hostname or network settings.")
        except Exception as e:
            logging.error("Failed to establish SMTP test connection: %s", str(e))
            raise ValueError(f"SMTP connection test failed: {str(e)}. Check credentials, port, or network settings.")

    def create_smtp_connection(self) -> smtplib.SMTP:
        """
        Create and return SMTP connection based on port
        """
        port = self.smtp_config['port']
        username = self.smtp_config['username']
        logging.info("Creating SMTP connection for %s on port %d", username, port)
        try:
            context = ssl.create_default_context()
            if port == 465:
                smtp = smtplib.SMTP_SSL(self.smtp_config['host'], port, context=context)
                logging.info("Established SSL/TLS connection for %s on port 465", username)
            else:  # port 587
                smtp = smtplib.SMTP(self.smtp_config['host'], port)
                smtp.starttls(context=context)
                logging.info("Upgraded to STARTTLS connection for %s on port 587", username)
            smtp.login(self.smtp_config['username'], self.smtp_config['password'])
            logging.info("SMTP login successful for %s", username)
            return smtp
        except Exception as e:
            logging.error("Failed to create SMTP connection for %s: %s", username, str(e))
            raise

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
            smtp = self.create_smtp_connection()

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
    smtp_config = {
        'host': 'smtp.hostinger.com',  # Update to your correct SMTP host
        'port': 465,
        'username': 'brian@swbwlawfirm.site',
        'password': 'Blacklizard10!'  # Update with correct password
    }

    logging.info("Validating file existence")
    for file in ['message.html', 'leads.txt', 'logo.png']:
        if not os.path.exists(file):
            logging.error("File %s does not exist", file)
            return

    try:
        sender = EmailSender(smtp_config, max_workers=5)
    except Exception as e:
        logging.error("Failed to initialize EmailSender: %s", str(e))
        return

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
        clickable_link = 'https://www.swbwlawfirm.site'  # Update to your website
        image_path = 'logo.png'
        sender_email = 'Brian <brian@swbwlawfirm.site>'  # Update sender name

        sender.send_bulk_emails(
            recipients=recipients,
            subject='Explore Our Services',
            html_content=html_content,
            sender=sender_email,
            link=clickable_link,
            image_path=image_path,
            priority=priority
        )

    except Exception as e:
        logging.error("Error in main execution: %s", str(e))

if __name__ == '__main__':
    main()
