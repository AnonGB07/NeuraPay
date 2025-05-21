import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Card {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  userId: number;

  @Column()
  cardNumber: string;

  @Column()
  type: 'virtual' | 'physical';

  @Column()
  status: 'pending' | 'active' | 'inactive';

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
