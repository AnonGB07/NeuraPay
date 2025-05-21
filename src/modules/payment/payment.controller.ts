import { Controller, Post, Body, UseGuards } from '@nestjs/common';
import { PaymentService } from './payment.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { User } from '../../common/decorators/user.decorator';

@Controller('payments')
@UseGuards(JwtAuthGuard)
export class PaymentController {
  constructor(private readonly paymentService: PaymentService) {}

  @Post('topup')
  async topUp(
    @User('id') userId: number,
    @Body('amount') amount: number,
    @Body('method') method: 'crypto' | 'bank',
  ) {
    return this.paymentService.topUp(userId, amount, method);
  }

  @Post('utility')
  async payUtilityBill(@User('id') userId: number, @Body('billId') billId: string, @Body('amount') amount: number) {
    return this.paymentService.payUtilityBill(userId, billId, amount);
  }

  @Post('flight')
  async bookFlight(@User('id') userId: number, @Body('flightDetails') flightDetails: any) {
    return this.paymentService.bookFlight(userId, flightDetails);
  }

  @Post('subscription')
  async purchaseSubscription(
    @User('id') userId: number,
    @Body('subscriptionId') subscriptionId: string,
    @Body('amount') amount: number,
    @Body('type') type: 'airtime' | 'data' | 'tv',
  ) {
    return this.paymentService.purchaseSubscription(userId, subscriptionId, amount, type);
  }

  @Post('betting')
  async fundBetting(
    @User('id') userId: number,
    @Body('bettingAccountId') bettingAccountId: string,
    @Body('amount') amount: number,
    @Body('platform') platform: string,
  ) {
    return this.paymentService.fundBetting(userId, bettingAccountId, amount, platform);
  }
}
