// server.js
const express = require('express');
const { ApolloServer } = require('apollo-server-express');
const mongoose = require('mongoose');
const redis = require('redis');
const { Kafka } = require('kafkajs');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const cors = require('cors');
const axios = require('axios');
const dotenv = require('dotenv');
const bcrypt = require('bcryptjs');
const { gql } = require('apollo-server-express');
const crypto = require('crypto');
const firebaseAdmin = require('firebase-admin');

// Load environment variables
dotenv.config();

// Initialize Firebase for push notifications
firebaseAdmin.initializeApp({
  credential: firebaseAdmin.credential.cert(JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT))
});

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors({ origin: process.env.CORS_ORIGIN || '*' }));
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: 'Too many requests, please try again later.'
}));

// MongoDB Connection with retry logic
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  serverSelectionTimeoutMS: 5000
}).then(() => console.log('Connected to MongoDB'))
  .catch(err => {
    console.error('MongoDB connection error:', err);
    setTimeout(() => mongoose.connect(process.env.MONGO_URI), 5000);
  });

// Redis Client with clustering support
const redisClient = redis.createClient({
  url: process.env.REDIS_URI,
  socket: { reconnectStrategy: retries => Math.min(retries * 100, 3000) }
});
redisClient.connect().catch(err => console.error('Redis connection error:', err));

// Kafka Client with region-based partitioning
const kafka = new Kafka({
  clientId: 'utility-app',
  brokers: [process.env.KAFKA_BROKER],
  retry: { retries: 10 }
});
const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'utility-group' });
async function connectKafka() {
  await producer.connect();
  await consumer.connect();
  await consumer.subscribe({ topic: 'utility-tasks', fromBeginning: false });
  await consumer.subscribe({ topic: 'notifications', fromBeginning: false });
}
connectKafka().catch(err => console.error('Kafka connection error:', err));

// Schemas
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true, index: true },
  password: { type: String, required: true },
  country: {
    type: String,
    enum: [
      // North Africa
      'Egypt', 'Algeria', 'Morocco', 'Tunisia', 'Libya',
      // East Africa
      'Ethiopia', 'Kenya', 'Uganda', 'Tanzania', 'Sudan',
      // West Africa
      'Nigeria', 'Ghana', 'Cote dIvoire', 'Senegal', 'Mali',
      // Southern Africa
      'South Africa', 'Angola', 'Zambia', 'Zimbabwe', 'Botswana',
      // Central Africa
      'DRC', 'Cameroon', 'Chad', 'Republic of Congo', 'Central African Republic'
    ],
    required: true
  },
  walletBalance: { type: Number, default: 0 },
  loyaltyPoints: { type: Number, default: 0 },
  language: { type: String, default: 'en' },
  deviceToken: String,
  createdAt: { type: Date, default: Date.now }
});
const User = mongoose.model('User', userSchema);

const cardSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', index: true },
  type: { type: String, enum: ['virtual', 'physical'], required: true },
  cardNumber: { type: String, required: true },
  status: { type: String, enum: ['active', 'frozen', 'cancelled'], default: 'active' },
  spendingLimit: { type: Number, default: 1000 },
  createdAt: { type: Date, default: Date.now }
});
const Card = mongoose.model('Card', cardSchema);

const transactionSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', index: true },
  type: {
    type: String,
    enum: ['airtime', 'data', 'flight', 'electricity', 'tv', 'water', 'internet', 'insurance', 'transfer', 'card', 'topup', 'loyalty'],
    required: true
  },
  amount: { type: Number, required: true },
  fee: { type: Number, default: 0 },
  currency: {
    type: String,
    enum: ['EGP', 'DZD', 'MAD', 'TND', 'LYD', 'ETB', 'KES', 'UGX', 'TZS', 'SDG', 'NGN', 'GHS', 'XOF', 'XAF', 'ZAR', 'AOA', 'ZMW', 'ZWL', 'BWP', 'CDF', 'USD', 'BTC', 'USDT', 'ETH'],
    default: 'USD'
  },
  status: { type: String, enum: ['pending', 'completed', 'failed'], default: 'pending' },
  provider: String,
  details: Object,
  createdAt: { type: Date, default: Date.now }
});
const Transaction = mongoose.model('Transaction', transactionSchema);

