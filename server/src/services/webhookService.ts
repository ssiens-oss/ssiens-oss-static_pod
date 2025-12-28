import { query } from '../config/database';
import { TikTokWebhookPayload } from '../types/tiktok';
import { generateEventId } from '../utils/webhookVerification';

/**
 * Log webhook event for auditing
 */
export async function logWebhookEvent(
  payload: TikTokWebhookPayload,
  signature: string,
  timestamp: string,
  success: boolean,
  errorMessage?: string
): Promise<void> {
  const eventId = generateEventId(payload);

  const queryText = `
    INSERT INTO webhook_events (
      event_id,
      shop_id,
      event_type,
      payload,
      signature,
      timestamp,
      processed,
      success,
      error_message
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    ON CONFLICT (event_id)
    DO UPDATE SET
      processed = EXCLUDED.processed,
      success = EXCLUDED.success,
      error_message = EXCLUDED.error_message
  `;

  const values = [
    eventId,
    payload.shop_id,
    payload.type,
    JSON.stringify(payload),
    signature,
    parseInt(timestamp, 10),
    true,
    success,
    errorMessage || null,
  ];

  await query(queryText, values);
}

/**
 * Check if webhook event was already processed (idempotency check)
 */
export async function isEventProcessed(payload: TikTokWebhookPayload): Promise<boolean> {
  const eventId = generateEventId(payload);

  const queryText = `
    SELECT success FROM webhook_events
    WHERE event_id = $1 AND processed = true AND success = true
    LIMIT 1
  `;

  const result = await query(queryText, [eventId]);
  return result.rows.length > 0;
}

/**
 * Get webhook statistics
 */
export async function getWebhookStats(shopId?: string) {
  let queryText = `
    SELECT
      event_type,
      COUNT(*) as total,
      SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
      SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed,
      MAX(received_at) as last_received
    FROM webhook_events
  `;

  const params: string[] = [];

  if (shopId) {
    queryText += ' WHERE shop_id = $1';
    params.push(shopId);
  }

  queryText += ' GROUP BY event_type';

  const result = await query(queryText, params);
  return result.rows;
}
