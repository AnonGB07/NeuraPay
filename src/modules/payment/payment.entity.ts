import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Payment {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  userId: number;

  @Column()
  amount: number;

  @Column()
  method: 'crypto' | 'bank' | 'utility' | 'flight' | 'airtime' | 'data' | 'tv' | 'betting';

  @Column()
  status: 'pending' | 'completed' | 'failed';

  @Column()
  transactionId: string;

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
