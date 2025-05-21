import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Betting {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  userId: number;

  @Column()
  platform: string;

  @Column()
  amount: number;

  @Column()
  transactionId: string;

  @Column()
  status: 'pending' | 'completed' | 'failed';

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
