import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { FlightService } from './flight.service';
import { FlightController } from './flight.controller';
import { Flight } from './flight.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Flight])],
  controllers: [FlightController],
  providers: [FlightService],
})
export class FlightModule {}
