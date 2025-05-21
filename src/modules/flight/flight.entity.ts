import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Flight {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  userId: number;

  @Column()
  flightId: string;

  @Column()
  amount: number;

  @Column()
  status: 'pending' | 'completed' | 'failed';

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
