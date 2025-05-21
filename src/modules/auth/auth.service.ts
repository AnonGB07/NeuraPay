import { Injectable, UnauthorizedException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { JwtService } from '@nestjs/jwt';
import { User } from './user.entity';
import * as bcrypt from 'bcrypt';
import { config } from '../../config/config';

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    private jwtService: JwtService,
  ) {}

  async signUp(email: string, password: string, phone: string) {
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = this.userRepository.create({
      email,
      password: hashedPassword,
      phone,
      kycStatus: 'pending',
    });
    await this.userRepository.save(user);
    return this.generateToken(user);
  }

  async signIn(email: string, password: string) {
    const user = await this.userRepository.findOne({ where: { email } });
    if (!user || !(await bcrypt.compare(password, user.password))) {
      throw new UnauthorizedException('Invalid credentials');
    }
    return this.generateToken(user);
  }

  private generateToken(user: User) {
    const payload = { email: user.email, sub: user.id };
    return {
      access_token: this.jwtService.sign(payload, {
        secret: config.jwtSecret,
        expiresIn: '1h',
      }),
    };
  }

  async verifyKyc(userId: number, kycData: any) {
    // Integrate with Onfido for KYC
    const response = await fetch('https://api.onfido.com/v3/checks', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer your_onfido_api_key',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(kycData),
    });
    const result = await response.json();
    const user = await this.userRepository.findOne({ where: { id: userId } });
    user.kycStatus = result.status === 'complete' ? 'verified' : 'failed';
    await this.userRepository.save(user);
    return user;
  }
}
