import { Controller, Post, Body, UseGuards } from '@nestjs/common';
import { FlightService } from './flight.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { User } from '../../common/decorators/user.decorator';

@Controller('flights')
@UseGuards(JwtAuthGuard)
export class FlightController {
  constructor(private readonly flightService: FlightService) {}

  @Post('search')
  async searchFlights(@Body() searchCriteria: any) {
    return this.flightService.searchFlights(searchCriteria);
  }

  @Post('book')
  async bookFlight(
    @User('id') userId: number,
    @Body('flightId') flightId: string,
    @Body('amount') amount: number,
  ) {
    return this.flightService.bookFlight(userId, flightId, amount);
  }
}
