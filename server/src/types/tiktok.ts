/**
 * TikTok Webhook Event Types
 */
export enum TikTokEventType {
  ORDER_STATUS_CHANGE = 'order_status_change',
  ORDER_CREATED = 'order_created',
  ORDER_CANCELLED = 'order_cancelled',
  ORDER_UPDATED = 'order_updated',
  PACKAGE_SHIPPED = 'package_shipped',
  PACKAGE_DELIVERED = 'package_delivered',
}

/**
 * TikTok Order Status
 */
export enum TikTokOrderStatus {
  UNPAID = 'UNPAID',
  AWAITING_SHIPMENT = 'AWAITING_SHIPMENT',
  AWAITING_COLLECTION = 'AWAITING_COLLECTION',
  IN_TRANSIT = 'IN_TRANSIT',
  DELIVERED = 'DELIVERED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

/**
 * TikTok Order Item
 */
export interface TikTokOrderItem {
  id: string;
  product_id: string;
  product_name: string;
  sku_id: string;
  sku_name: string;
  quantity: number;
  original_price: number;
  sale_price: number;
  seller_sku?: string;
  image_url?: string;
}

/**
 * TikTok Shipping Address
 */
export interface TikTokShippingAddress {
  full_address: string;
  name: string;
  phone: string;
  region_code: string;
  postal_code?: string;
  city?: string;
  state?: string;
  district?: string;
}

/**
 * TikTok Order Data
 */
export interface TikTokOrder {
  order_id: string;
  order_status: TikTokOrderStatus;
  create_time: number;
  update_time: number;
  payment_method?: string;
  shipping_provider?: string;
  tracking_number?: string;
  items: TikTokOrderItem[];
  shipping_address?: TikTokShippingAddress;
  buyer_message?: string;
  total_amount: number;
  shipping_fee?: number;
  buyer_email?: string;
}

/**
 * TikTok Webhook Payload
 */
export interface TikTokWebhookPayload {
  timestamp: number;
  type: TikTokEventType;
  shop_id: string;
  data: TikTokOrder;
}

/**
 * Webhook Verification Headers
 */
export interface WebhookHeaders {
  'x-tiktok-shop-signature': string;
  'x-tiktok-shop-timestamp': string;
}

/**
 * Database Order Record
 */
export interface OrderRecord {
  id: number;
  order_id: string;
  shop_id: string;
  event_type: TikTokEventType;
  order_status: TikTokOrderStatus;
  order_data: TikTokOrder;
  processed: boolean;
  created_at: Date;
  updated_at: Date;
  error_message?: string;
}
