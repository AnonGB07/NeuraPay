import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { createClient } from 'redis';
import { config } from '../../config/config';

@Injectable()
export class RedisService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(RedisService.name);
  private client: ReturnType<typeof createClient>;

  constructor() {
    this.client = createClient({
      url: `redis://:${config.redis.password}@${config.redis.host}:${config.redis.port}`,
    });

    this.client.on('error', (err) => this.logger.error(`Redis Client Error: ${err}`));
  }

  async onModuleInit() {
    await this.client.connect();
    this.logger.log('Redis client connected');
  }

  async onModuleDestroy() {
    await this.client.disconnect();
    this.logger.log('Redis client disconnected');
  }

  async get(key: string): Promise<string | null> {
    return this.client.get(key);
  }

  async set(key: string, value: string, expirySeconds?: number): Promise<void> {
    if (expirySeconds) {
      await this.client.setEx(key, expirySeconds, value);
    } else {
      await this.client.set(key, value);
    }
  }

  async del(key: string): Promise<void> {
    await this.client.del(key);
  }
}
