-- Production POD Engine Database Schema
-- Supports PostgreSQL

-- Job tracking table
CREATE TABLE IF NOT EXISTS pod_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 0,
    request JSONB NOT NULL,
    result JSONB,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    worker_id VARCHAR(255),

    CONSTRAINT valid_status CHECK (status IN ('pending', 'queued', 'processing', 'completed', 'failed', 'retrying'))
);

-- Generated images table
CREATE TABLE IF NOT EXISTS pod_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES pod_jobs(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    prompt TEXT NOT NULL,
    title VARCHAR(500),
    description TEXT,
    tags TEXT[],
    hash VARCHAR(64) UNIQUE,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_job_images (job_id),
    INDEX idx_image_hash (hash)
);

-- Products table
CREATE TABLE IF NOT EXISTS pod_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES pod_jobs(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES pod_images(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_product_id VARCHAR(255) NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    published_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_product_status CHECK (status IN ('draft', 'publishing', 'published', 'failed', 'archived')),
    INDEX idx_job_products (job_id),
    INDEX idx_image_products (image_id),
    INDEX idx_platform_product (platform, platform_product_id)
);

-- Worker health tracking
CREATE TABLE IF NOT EXISTS pod_workers (
    id VARCHAR(255) PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    current_job_id UUID REFERENCES pod_jobs(id) ON DELETE SET NULL,
    last_heartbeat TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    jobs_processed INTEGER NOT NULL DEFAULT 0,
    jobs_failed INTEGER NOT NULL DEFAULT 0,
    metadata JSONB,

    CONSTRAINT valid_worker_status CHECK (status IN ('idle', 'busy', 'offline', 'error'))
);

-- Execution metrics
CREATE TABLE IF NOT EXISTS pod_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(100) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(20,6) NOT NULL,
    labels JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_metric_type (metric_type, metric_name),
    INDEX idx_metric_timestamp (timestamp)
);

-- Job execution logs
CREATE TABLE IF NOT EXISTS pod_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES pod_jobs(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_log_level CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    INDEX idx_job_logs (job_id, timestamp),
    INDEX idx_log_level (level, timestamp)
);

-- Configuration store
CREATE TABLE IF NOT EXISTS pod_config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_status ON pod_jobs(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON pod_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workers_heartbeat ON pod_workers(last_heartbeat DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_pod_jobs_updated_at BEFORE UPDATE ON pod_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pod_products_updated_at BEFORE UPDATE ON pod_products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default configuration
INSERT INTO pod_config (key, value, description) VALUES
    ('max_concurrent_jobs', '5', 'Maximum number of concurrent jobs per worker'),
    ('job_timeout_seconds', '3600', 'Job timeout in seconds (1 hour)'),
    ('worker_heartbeat_interval', '30', 'Worker heartbeat interval in seconds'),
    ('dead_worker_threshold', '120', 'Consider worker dead after N seconds without heartbeat'),
    ('retry_delay_seconds', '60', 'Delay between job retries in seconds'),
    ('image_generation_timeout', '600', 'Timeout for image generation in seconds'),
    ('enable_auto_retry', 'true', 'Automatically retry failed jobs')
ON CONFLICT (key) DO NOTHING;
