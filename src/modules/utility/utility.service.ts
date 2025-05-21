import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Utility } from './utility.entity';
import { config } from '../../config/config';

@Injectable()
export class UtilityService {
  constructor(
    @InjectRepository(Utility)
    private utilityRepository: Repository<Utility>,
  ) {}

  async getAvailableUtilities(country: string) {
    const response = await fetch(`https://api.reloadly.com/utilities?country=${country}`, {
      headers: { Authorization: `Bearer ${config.reloadlyKey}` },
    });

    if (!response.ok) {
      throw new HttpException('Failed to fetch utilities', HttpStatus.BAD_REQUEST);
    }

    return await response.json();
  }

  async validateBill(billId: string, userId: number) {
    const response = await fetch(`https://api.reloadly.com/bill-validation/${billId}`, {
      headers: { Authorization: `Bearer ${config.reloadlyKey}` },
    });

    if (!response.ok) {
      throw new HttpException('Invalid bill', HttpStatus.BAD_REQUEST);
    }

    const bill = await response.json();
    const utility = this.utilityRepository.create({
      userId,
      billId,
      amount: bill.amount,
      status: 'pending',
      createdAt: new Date(),
    });
    await this.utilityRepository.save(utility);
    return utility;
  }
}
