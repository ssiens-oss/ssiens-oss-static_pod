import express, { Request, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { validateWebhookHeaders, validateWebhookPayload } from '../middleware/validation';
import { verifyTikTokSignature, validateTimestamp } from '../utils/webhookVerification';
import { saveOrder, processOrder, markOrderAsProcessed } from '../services/orderService';
import { logWebhookEvent, isEventProcessed } from '../services/webhookService';
import { TikTokWebhookPayload } from '../types/tiktok';
import { OperationalError } from '../middleware/errorHandler';

const router = express.Router();

/**
 * TikTok Webhook Endpoint
 * POST /webhook/tiktok
 */
router.post(
  '/tiktok',
  express.raw({ type: 'application/json' }), // Keep raw body for signature verification
  asyncHandler(async (req: Request, res: Response) => {
    const rawBody = req.body.toString('utf8');

    // Parse JSON body
    let payload: TikTokWebhookPayload;
    try {
      payload = JSON.parse(rawBody);
    } catch (error) {
      throw new OperationalError('Invalid JSON payload', 400);
    }

    // Extract headers
    const signature = req.headers['x-tiktok-shop-signature'] as string;
    const timestamp = req.headers['x-tiktok-shop-timestamp'] as string;

    // Validate headers presence
    if (!signature || !timestamp) {
      throw new OperationalError(
        'Missing required headers: x-tiktok-shop-signature and x-tiktok-shop-timestamp',
        401
      );
    }

    // Validate timestamp (prevent replay attacks)
    if (!validateTimestamp(timestamp)) {
      throw new OperationalError('Webhook timestamp is too old or invalid', 401);
    }

    // Verify signature
    const appSecret = process.env.TIKTOK_APP_SECRET;
    if (!appSecret) {
      console.error('TIKTOK_APP_SECRET is not configured');
      throw new OperationalError('Server configuration error', 500);
    }

    const isValid = verifyTikTokSignature(rawBody, signature, timestamp, appSecret);
    if (!isValid) {
      await logWebhookEvent(payload, signature, timestamp, false, 'Invalid signature');
      throw new OperationalError('Invalid webhook signature', 401);
    }

    console.log('Webhook received and verified:', {
      type: payload.type,
      shop_id: payload.shop_id,
      order_id: payload.data?.order_id,
      timestamp: payload.timestamp,
    });

    // Check for duplicate events (idempotency)
    const alreadyProcessed = await isEventProcessed(payload);
    if (alreadyProcessed) {
      console.log('Webhook event already processed (duplicate), skipping');
      return res.status(200).json({
        success: true,
        message: 'Event already processed',
      });
    }

    try {
      // Save order to database
      const orderRecord = await saveOrder(
        payload.data.order_id,
        payload.shop_id,
        payload.type,
        payload.data
      );

      console.log('Order saved to database:', {
        id: orderRecord.id,
        order_id: orderRecord.order_id,
        status: orderRecord.order_status,
      });

      // Process order (business logic)
      await processOrder(payload.data);

      // Mark as successfully processed
      await markOrderAsProcessed(payload.data.order_id, true);

      // Log successful webhook processing
      await logWebhookEvent(payload, signature, timestamp, true);

      // Respond to TikTok (must respond within 5 seconds)
      res.status(200).json({
        success: true,
        message: 'Webhook processed successfully',
        order_id: payload.data.order_id,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      console.error('Error processing webhook:', {
        error: errorMessage,
        order_id: payload.data?.order_id,
      });

      // Mark as failed
      if (payload.data?.order_id) {
        await markOrderAsProcessed(payload.data.order_id, false, errorMessage);
      }

      // Log failed webhook
      await logWebhookEvent(payload, signature, timestamp, false, errorMessage);

      // Still return 200 to TikTok to acknowledge receipt
      // We'll retry processing internally
      res.status(200).json({
        success: false,
        message: 'Webhook received but processing failed',
        error: errorMessage,
      });
    }
  })
);

/**
 * Webhook health check
 * GET /webhook/health
 */
router.get('/health', (req: Request, res: Response) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'TikTok Webhook Service',
  });
});

export default router;
