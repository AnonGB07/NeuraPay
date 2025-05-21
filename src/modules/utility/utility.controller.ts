import { Controller, Get, Post, Query, Body, UseGuards } from '@nestjs/common';
import { UtilityService } from './utility.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { User } from '../../common/decorators/user.decorator';

@Controller('utilities')
@UseGuards(JwtAuthGuard)
export class UtilityController {
  constructor(private readonly utilityService: UtilityService) {}

  @Get('available')
  async getAvailableUtilities(@Query('country') country: string) {
    return this.utilityService.getAvailableUtilities(country);
  }

  @Post('validate')
  async validateBill(@User('id') userId: number, @Body('billId') billId: string) {
    return this.utilityService.validateBill(billId, userId);
  }
}
