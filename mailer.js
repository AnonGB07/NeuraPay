const nodemailer = require('nodemailer');
const fs = require('fs').promises;
const path = require('path');
const prompt = require('prompt');
const log4js = require('log4js');

// Configure logging
log4js.configure({
  appenders: { file: { type: 'file', filename: 'email_sender.log' } },
  categories: { default: { appenders: ['file'], level: 'info' } }
});
const logger = log4js.getLogger();

class EmailSender {
  constructor(smtpConfigs, maxConnections = 5) {
    this.smtpConfigs = smtpConfigs;
    this.maxConnections = maxConnections;
    this.sentCount = 0;
    this.failedCount = 0;
    this.priorityMap = {
      1: '1 (High)',  // High priority
      2: '3 (Normal)', // Normal priority
      3: '5 (Low)'   // Low priority
    };
    this.transporters = [];
  }

  async initializeTransporters() {
    for (const config of this.smtpConfigs) {
      const transporter = nodemailer.createTransport({
        host: config.host,
        port: config.port,
        secure: config.port === 465, // true for 465, false for others
        auth: {
          user: config.username,
          pass: config.password
        },
        pool: true,
        maxConnections: this.maxConnections
      });
      try {
        await transporter.verify();
        this.transporters.push(transporter);
        logger.info(`SMTP connection verified for ${config.username}`);
      } catch (error) {
        logger.error(`Failed to verify SMTP connection for ${config.username}: ${error.message}`);
      }
    }
    if (this.transporters.length === 0) {
      throw new Error('No valid SMTP connections available');
    }
  }

  async readHtmlTemplate(filePath) {
    try {
      return await fs.readFile(filePath, 'utf-8');
    } catch (error) {
      logger.error(`Failed to read HTML template: ${error.message}`);
      throw error;
    }
  }

  async readRecipients(filePath) {
    try {
      const data = await fs.readFile(filePath, 'utf-8');
      return data.split('\n').map(line => line.trim()).filter(line => line);
    } catch (error) {
      logger.error(`Failed to read recipients: ${error.message}`);
      throw error;
    }
  }

  async readImage(filePath) {
    try {
      return await fs.readFile(filePath);
    } catch (error) {
      logger.error(`Failed to read image file: ${error.message}`);
      throw error;
    }
  }

  extractUsername(email) {
    try {
      const username = email.split('@')[0]
        .replace(/[^\w\.\_]/g, ' ')
        .replace(/\./g, ' ')
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
        .trim();
      return username.length < 2 || !username.match(/\w/) ? 'Valued Customer' : username;
    } catch {
      return 'Valued Customer';
    }
  }

  async sendEmail(recipient, subject, htmlContent, sender, link, imagePath, priority) {
    const transporter = this.transporters[Math.floor(Math.random() * this.transporters.length)];
    const username = this.extractUsername(recipient);
    const personalizedContent = htmlContent
      .replace('{username}', username)
      .replace('{link}', link);

    const mailOptions = {
      from: sender,
      to: recipient,
      subject: subject,
      html: personalizedContent,
      headers: { 'X-Priority': this.priorityMap[priority] || '3 (Normal)' },
      attachments: [
        {
          filename: 'logo.png',
          content: await this.readImage(imagePath),
          cid: 'logo'
        }
      ]
    };

    try {
      await transporter.sendMail(mailOptions);
      this.sentCount++;
      logger.info(`Successfully sent email to ${recipient} with priority ${this.priorityMap[priority] || '3 (Normal)'}`);
    } catch (error) {
      this.failedCount++;
      logger.error(`Failed to send email to ${recipient}: ${error.message}`);
    }

    // Random delay to avoid spam detection
    await new Promise(resolve => setTimeout(resolve, Math.random() * 1500 + 500));
  }

  async sendBulkEmails(recipients, subject, htmlContent, sender, link, imagePath, priority) {
    logger.info(`Starting bulk email sending to ${recipients.length} recipients with priority ${this.priorityMap[priority] || '3 (Normal)'}`);

    const sendPromises = recipients.map(recipient =>
      this.sendEmail(recipient, subject, htmlContent, sender, link, imagePath, priority)
    );

    await Promise.all(sendPromises);

    logger.info(`Bulk email sending completed. Sent: ${this.sentCount}, Failed: ${this.failedCount}`);
  }
}

async function main() {
  const smtpConfigs = [
    {
      host: 'smtp.gmail.com',
      port: 587,
      username: 'your_email@gmail.com',
      password: 'your_app_password'
    }
    // Add more SMTP configurations here
  ];

  const sender = new EmailSender(smtpConfigs, 5);

  try {
    await sender.initializeTransporters();

    prompt.start();
    const schema = {
      properties: {
        priority: {
          description: 'Enter priority number (1: High, 2: Normal, 3: Low)',
          type: 'integer',
          pattern: /^[1-3]$/,
          message: 'Priority must be 1, 2, or 3',
          required: true,
          default: 2
        }
      }
    };

    const { priority } = await new Promise((resolve, reject) => {
      prompt.get(schema, (err, result) => {
        if (err) reject(err);
        else resolve(result);
      });
    });

    logger.info(`Selected priority: ${sender.priorityMap[priority] || '3 (Normal)'}`);

    const htmlContent = await sender.readHtmlTemplate('message.html');
    const recipients = await sender.readRecipients('leads.txt');
    const clickableLink = 'https://www.microsoft.com';
    const imagePath = 'logo.png';

    await sender.sendBulkEmails(
      recipients,
      'Explore Microsoft Services',
      htmlContent,
      'Microsoft <no-reply@microsoft.com>',
      clickableLink,
      imagePath,
      parseInt(priority)
    );
  } catch (error) {
    logger.error(`Error in main execution: ${error.message}`);
  }
}

// Install dependencies before running
console.log('Ensure dependencies are installed: npm install nodemailer prompt log4js');
main();
