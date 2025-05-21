import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Utility {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  userId: number;

  @Column()
  billId: string;

  @Column()
  amount: number;

  @Column()
  status: 'pending' | 'completed' | 'failed';

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
