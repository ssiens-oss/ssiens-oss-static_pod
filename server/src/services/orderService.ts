import { query } from '../config/database';
import { TikTokOrder, TikTokEventType, OrderRecord } from '../types/tiktok';

/**
 * Save order to database
 */
export async function saveOrder(
  orderId: string,
  shopId: string,
  eventType: TikTokEventType,
  orderData: TikTokOrder
): Promise<OrderRecord> {
  const queryText = `
    INSERT INTO tiktok_orders (
      order_id,
      shop_id,
      event_type,
      order_status,
      order_data,
      processed
    )
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (order_id, event_type, updated_at)
    DO UPDATE SET
      order_status = EXCLUDED.order_status,
      order_data = EXCLUDED.order_data,
      updated_at = CURRENT_TIMESTAMP
    RETURNING *
  `;

  const values = [
    orderId,
    shopId,
    eventType,
    orderData.order_status,
    JSON.stringify(orderData),
    false,
  ];

  const result = await query(queryText, values);
  return result.rows[0];
}

/**
 * Get order by ID
 */
export async function getOrderById(orderId: string): Promise<OrderRecord | null> {
  const queryText = `
    SELECT * FROM tiktok_orders
    WHERE order_id = $1
    ORDER BY created_at DESC
    LIMIT 1
  `;

  const result = await query(queryText, [orderId]);
  return result.rows[0] || null;
}

/**
 * Get unprocessed orders
 */
export async function getUnprocessedOrders(limit: number = 100): Promise<OrderRecord[]> {
  const queryText = `
    SELECT * FROM tiktok_orders
    WHERE processed = false
    ORDER BY created_at ASC
    LIMIT $1
  `;

  const result = await query(queryText, [limit]);
  return result.rows;
}

/**
 * Mark order as processed
 */
export async function markOrderAsProcessed(
  orderId: string,
  success: boolean,
  errorMessage?: string
): Promise<void> {
  const queryText = `
    UPDATE tiktok_orders
    SET processed = $1, error_message = $2, updated_at = CURRENT_TIMESTAMP
    WHERE order_id = $3
  `;

  await query(queryText, [success, errorMessage || null, orderId]);
}

/**
 * Get orders by shop ID
 */
export async function getOrdersByShop(
  shopId: string,
  limit: number = 100,
  offset: number = 0
): Promise<OrderRecord[]> {
  const queryText = `
    SELECT * FROM tiktok_orders
    WHERE shop_id = $1
    ORDER BY created_at DESC
    LIMIT $2 OFFSET $3
  `;

  const result = await query(queryText, [shopId, limit, offset]);
  return result.rows;
}

/**
 * Process order business logic
 */
export async function processOrder(orderData: TikTokOrder): Promise<void> {
  console.log(`Processing order ${orderData.order_id}`, {
    status: orderData.order_status,
    total: orderData.total_amount,
    items: orderData.items.length,
  });

  // TODO: Implement your business logic here
  // Examples:
  // - Send order to Printify for fulfillment
  // - Update inventory
  // - Send confirmation email
  // - Trigger automation workflows
  // - Update analytics

  // Placeholder: Log order details
  for (const item of orderData.items) {
    console.log(`  - Item: ${item.product_name} (${item.sku_name}) x${item.quantity}`);
  }

  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 100));
}
