import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { OperationalError } from './errorHandler';
import { TikTokEventType, TikTokOrderStatus } from '../types/tiktok';

/**
 * Zod schema for TikTok webhook payload validation
 */
const TikTokOrderItemSchema = z.object({
  id: z.string(),
  product_id: z.string(),
  product_name: z.string(),
  sku_id: z.string(),
  sku_name: z.string(),
  quantity: z.number().positive(),
  original_price: z.number().nonnegative(),
  sale_price: z.number().nonnegative(),
  seller_sku: z.string().optional(),
  image_url: z.string().url().optional(),
});

const TikTokShippingAddressSchema = z.object({
  full_address: z.string(),
  name: z.string(),
  phone: z.string(),
  region_code: z.string(),
  postal_code: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  district: z.string().optional(),
});

const TikTokOrderSchema = z.object({
  order_id: z.string(),
  order_status: z.nativeEnum(TikTokOrderStatus),
  create_time: z.number(),
  update_time: z.number(),
  payment_method: z.string().optional(),
  shipping_provider: z.string().optional(),
  tracking_number: z.string().optional(),
  items: z.array(TikTokOrderItemSchema).min(1),
  shipping_address: TikTokShippingAddressSchema.optional(),
  buyer_message: z.string().optional(),
  total_amount: z.number().nonnegative(),
  shipping_fee: z.number().nonnegative().optional(),
  buyer_email: z.string().email().optional(),
});

const TikTokWebhookPayloadSchema = z.object({
  timestamp: z.number(),
  type: z.nativeEnum(TikTokEventType),
  shop_id: z.string(),
  data: TikTokOrderSchema,
});

/**
 * Validate webhook payload structure
 */
export const validateWebhookPayload = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const result = TikTokWebhookPayloadSchema.safeParse(req.body);

    if (!result.success) {
      const errors = result.error.errors.map(err => ({
        path: err.path.join('.'),
        message: err.message,
      }));

      throw new OperationalError(
        `Invalid webhook payload: ${JSON.stringify(errors)}`,
        400
      );
    }

    // Attach validated data to request
    req.body = result.data;
    next();
  } catch (error) {
    next(error);
  }
};

/**
 * Validate required webhook headers
 */
export const validateWebhookHeaders = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const signature = req.headers['x-tiktok-shop-signature'] as string;
  const timestamp = req.headers['x-tiktok-shop-timestamp'] as string;

  if (!signature || !timestamp) {
    throw new OperationalError(
      'Missing required headers: x-tiktok-shop-signature and x-tiktok-shop-timestamp',
      401
    );
  }

  next();
};