// GraphQL Schema
const typeDefs = gql`
  type User {
    id: ID!
    email: String!
    country: String!
    walletBalance: Float!
    loyaltyPoints: Int!
    language: String!
    createdAt: String!
  }
  type Card {
    id: ID!
    type: String!
    cardNumber: String!
    status: String!
    spendingLimit: Float!
    createdAt: String!
  }
  type Transaction {
    id: ID!
    type: String!
    amount: Float!
    fee: Float!
    currency: String!
    status: String!
    provider: String!
    details: String
    createdAt: String!
  }
  type Analytics {
    spending: Float!
    categoryBreakdown: String!
    recommendations: String!
  }
  type Query {
    me: User
    transactions(limit: Int, offset: Int): [Transaction]
    cards: [Card]
    analytics: Analytics
    supportedCurrencies: [String]
    utilityProviders(type: String!, country: String!): [String]
  }
  type Mutation {
    register(email: String!, password: String!, country: String!, deviceToken: String, language: String): String
    login(email: String!, password: String!, deviceToken: String): String
    purchaseUtility(type: String!, amount: Float!, provider: String!, currency: String!, details: String): String
    orderCard(type: String!, spendingLimit: Float, currency: String!): String
    transferFunds(toEmail: String!, amount: Float!, currency: String!): String
    updateLanguage(language: String!): Boolean
    freezeCard(cardId: ID!, freeze: Boolean!): Boolean
    topUpWallet(amount: Float!, currency: String!): String
    redeemLoyaltyPoints(amount: Int!): String
  }
`;

