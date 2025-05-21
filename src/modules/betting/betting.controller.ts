import { Controller, Get, Post, Query, Body, UseGuards } from '@nestjs/common';
import { BettingService } from './betting.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { User } from '../../common/decorators/user.decorator';

@Controller('betting')
@UseGuards(JwtAuthGuard)
export class BettingController {
  constructor(private readonly bettingService: BettingService) {}

  @Get('platforms')
  async getAvailableBettingPlatforms(@Query('country') country: string) {
    return this.bettingService.getAvailableBettingPlatforms(country);
  }

  @Post('fund')
  async fundBettingAccount(
    @User('id') userId: number,
    @Body('bettingAccountId') bettingAccountId: string,
    @Body('amount') amount: number,
    @Body('platform') platform: string,
  ) {
    return this.bettingService.fundBettingAccount(userId, bettingAccountId, amount, platform);
  }

  @Post('place')
  async placeBet(@User('id') userId: number, @Body('betDetails') betDetails: any, @Body('platform') platform: string) {
    return this.bettingService.placeBet(userId, betDetails, platform);
  }
}
