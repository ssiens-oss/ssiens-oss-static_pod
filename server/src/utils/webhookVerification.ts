import crypto from 'crypto';

/**
 * Verify TikTok webhook signature
 *
 * TikTok signs webhook requests using HMAC-SHA256
 * Signature = HMAC-SHA256(app_secret, timestamp + request_body)
 */
export function verifyTikTokSignature(
  payload: string,
  signature: string,
  timestamp: string,
  appSecret: string
): boolean {
  try {
    // Construct the string to sign: timestamp + payload
    const signString = timestamp + payload;

    // Calculate HMAC-SHA256
    const expectedSignature = crypto
      .createHmac('sha256', appSecret)
      .update(signString)
      .digest('hex');

    // Compare signatures using timing-safe comparison
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch (error) {
    console.error('Signature verification error:', error);
    return false;
  }
}

/**
 * Validate webhook timestamp to prevent replay attacks
 * Rejects requests older than 5 minutes
 */
export function validateTimestamp(timestamp: string): boolean {
  const requestTime = parseInt(timestamp, 10);
  const currentTime = Math.floor(Date.now() / 1000);
  const timeDifference = Math.abs(currentTime - requestTime);

  // Allow 5 minutes (300 seconds) tolerance
  const TOLERANCE_SECONDS = 300;

  return timeDifference <= TOLERANCE_SECONDS;
}

/**
 * Generate a unique event ID from the webhook payload
 */
export function generateEventId(payload: any): string {
  const eventString = JSON.stringify({
    timestamp: payload.timestamp,
    type: payload.type,
    shop_id: payload.shop_id,
    order_id: payload.data?.order_id,
  });

  return crypto
    .createHash('sha256')
    .update(eventString)
    .digest('hex')
    .substring(0, 32);
}