// GraphQL Resolvers
const resolvers = {
  Query: {
    me: async (_, __, { user }) => {
      if (!user) throw new Error('Unauthorized');
      return await User.findById(user.userId);
    },
    transactions: async (_, { limit = 10, offset = 0 }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const cacheKey = `transactions:${user.userId}:${limit}:${offset}`;
      const cached = await redisClient.get(cacheKey);
      if (cached) return JSON.parse(cached);

      const transactions = await Transaction.find({ userId: user.userId })
        .sort({ createdAt: -1 })
        .skip(offset)
        .limit(limit);
      await redisClient.setEx(cacheKey, 300, JSON.stringify(transactions));
      return transactions;
    },
    cards: async (_, __, { user }) => {
      if (!user) throw new Error('Unauthorized');
      return await Card.find({ userId: user.userId });
    },
    analytics: async (_, __, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const transactions = await Transaction.find({ userId: user.userId });
      const spending = transactions.reduce((sum, t) => sum + t.amount, 0);
      const categoryBreakdown = JSON.stringify(
        transactions.reduce((acc, t) => ({ ...acc, [t.type]: (acc[t.type] || 0) + t.amount }), {})
      );
      const recommendations = spending > 1000 ? 'Consider reducing spending on high-cost categories.' : 'You’re managing your budget well!';
      return { spending, categoryBreakdown, recommendations };
    },
    supportedCurrencies: () => [
      'EGP', 'DZD', 'MAD', 'TND', 'LYD', // North
      'ETB', 'KES', 'UGX', 'TZS', 'SDG', // East
      'NGN', 'GHS', 'XOF', 'XAF', // West
      'ZAR', 'AOA', 'ZMW', 'ZWL', 'BWP', // Southern
      'CDF', 'XAF', // Central
      'USD', 'BTC', 'USDT', 'ETH' // Global/Crypto
    ],
    utilityProviders: async (_, { type, country }) => {
      const providers = {
        // North Africa
        Egypt: { airtime: ['Vodafone', 'Orange'], electricity: ['North Cairo'], water: ['Cairo Water'] },
        Algeria: { airtime: ['Mobilis', 'Djezzy'], electricity: ['Sonelgaz'], water: ['ADE'] },
        Morocco: { airtime: ['Maroc Telecom', 'Orange'], electricity: ['ONE'], water: ['Lydec'] },
        Tunisia: { airtime: ['Ooredoo', 'Tunisie Telecom'], electricity: ['STEG'], water: ['SONEDE'] },
        Libya: { airtime: ['Almadar', 'Libyana'], electricity: ['GECOL'], water: ['Libya Water'] },
        // East Africa
        Ethiopia: { airtime: ['Ethio Telecom'], electricity: ['EEPCO'], water: ['Addis Water'] },
        Kenya: { airtime: ['Safaricom', 'Airtel'], electricity: ['KPLC'], water: ['Nairobi Water'] },
        Uganda: { airtime: ['MTN', 'Airtel'], electricity: ['Umeme'], water: ['NWSC'] },
        Tanzania: { airtime: ['Vodacom', 'Tigo'], electricity: ['TANESCO'], water: ['DAWASA'] },
        Sudan: { airtime: ['Zain', 'MTN'], electricity: ['SEDC'], water: ['Khartoum Water'] },
        // West Africa
        Nigeria: { airtime: ['MTN', 'Airtel'], electricity: ['Eko', 'Ikeja'], water: ['Lagos Water'] },
        Ghana: { airtime: ['MTN', 'Vodafone'], electricity: ['ECG'], water: ['Ghana Water'] },
        'Cote dIvoire': { airtime: ['Orange', 'MTN'], electricity: ['CIE'], water: ['SODECI'] },
        Senegal: { airtime: ['Orange', 'Free'], electricity: ['SENELEC'], water: ['Sen’Eau'] },
        Mali: { airtime: ['Orange', 'Malitel'], electricity: ['EDM'], water: ['Mali Water'] },
        // Southern Africa
        'South Africa': { airtime: ['Vodacom', 'MTN'], electricity: ['Eskom'], water: ['Joburg Water'] },
        Angola: { airtime: ['Unitel', 'Movicel'], electricity: ['ENDE'], water: ['EPAL'] },
        Zambia: { airtime: ['MTN', 'Airtel'], electricity: ['ZESCO'], water: ['LWSC'] },
        Zimbabwe: { airtime: ['Econet', 'NetOne'], electricity: ['ZESA'], water: ['Harare Water'] },
        Botswana: { airtime: ['Mascom', 'Orange'], electricity: ['BPC'], water: ['WUC'] },
        // Central Africa
        DRC: { airtime: ['Vodacom', 'Airtel'], electricity: ['SNEL'], water: ['REGIDESO'] },
        Cameroon: { airtime: ['MTN', 'Orange'], electricity: ['Eneo'], water: ['Camwater'] },
        Chad: { airtime: ['Tigo', 'Airtel'], electricity: ['SNE'], water: ['STE'] },
        'Republic of Congo': { airtime: ['MTN', 'Airtel'], electricity: ['E2C'], water: ['LCDE'] },
        'Central African Republic': { airtime: ['Orange', 'Telecel'], electricity: ['ENERCA'], water: ['SODECA'] }
      };
      const cacheKey = `providers:${country}:${type}`;
      const cached = await redisClient.get(cacheKey);
      if (cached) return JSON.parse(cached);

      const providerList = providers[country]?.[type] || [];
      await redisClient.setEx(cacheKey, 3600, JSON.stringify(providerList));
      return providerList;
    }
  },
  Mutation: {
    register: async (_, { email, password, country, deviceToken, language }) => {
      const hashedPassword = await bcrypt.hash(password, 10);
      const user = new User({ email, password: hashedPassword, country, deviceToken, language });
      await user.save();
      const token = jwt.sign({ userId: user._id, country }, process.env.JWT_SECRET, { expiresIn: '7d' });
      await producer.send({
        topic: 'notifications',
        messages: [{
          value: JSON.stringify({
            userId: user._id,
            message: `Welcome to the Utility App, ${email}!`
          })
        }]
      });
      return token;
    },
    login: async (_, { email, password, deviceToken }) => {
      const user = await User.findOne({ email });
      if (!user || !await bcrypt.compare(password, user.password)) {
        throw new Error('Invalid credentials');
      }
      if (deviceToken) await User.findByIdAndUpdate(user._id, { deviceToken });
      return jwt.sign({ userId: user._id, country: user.country }, process.env.JWT_SECRET, { expiresIn: '7d' });
    },
    purchaseUtility: async (_, { type, amount, provider, currency, details }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const cacheKey = `purchase:${user.userId}:${type}:${Date.now()}`;
      const cached = await redisClient.get(cacheKey);
      if (cached) throw new Error('Request already in progress');

      const fee = amount * 0.015; // 1.5% transaction fee
      const userData = await User.findById(user.userId);
      if (amount + fee > userData.walletBalance) {
        throw new Error('Insufficient wallet balance');
      }

      const transaction = new Transaction({
        userId: user.userId,
        type,
        amount,
        fee,
        currency,
        provider,
        details: JSON.parse(details || '{}')
      });
      await transaction.save();

      await producer.send({
        topic: 'utility-tasks',
        partition: getRegionPartition(user.country),
        messages: [{
          value: JSON.stringify({
            transactionId: transaction._id,
            type,
            amount,
            currency,
            provider,
            details: JSON.parse(details || '{}'),
            country: user.country
          })
        }]
      });

      await redisClient.setEx(cacheKey, 60, 'processing');
      await User.findByIdAndUpdate(user.userId, {
        $inc: { walletBalance: -(amount + fee), loyaltyPoints: Math.floor(amount / 10) }
      });

      await producer.send({
        topic: 'notifications',
        messages: [{
          value: JSON.stringify({
            userId: user.userId,
            message: `Your ${type} purchase of ${amount} ${currency} is being processed.`
          })
        }]
      });

      return transaction._id;
    },
    orderCard: async (_, { type, spendingLimit, currency }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const userData = await User.findById(user.userId);
      const fee = type === 'virtual' ? 2 : 10;
      if (userData.walletBalance < fee) throw new Error('Insufficient wallet balance');

      const cardNumber = crypto.randomBytes(8).toString('hex').match(/.{1,4}/g).join('-');
      const card = new Card({ userId: user.userId, type, cardNumber, spendingLimit: spendingLimit || 1000 });
      await card.save();

      await producer.send({
        topic: 'utility-tasks',
        partition: getRegionPartition(user.country),
        messages: [{
          value: JSON.stringify({
            transactionId: card._id,
            type: 'card',
            details: { type, cardNumber, spendingLimit, currency },
            country: user.country
          })
        }]
      });

      await User.findByIdAndUpdate(user.userId, {
        $inc: { walletBalance: -fee, loyaltyPoints: 10 }
      });

      await producer.send({
        topic: 'notifications',
        messages: [{
          value: JSON.stringify({
            userId: user.userId,
            message: `Your ${type} card has been ordered.`
          })
        }]
      });

      return card._id;
    },
    transferFunds: async (_, { toEmail, amount, currency }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const sender = await User.findById(user.userId);
      const recipient = await User.findOne({ email: toEmail });
      if (!recipient) throw new Error('Recipient not found');
      if (sender.walletBalance < amount) throw new Error('Insufficient balance');

      const fee = amount * 0.01;
      const transaction = new Transaction({
        userId: user.userId,
        type: 'transfer',
        amount,
        fee,
        currency,
        provider: 'internal',
        details: { toUserId: recipient._id }
      });
      await transaction.save();

      await User.findByIdAndUpdate(user.userId, {
        $inc: { walletBalance: -(amount + fee), loyaltyPoints: Math.floor(amount / 10) }
      });
      await User.findByIdAndUpdate(recipient._id, { $inc: { walletBalance: amount } });

      await producer.send({
        topic: 'utility-tasks',
        partition: getRegionPartition(user.country),
        messages: [{
          value: JSON.stringify({
            transactionId: transaction._id,
            type: 'transfer',
            amount,
            currency,
            details: { toUserId: recipient._id },
            country: user.country
          })
        }]
      });

      await producer.send({
        topic: 'notifications',
        messages: [{
          value: JSON.stringify({
            userId: user.userId,
            message: `You transferred ${amount} ${currency} to ${toEmail}.`
          })
        }, {
          value: JSON.stringify({
            userId: recipient._id,
            message: `You received ${amount} ${currency} from ${sender.email}.`
          })
        }]
      });

      return transaction._id;
    },
    updateLanguage: async (_, { language }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      await User.findByIdAndUpdate(user.userId, { language });
      return true;
    },
    freezeCard: async (_, { cardId, freeze }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const card = await Card.findOne({ _id: cardId, userId: user.userId });
      if (!card) throw new Error('Card not found');
      card.status = freeze ? 'frozen' : 'active';
      await card.save();
      return true;
    },
    topUpWallet: async (_, { amount, currency }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const transaction = new Transaction({
        userId: user.userId,
        type: 'topup',
        amount,
        currency,
        provider: 'payment-gateway'
      });
      await transaction.save();

      await producer.send({
        topic: 'utility-tasks',
        partition: getRegionPartition(user.country),
        messages: [{
          value: JSON.stringify({
            transactionId: transaction._id,
            type: 'topup',
            amount,
            currency,
            details: {},
            country: user.country
          })
        }]
      });

      return transaction._id;
    },
    redeemLoyaltyPoints: async (_, { amount }, { user }) => {
      if (!user) throw new Error('Unauthorized');
      const userData = await User.findById(user.userId);
      if (userData.loyaltyPoints < amount) throw new Error('Insufficient loyalty points');

      const cashValue = amount * 0.01; // 100 points = $1
      await User.findByIdAndUpdate(user.userId, {
        $inc: { loyaltyPoints: -amount, walletBalance: cashValue }
      });

      const transaction = new Transaction({
        userId: user.userId,
        type: 'loyalty',
        amount: cashValue,
        currency: 'USD',
        provider: 'internal',
        details: { points: amount }
      });
      await transaction.save();

      await producer.send({
        topic: 'notifications',
        messages: [{
          value: JSON.stringify({
            userId: user.userId,
            message: `You redeemed ${amount} loyalty points for ${cashValue} USD.`
          })
        }]
      });

      return transaction._id;
    }
  }
};

