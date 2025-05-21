import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UtilityService } from './utility.service';
import { UtilityController } from './utility.controller';
import { Utility } from './utility.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Utility])],
  controllers: [UtilityController],
  providers: [UtilityService],
})
export class UtilityModule {}
