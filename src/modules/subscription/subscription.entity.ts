import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Subscription {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  userId: number;

  @Column()
  type: 'airtime' | 'data' | 'tv';

  @Column()
  provider: string;

  @Column()
  amount: number;

  @Column()
  transactionId: string;

  @Column()
  status: 'pending' | 'completed' | 'failed';

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