// Helper: Assign Kafka partition by region
function getRegionPartition(country) {
  const regions = {
    North: ['Egypt', 'Algeria', 'Morocco', 'Tunisia', 'Libya'],
    East: ['Ethiopia', 'Kenya', 'Uganda', 'Tanzania', 'Sudan'],
    West: ['Nigeria', 'Ghana', 'Cote dIvoire', 'Senegal', 'Mali'],
    Southern: ['South Africa', 'Angola', 'Zambia', 'Zimbabwe', 'Botswana'],
    Central: ['DRC', 'Cameroon', 'Chad', 'Republic of Congo', 'Central African Republic']
  };
  for (const [region, countries] of Object.entries(regions)) {
    if (countries.includes(country)) {
      return { North: 0, East: 1, West: 2, Southern: 3, Central: 4 }[region];
    }
  }
  return 0;
}

// GraphQL Server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (token) {
      try {
        return { user: jwt.verify(token, process.env.JWT_SECRET) };
      } catch (err) {
        return {};
      }
    }
    return {};
  },
  formatError: (err) => {
    console.error(err);
    return { message: err.message, code: err.extensions?.code || 'INTERNAL_SERVER_ERROR' };
  }
});

async function startServer() {
  await server.start();
  server.applyMiddleware({ app, path: '/graphql' });
}
startServer();

