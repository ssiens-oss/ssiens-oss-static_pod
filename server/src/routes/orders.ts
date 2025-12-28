import express, { Request, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import {
  getOrderById,
  getOrdersByShop,
  getUnprocessedOrders,
} from '../services/orderService';
import { getWebhookStats } from '../services/webhookService';
import { query } from '../config/database';

const router = express.Router();

/**
 * Get order by ID
 * GET /orders/:orderId
 */
router.get(
  '/:orderId',
  asyncHandler(async (req: Request, res: Response) => {
    const { orderId } = req.params;

    const order = await getOrderById(orderId);

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found',
      });
    }

    res.status(200).json({
      success: true,
      data: order,
    });
  })
);

/**
 * Get orders by shop ID
 * GET /orders/shop/:shopId?limit=100&offset=0
 */
router.get(
  '/shop/:shopId',
  asyncHandler(async (req: Request, res: Response) => {
    const { shopId } = req.params;
    const limit = parseInt(req.query.limit as string) || 100;
    const offset = parseInt(req.query.offset as string) || 0;

    const orders = await getOrdersByShop(shopId, limit, offset);

    res.status(200).json({
      success: true,
      data: orders,
      pagination: {
        limit,
        offset,
        count: orders.length,
      },
    });
  })
);

/**
 * Get unprocessed orders
 * GET /orders/unprocessed?limit=100
 */
router.get(
  '/queue/unprocessed',
  asyncHandler(async (req: Request, res: Response) => {
    const limit = parseInt(req.query.limit as string) || 100;

    const orders = await getUnprocessedOrders(limit);

    res.status(200).json({
      success: true,
      data: orders,
      count: orders.length,
    });
  })
);

/**
 * Get webhook statistics
 * GET /orders/stats/webhooks?shopId=xxx
 */
router.get(
  '/stats/webhooks',
  asyncHandler(async (req: Request, res: Response) => {
    const shopId = req.query.shopId as string | undefined;

    const stats = await getWebhookStats(shopId);

    res.status(200).json({
      success: true,
      data: stats,
    });
  })
);

/**
 * Get order statistics
 * GET /orders/stats/orders
 */
router.get(
  '/stats/orders',
  asyncHandler(async (req: Request, res: Response) => {
    const result = await query('SELECT * FROM order_statistics ORDER BY order_count DESC');

    res.status(200).json({
      success: true,
      data: result.rows,
    });
  })
);

export default router;
