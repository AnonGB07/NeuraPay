import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AuthModule } from './auth/auth.module';
import { UserModule } from './user/user.module';
import { PaymentModule } from './payment/payment.module';
import { CardModule } from './card/card.module';
import { UtilityModule } from './utility/utility.module';
import { FlightModule } from './flight/flight.module';
import { SubscriptionModule } from './subscription/subscription.module';
import { BettingModule } from './betting/betting.module';
import { NotificationModule } from './notification/notification.module';
import { AnalyticsModule } from './analytics/analytics.module';
import { CommonModule } from '../common/common.module'; // New import
import { config } from '../config/config';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: config.database.host,
      port: config.database.port,
      username: config.database.username,
      password: config.database.password,
      database: config.database.database,
      autoLoadEntities: true,
      synchronize: true, // Set to false in production
    }),
    CommonModule, // New module
    AuthModule,
    UserModule,
    PaymentModule,
    CardModule,
    UtilityModule,
    FlightModule,
    SubscriptionModule,
    BettingModule,
    NotificationModule,
    AnalyticsModule,
  ],
})
export class AppModule {}