// Background Task Processor
async function processTasks() {
  await consumer.run({
    eachMessage: async ({ topic, message }) => {
      if (topic === 'utility-tasks') {
        const task = JSON.parse(message.value);
        try {
          let response;
          switch (task.type) {
            case 'card':
              response = await axios.post(
                'https://api.paymentprovider.com/issue-card',
                { type: task.details.type, cardNumber: task.details.cardNumber, spendingLimit: task.details.spendingLimit, currency: task.currency },
                { headers: { Authorization: `Bearer ${process.env.PAYMENT_API_KEY}` } }
              );
              await Card.findByIdAndUpdate(task.transactionId, { status: 'active' });
              break;
            case 'topup':
              response = await axios.post(
                'https://api.paymentprovider.com/topup',
                { amount: task.amount, userId: task.userId, currency: task.currency },
                { headers: { Authorization: `Bearer ${process.env.PAYMENT_API_KEY}` } }
              );
              await User.findByIdAndUpdate(task.userId, { $inc: { walletBalance: task.amount } });
              await Transaction.findByIdAndUpdate(task.transactionId, { status: 'completed' });
              break;
            default:
              response = await axios.post(
                `https://api.provider.com/${task.type}`,
                { amount: task.amount, provider: task.provider, details: task.details, currency: task.currency },
                { headers: { Authorization: `Bearer ${process.env.PROVIDER_API_KEY}` } }
              );
              await Transaction.findByIdAndUpdate(task.transactionId, { status: 'completed' });
          }
          console.log(`Processed ${task.type} task: ${task.transactionId}`);
        } catch (err) {
          console.error(`Task error: ${err.message}`);
          if (task.type === 'card') {
            await Card.findByIdAndUpdate(task.transactionId, { status: 'cancelled' });
          } else {
            await Transaction.findByIdAndUpdate(task.transactionId, { status: 'failed' });
          }
        }
      } else if (topic === 'notifications') {
        const { userId, message } = JSON.parse(message.value);
        const user = await User.findById(userId);
        if (user?.deviceToken) {
          await firebaseAdmin.messaging().send({
            token: user.deviceToken,
            notification: { title: 'Utility App', body: message }
          });
        }
      }
    }
  });
}
processTasks();

