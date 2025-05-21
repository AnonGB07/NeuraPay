export const config = {
  // Replace with your actual API keys and credentials
  stripeKey: 'sk_test_your_stripe_key',
  coingateKey: 'your_coingate_api_key',
  reloadlyKey: 'your_reloadly_api_key',
  amadeusKey: 'your_amadeus_api_key',
  betwayKey: 'your_betway_api_key',
  sportpesaKey: 'your_sportpesa_api_key',
  jwtSecret: 'your_jwt_secret_123',
  database: {
    host: 'localhost', // Your VPS PostgreSQL host
    port: 5432,
    username: 'neurapay_admin',
    password: 'your_secure_password_123',
    database: 'neurapay_db',
  },
  redis: {
    host: 'localhost', // Your VPS Redis host
    port: 6379,
    password: 'your_redis_password_123',
  },
  aws: {
    accessKeyId: 'your_aws_access_key',
    secretAccessKey: 'your_aws_secret_key',
    region: 'us-east-1',
  },
  email: {
    host: 'smtp.your-email-provider.com',
    port: 587,
    user: 'your_email@example.com',
    pass: 'your_email_password',
  },
};
