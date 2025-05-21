import { Controller, Get, Post, Query, Body, UseGuards } from '@nestjs/common';
import { SubscriptionService } from './subscription.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { User } from '../../common/decorators/user.decorator';

@Controller('subscriptions')
@UseGuards(JwtAuthGuard)
export class SubscriptionController {
  constructor(private readonly subscriptionService: SubscriptionService) {}

  @Get('available')
  async getAvailableSubscriptions(@Query('country') country: string, @Query('type') type: 'airtime' | 'data' | 'tv') {
    return this.subscriptionService.getAvailableSubscriptions(country, type);
  }

  @Post('purchase')
  async purchaseSubscription(
    @User('id') userId: number,
    @Body('subscriptionId') subscriptionId: string,
    @Body('type') type: 'airtime' | 'data' | 'tv',
    @Body('provider') provider: string,
  ) {
    return this.subscriptionService.purchaseSubscription(userId, subscriptionId, type, provider);
  }
}
