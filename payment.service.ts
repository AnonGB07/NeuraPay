import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Payment } from './payment.entity';
import Stripe from 'stripe';
import CoinGate from 'coingate';
import { config } from '../../config/config';
import { RedisService } from '../../common/services/redis.service'; // New import

@Injectable()
export class PaymentService {
  private stripe: Stripe;
  private coingate: CoinGate;

  constructor(
    @InjectRepository(Payment)
    private paymentRepository: Repository<Payment>,
    private redisService: RedisService, // Inject RedisService
  ) {
    this.stripe = new Stripe(config.stripeKey, { apiVersion: '2023-10-16' });
    this.coingate = new CoinGate(config.coingateKey);
  }

  async topUp(userId: number, amount: number, method: 'crypto' | 'bank') {
    // Cache user balance check
    const cacheKey = `user:${userId}:balance`;
    let balance = await this.redisService.get(cacheKey);
    if (!balance) {
      balance = '0'; // Assume initial balance; replace with actual logic
      await this.redisService.set(cacheKey, balance, 3600); // Cache for 1 hour
    }

    let paymentIntent;
    if (method === 'bank') {
      paymentIntent = await this.stripe.paymentIntents.create({
        amount: amount * 100,
        currency: 'usd',
        payment_method_types: ['card'],
      });
    } else {
      paymentIntent = await this.coingate.createOrder({
        order_id: `order_${userId}_${Date.now()}`,
        price_amount: amount,
        price_currency: 'USD',
        receive_currency: 'BTC',
      });
    }

    const payment = this.paymentRepository.create({
      userId,
      amount,
      method,
      status: 'pending',
      transactionId: paymentIntent.id,
    });
    await this.paymentRepository.save(payment);

    // Update cached balance
    await this.redisService.set(cacheKey, (parseFloat(balance) + amount).toString(), 3600);

    return paymentIntent;
  }

  async payUtilityBill(userId: number, billId: string, amount: number) {
    const response = await fetch('https://api.reloadly.com/bill-payment', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.reloadlyKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ billId, amount, userId }),
    });

    if (!response.ok) {
      throw new HttpException('Utility payment failed', HttpStatus.BAD_REQUEST);
    }

    const payment = this.paymentRepository.create({
      userId,
      amount,
      method: 'utility',
      status: 'completed',
      transactionId: billId,
    });
    await this.paymentRepository.save(payment);
    return payment;
  }

  async bookFlight(userId: number, flightDetails: any) {
    const response = await fetch('https://api.amadeus.com/v2/shopping/flight-offers', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.amadeusKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(flightDetails),
    });

    if (!response.ok) {
      throw new HttpException('Flight booking failed', HttpStatus.BAD_REQUEST);
    }

    const flight = await response.json();
    const payment = this.paymentRepository.create({
      userId,
      amount: flightDetails.price,
      method: 'flight',
      status: 'completed',
      transactionId: flight.id,
    });
    await this.paymentRepository.save(payment);
    return payment;
  }

  async purchaseSubscription(userId: number, subscriptionId: string, amount: number, type: 'airtime' | 'data' | 'tv') {
    const response = await fetch('https://api.reloadly.com/subscription-payment', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.reloadlyKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ subscriptionId, amount, userId, type }),
    });

    if (!response.ok) {
      throw new HttpException(`${type} purchase failed`, HttpStatus.BAD_REQUEST);
    }

    const payment = this.paymentRepository.create({
      userId,
      amount,
      method: type,
      status: 'completed',
      transactionId: subscriptionId,
    });
    await this.paymentRepository.save(payment);
    return payment;
  }

  async fundBetting(userId: number, bettingAccountId: string, amount: number, platform: string) {
    const apiKey = platform === 'betway' ? config.betwayKey : config.sportpesaKey;
    const response = await fetch(`https://api.${platform}.com/fund-account`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ accountId: bettingAccountId, amount, userId }),
    });

    if (!response.ok) {
      throw new HttpException('Betting funding failed', HttpStatus.BAD_REQUEST);
    }

    const payment = this.paymentRepository.create({
      userId,
      amount,
      method: 'betting',
      status: 'completed',
      transactionId: bettingAccountId,
    });
    await this.paymentRepository.save(payment);
    return payment;
  }
}
