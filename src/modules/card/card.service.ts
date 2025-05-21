import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Card } from './card.entity';
import Stripe from 'stripe';
import { config } from '../../config/config';

@Injectable()
export class CardService {
  private stripe: Stripe;

  constructor(
    @InjectRepository(Card)
    private cardRepository: Repository<Card>,
  ) {
    this.stripe = new Stripe(config.stripeKey, { apiVersion: '2023-10-16' });
  }

  async issueVirtualCard(userId: number) {
    const card = await this.stripe.issuing.cards.create({
      currency: 'usd',
      type: 'virtual',
      cardholder: `cardholder_${userId}`,
    });

    const newCard = this.cardRepository.create({
      userId,
      cardNumber: card.last4,
      type: 'virtual',
      status: 'active',
    });
    await this.cardRepository.save(newCard);
    return newCard;
  }

  async issuePhysicalCard(userId: number, shippingAddress: string) {
    const card = await this.stripe.issuing.cards.create({
      currency: 'usd',
      type: 'physical',
      cardholder: `cardholder_${userId}`,
      shipping: { address: shippingAddress },
    });

    const newCard = this.cardRepository.create({
      userId,
      cardNumber: card.last4,
      type: 'physical',
      status: 'pending',
    });
    await this.cardRepository.save(newCard);
    return newCard;
  }
}
