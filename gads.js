const nodemailer = require('nodemailer');
const fs = require('fs').promises;
const path = require('path');
const prompt = require('prompt');
const log4js = require('log4js');

// Configure logging to both file and console
log4js.configure({
  appenders: {
    file: { type: 'file', filename: 'email_sender.log' },
    console: { type: 'console' }
  },
  categories: { default: { appenders: ['file', 'console'], level: 'info' } }
});
const logger = log4js.getLogger();

class EmailSender {
  constructor(smtpConfig, maxConnections = 5) {
    this.smtpConfig = smtpConfig;
    this.maxConnections = maxConnections;
    this.sentCount = 0;
    this.failedCount = 0;
    this.priorityMap = {
      1: '1 (High)',  // High priority
      2: '3 (Normal)', // Normal priority
      3: '5 (Low)'   // Low priority
    };
    this.transporter = null;
    logger.info(`Initialized EmailSender with SMTP configuration for ${smtpConfig.username}`);
  }

  async initializeTransporter() {
    logger.info('Validating SMTP configuration');
    if (!this.smtpConfig.host || !this.smtpConfig.port || !this.smtpConfig.username || !this.smtpConfig.password) {
      logger.error('Invalid SMTP config: missing required fields');
      throw new Error('SMTP config must include host, port, username, and password');
    }
    if (![465, 587].includes(this.smtpConfig.port)) {
      logger.error(`Invalid SMTP port ${this.smtpConfig.port}: must be 465 or 587`);
      throw new Error('SMTP port must be 465 or 587');
    }
    logger.info('SMTP configuration validated successfully');

    logger.info(`Creating SMTP transporter for ${this.smtpConfig.username} on port ${this.smtpConfig.port}`);
    this.transporter = nodemailer.createTransport({
      host: this.smtpConfig.host,
      port: this.smtpConfig.port,
      secure: this.smtpConfig.port === 465, // true for 465 (SSL/TLS), false for 587 (STARTTLS)
      auth: {
        user: this.smtpConfig.username,
        pass: this.smtpConfig.password
      },
      pool: true,
      maxConnections: this.maxConnections
    });
    try {
      await this.transporter.verify();
      logger.info(`SMTP connection verified for ${this.smtpConfig.username} on port ${this.smtpConfig.port} (${this.smtpConfig.port === 465 ? 'SSL/TLS' : 'STARTTLS'})`);
    } catch (error) {
      logger.error(`Failed to verify SMTP connection for ${this.smtpConfig.username}: ${error.message}`);
      throw error;
    }
  }

  async readHtmlTemplate(filePath) {
    logger.info(`Reading HTML template from ${filePath}`);
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      logger.info('Successfully read HTML template');
      return content;
    } catch (error) {
      logger.error(`Failed to read HTML template: ${error.message}`);
      throw error;
    }
  }

  async readRecipients(filePath) {
    logger.info(`Reading recipients from ${filePath}`);
    try {
      const data = await fs.readFile(filePath, 'utf-8');
      const recipients = data.split('\n').map(line => line.trim()).filter(line => line);
      logger.info(`Read ${recipients.length} recipients`);
      return recipients;
    } catch (error) {
      logger.error(`Failed to read recipients: ${error.message}`);
      throw error;
    }
  }

  async readImage(filePath) {
    logger.info(`Reading image from ${filePath}`);
    try {
      const imageData = await fs.readFile(filePath);
      logger.info('Successfully read image');
      return imageData;
    } catch (error) {
      logger.error(`Failed to read image file: ${error.message}`);
      throw error;
    }
  }

  extractUsername(email) {
    logger.info(`Extracting username from email: ${email}`);
    try {
      const username = email.split('@')[0]
        .replace(/[^\w\.\_]/g, ' ')
        .replace(/\./g, ' ')
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
        .trim();
      const result = username.length < 2 || !username.match(/\w/) ? 'Valued Customer' : username;
      logger.info(`Extracted username: ${result}`);
      return result;
    } catch (error) {
      logger.error(`Failed to extract username: ${error.message}`);
      return 'Valued Customer';
    }
  }

  async sendEmail(recipient, subject, htmlContent, sender, link, imagePath, priority) {
    const username = this.extractUsername(recipient);
    const personalizedContent = htmlContent
      .replace('{username}', username)
      .replace('{link}', link);
    logger.info(`Preparing to send email to ${recipient}`);

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
      await this.transporter.sendMail(mailOptions);
      this.sentCount++;
      logger.info(`Successfully sent email to ${recipient} with priority ${this.priorityMap[priority] || '3 (Normal)'}`);
    } catch (error) {
      this.failedCount++;
      logger.error(`Failed to send email to ${recipient}: ${error.message}`);
    }

    await new Promise(resolve => setTimeout(resolve, Math.random() * 1500 + 500));
  }

  async sendBulkEmails(recipients, subject, htmlContent, sender, link, imagePath, priority) {
    logger.info(`Starting bulk email sending to ${recipients.length} recipients with priority ${this.priorityMap[priority] || '3 (Normal)'}`);

    for (const recipient of recipients) {
      await this.sendEmail(recipient, subject, htmlContent, sender, link, imagePath, priority);
    }

    logger.info(`Bulk email sending completed. Sent: ${this.sentCount}, Failed: ${this.failedCount}`);
    this.transporter.close();
    logger.info('Closed SMTP transporter');
  }
}

async function main() {
  const smtpConfig = {
    host: 'smtp.swbwlawfirm.site', // Update to your correct SMTP host
    port: 465,
    username: 'brian@swbwlawfirm.site',
    password: 'your_app_password' // Update with correct password
  };

  logger.info('Validating file existence');
  for (const file of ['message.html', 'leads.txt', 'logo.png']) {
    try {
      await fs.access(file);
      logger.info(`File ${file} exists`);
    } catch {
      logger.error(`File ${file} does not exist`);
      return;
    }
  }

  const sender = new EmailSender(smtpConfig, 5);

  try {
    await sender.initializeTransporter();

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
    const clickableLink = 'https://www.swbwlawfirm.site'; // Update to your website
    const imagePath = 'logo.png';
    const senderEmail = 'Brian <brian@swbwlawfirm.site>'; // Update sender name

    await sender.sendBulkEmails(
      recipients,
      'Explore Our Services',
      htmlContent,
      senderEmail,
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
