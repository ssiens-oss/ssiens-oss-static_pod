import express, { Application } from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import webhookRouter from './routes/webhook';
import ordersRouter from './routes/orders';
import { errorHandler } from './middleware/errorHandler';
import pool from './config/database';

// Load environment variables
dotenv.config();

const app: Application = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());

// CORS configuration
app.use(
  cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  })
);

// Request logging
app.use(morgan('combined'));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000'), // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/', limiter);

// Body parsing - JSON for most routes
app.use('/api/orders', express.json());

// Routes
app.use('/webhook', webhookRouter); // Webhook uses raw body parser
app.use('/api/orders', ordersRouter);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development',
  });
});

// Error handling middleware (must be last)
app.use(errorHandler);

// Graceful shutdown
const gracefulShutdown = async () => {
  console.log('Received shutdown signal, closing server gracefully...');

  try {
    await pool.end();
    console.log('Database connections closed');
  } catch (error) {
    console.error('Error closing database connections:', error);
  }

  process.exit(0);
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// Start server
const server = app.listen(PORT, () => {
  console.log(`🚀 TikTok Webhook Server running on port ${PORT}`);
  console.log(`📝 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
  console.log(`\nEndpoints:`);
  console.log(`  - POST /webhook/tiktok - TikTok webhook receiver`);
  console.log(`  - GET  /webhook/health - Webhook health check`);
  console.log(`  - GET  /api/orders/:orderId - Get order by ID`);
  console.log(`  - GET  /api/orders/shop/:shopId - Get orders by shop`);
  console.log(`  - GET  /api/orders/queue/unprocessed - Get unprocessed orders`);
  console.log(`  - GET  /api/orders/stats/webhooks - Webhook statistics`);
  console.log(`  - GET  /api/orders/stats/orders - Order statistics`);
  console.log(`  - GET  /health - Server health check`);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Don't exit in production, just log
  if (process.env.NODE_ENV === 'development') {
    process.exit(1);
  }
});

export default app;
