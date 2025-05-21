import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Analytics } from './analytics.entity';

@Injectable()
export class AnalyticsService {
  constructor(
    @InjectRepository(Analytics)
    private analyticsRepository: Repository<Analytics>,
  ) {}

  async logTransaction(userId: number, transactionType: string, amount: number) {
    const analytics = this.analyticsRepository.create({
      userId,
      transactionType,
      amount,
      createdAt: new Date(),
    });
    await this.analyticsRepository.save(analytics);
    return analytics;
  }

  async getUserAnalytics(userId: number) {
    return this.analyticsRepository.find({ where: { userId } });
  }
}