// Fraud Detection with Region-Specific Rules
async function detectFraud(transaction) {
  const userId = transaction.userId;
  const country = transaction.country;
  const transactions = await Transaction.find({
    userId,
    createdAt: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
  });

  const thresholds = {
    'South Africa': 20000, Nigeria: 15000, Egypt: 15000, Kenya: 10000, Algeria: 10000,
    Morocco: 10000, Tunisia: 8000, Libya: 8000, Ethiopia: 5000, Uganda: 5000,
    Tanzania: 5000, Sudan: 5000, Ghana: 8000, 'Cote dIvoire': 7000, Senegal: 7000,
    Mali: 6000, Angola: 8000, Zambia: 6000, Zimbabwe: 5000, Botswana: 7000,
    DRC: 5000, Cameroon: 6000, Chad: 4000, 'Republic of Congo': 4000, 'Central African Republic': 3000
  };

  const totalAmount = transactions.reduce((sum, t) => sum + t.amount, 0);
  if (totalAmount > thresholds[country] || 10000) {
    await producer.send({
      topic: 'notifications',
      messages: [{
        value: JSON.stringify({
          userId,
          message: 'High transaction volume detected. Please verify your account.'
        })
      }]
    });
    await Transaction.findByIdAndUpdate(transaction._id, { status: 'pending' });
    return false;
  }
  return true;
}

// Transaction Middleware for Fraud Detection
app.use('/graphql', async (req, res, next) => {
  if (req.body.query?.includes('purchaseUtility') || req.body.query?.includes('transferFunds') || req.body.query?.includes('topUpWallet')) {
    const token = req.headers.authorization?.split(' ')[1];
    if (token) {
      try {
        const user = jwt.verify(token, process.env.JWT_SECRET);
        const transaction = await Transaction.findOne({ userId: user.userId }).sort({ createdAt: -1 });
        if (transaction && !(await detectFraud({ ...transaction.toObject(), country: user.country }))) {
          return res.status(403).json({ error: 'Transaction flagged for review' });
        }
      } catch (err) {
        // Continue without user context if token is invalid
      }
    }
  }
  next();
});

// Error Handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Health Check Endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', uptime: process.uptime() });
});

// Start Server
app.listen(port, () => {
  console.log(`Server running on port ${port}, GraphQL at /graphql`);
});
