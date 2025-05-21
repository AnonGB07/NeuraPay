import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @Column()
  password: string;

  @Column()
  phone: string;

  @Column({ nullable: true })
  kycStatus: 'pending' | 'verified' | 'failed';

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
