import { Controller, Post, Body, UseGuards } from '@nestjs/common';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { User } from '../../common/decorators/user.decorator';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('signup')
  async signUp(@Body() body: { email: string; password: string; phone: string }) {
    return this.authService.signUp(body.email, body.password, body.phone);
  }

  @Post('signin')
  async signIn(@Body() body: { email: string; password: string }) {
    return this.authService.signIn(body.email, body.password);
  }

  @Post('kyc')
  @UseGuards(JwtAuthGuard)
  async verifyKyc(@User('id') userId: number, @Body() kycData: any) {
    return this.authService.verifyKyc(userId, kycData);
  }
}
