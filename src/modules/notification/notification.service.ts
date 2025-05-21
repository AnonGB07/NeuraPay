import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as nodemailer from 'nodemailer';
import * as AWS from 'aws-sdk';
import { User } from '../auth/user.entity';
import { config } from '../../config/config';

@Injectable()
export class NotificationService {
  private transporter: nodemailer.Transporter;
  private sns: AWS.SNS;

  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {
    this.transporter = nodemailer.createTransport({
      host: config.email.host,
      port: config.email.port,
      auth: {
        user: config.email.user,
        pass: config.email.pass,
      },
    });
    this.sns = new AWS.SNS({
      accessKeyId: config.aws.accessKeyId,
      secretAccessKey: config.aws.secretAccessKey,
      region: config.aws.region,
    });
  }

  async sendEmail(to: string, subject: string, text: string) {
    await this.transporter.sendMail({
      from: 'no-reply@neurapay.com',
      to,
      subject,
      text,
    });
  }

  async sendPushNotification(userId: number, message: string) {
    await this.sns
      .publish({
        Message: message,
        TargetArn: `arn:aws:sns:${config.aws.region}:your_account_id:user_${userId}`,
      })
      .promise();
  }

  async notifyTransaction(userId: number, type: string, amount: number) {
    const user = await this.userRepository.findOne({ where: { id: userId } });
    const message = `Your ${type} transaction of $${amount} was successful!`;
    await this.sendEmail(user.email, `${type} Transaction Confirmation`, message);
    await this.sendPushNotification(userId, message);
  }
}
