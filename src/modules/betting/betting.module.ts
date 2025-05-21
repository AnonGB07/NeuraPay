import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BettingService } from './betting.service';
import { BettingController } from './betting.controller';
import { Betting } from './betting.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Betting])],
  controllers: [BettingController],
  providers: [BettingService],
})
export class BettingModule {}
