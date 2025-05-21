import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Flight } from './flight.entity';
import { config } from '../../config/config';

@Injectable()
export class FlightService {
  constructor(
    @InjectRepository(Flight)
    private flightRepository: Repository<Flight>,
  ) {}

  async searchFlights(searchCriteria: any) {
    const response = await fetch('https://api.amadeus.com/v2/shopping/flight-offers', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.amadeusKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchCriteria),
    });

    if (!response.ok) {
      throw new HttpException('Flight search failed', HttpStatus.BAD_REQUEST);
    }

    return await response.json();
  }

  async bookFlight(userId: number, flightId: string, amount: number) {
    const flight = this.flightRepository.create({
      userId,
      flightId,
      amount,
      status: 'pending',
      createdAt: new Date(),
    });
    await this.flightRepository.save(flight);
    return flight;
  }
}
