-- TikTok Orders Table
CREATE TABLE IF NOT EXISTS tiktok_orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(255) UNIQUE NOT NULL,
    shop_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    order_status VARCHAR(100) NOT NULL,
    order_data JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    CONSTRAINT unique_order_event UNIQUE(order_id, event_type, updated_at)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_order_id ON tiktok_orders(order_id);
CREATE INDEX IF NOT EXISTS idx_shop_id ON tiktok_orders(shop_id);
CREATE INDEX IF NOT EXISTS idx_order_status ON tiktok_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_processed ON tiktok_orders(processed);
CREATE INDEX IF NOT EXISTS idx_created_at ON tiktok_orders(created_at);
CREATE INDEX IF NOT EXISTS idx_event_type ON tiktok_orders(event_type);

-- Webhook Events Log Table (for debugging and auditing)
CREATE TABLE IF NOT EXISTS webhook_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE,
    shop_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    signature VARCHAR(512),
    timestamp BIGINT,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    success BOOLEAN DEFAULT FALSE,
    error_message TEXT
);

-- Indexes for webhook events
CREATE INDEX IF NOT EXISTS idx_webhook_shop_id ON webhook_events(shop_id);
CREATE INDEX IF NOT EXISTS idx_webhook_event_type ON webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_received_at ON webhook_events(received_at);
CREATE INDEX IF NOT EXISTS idx_webhook_processed ON webhook_events(processed);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_tiktok_orders_updated_at
    BEFORE UPDATE ON tiktok_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Order Processing Queue View (for monitoring)
CREATE OR REPLACE VIEW order_processing_queue AS
SELECT
    id,
    order_id,
    shop_id,
    event_type,
    order_status,
    processed,
    error_message,
    created_at,
    updated_at,
    (order_data->>'total_amount')::decimal as total_amount,
    jsonb_array_length(order_data->'items') as item_count
FROM tiktok_orders
ORDER BY created_at DESC;

-- Order Statistics View
CREATE OR REPLACE VIEW order_statistics AS
SELECT
    shop_id,
    order_status,
    COUNT(*) as order_count,
    SUM((order_data->>'total_amount')::decimal) as total_revenue,
    AVG((order_data->>'total_amount')::decimal) as avg_order_value,
    MIN(created_at) as first_order,
    MAX(created_at) as last_order
FROM tiktok_orders
GROUP BY shop_id, order_status;
