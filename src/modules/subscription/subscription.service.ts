import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Subscription } from './subscription.entity';
import { config } from '../../config/config';

@Injectable()
export class SubscriptionService {
  constructor(
    @InjectRepository(Subscription)
    private subscriptionRepository: Repository<Subscription>,
  ) {}

  async getAvailableSubscriptions(country: string, type: 'airtime' | 'data' | 'tv') {
    const response = await fetch(`https://api.reloadly.com/subscriptions?country=${country}&type=${type}`, {
      headers: { Authorization: `Bearer ${config.reloadlyKey}` },
    });

    if (!response.ok) {
      throw new HttpException(`Failed to fetch ${type} subscriptions`, HttpStatus.BAD_REQUEST);
    }

    return await response.json();
  }

  async purchaseSubscription(userId: number, subscriptionId: string, type: 'airtime' | 'data' | 'tv', provider: string) {
    const response = await fetch(`https://api.reloadly.com/subscription-validation/${subscriptionId}`, {
      headers: { Authorization: `Bearer ${config.reloadlyKey}` },
    });

    if (!response.ok) {
      throw new HttpException(`Invalid ${type} subscription`, HttpStatus.BAD_REQUEST);
    }

    const subscriptionDetails = await response.json();
    const subscription = this.subscriptionRepository.create({
      userId,
      type,
      provider,
      amount: subscriptionDetails.amount,
      transactionId: subscriptionId,
      status: 'pending',
      createdAt: new Date(),
    });
    await this.subscriptionRepository.save(subscription);
    return subscription;
  }
}
