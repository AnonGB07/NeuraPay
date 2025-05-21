import { Controller, Post, Body, UseGuards } from '@nestjs/common';
import { CardService } from './card.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { User } from '../../common/decorators/user.decorator';

@Controller('cards')
@UseGuards(JwtAuthGuard)
export class CardController {
  constructor(private readonly cardService: CardService) {}

  @Post('virtual')
  async issueVirtualCard(@User('id') userId: number) {
    return this.cardService.issueVirtualCard(userId);
  }

  @Post('physical')
  async issuePhysicalCard(@User('id') userId: number, @Body('shippingAddress') shippingAddress: string) {
    return this.cardService.issuePhysicalCard(userId, shippingAddress);
  }
}
