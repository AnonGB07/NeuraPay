import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Betting } from './betting.entity';
import { config } from '../../config/config';

@Injectable()
export class BettingService {
  constructor(
    @InjectRepository(Betting)
    private bettingRepository: Repository<Betting>,
  ) {}

  async getAvailableBettingPlatforms(country: string) {
    // Mocked; replace with actual API call
    return ['betway', 'sportpesa', '1xbet'];
  }

  async fundBettingAccount(userId: number, bettingAccountId: string, amount: number, platform: string) {
    const apiKey = platform === 'betway' ? config.betwayKey : config.sportpesaKey;
    const response = await fetch(`https://api.${platform}.com/validate-account/${bettingAccountId}`, {
      headers: { Authorization: `Bearer ${apiKey}` },
    });

    if (!response.ok) {
      throw new HttpException('Invalid betting account', HttpStatus.BAD_REQUEST);
    }

    const betting = this.bettingRepository.create({
      userId,
      platform,
      amount,
      transactionId: bettingAccountId,
      status: 'pending',
      createdAt: new Date(),
    });
    await this.bettingRepository.save(betting);
    return betting;
  }

  async placeBet(userId: number, betDetails: any, platform: string) {
    const apiKey = platform === 'betway' ? config.betwayKey : config.sportpesaKey;
    const response = await fetch(`https://api.${platform}.com/place-bet`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(betDetails),
    });

    if (!response.ok) {
      throw new HttpException('Bet placement failed', HttpStatus.BAD_REQUEST);
    }

    const betting = this.bettingRepository.create({
      userId,
      platform,
      amount: betDetails.amount,
      transactionId: betDetails.betId,
      status: 'completed',
      createdAt: new Date(),
    });
    await this.bettingRepository.save(betting);
    return betting;
  }
}
