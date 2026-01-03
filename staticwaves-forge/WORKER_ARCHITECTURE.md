# StaticWaves Forge - Worker Architecture

## System Overview

StaticWaves Forge uses a distributed worker architecture for scalable 3D asset generation:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Web GUI   │─────▶│  API Server │─────▶│Redis Queue  │─────▶│   Workers   │
│  (Next.js)  │      │  (FastAPI)  │      │  (Bull/RQ)  │      │  (Blender)  │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
       │                    │                     │                    │
       │              WebSocket                   │                    │
       └────────────────────┴─────────────────────┴────────────────────┘
                         Real-time Progress Updates
```

## Components

### 1. API Server (FastAPI)
- **Role**: Request validation, job creation, status tracking
- **Endpoints**:
  - `POST /api/generate/` - Create generation job
  - `GET /api/jobs/{job_id}` - Get job status
  - `WS /api/jobs/{job_id}/stream` - Real-time progress
- **Responsibilities**:
  - Validate generation requests
  - Enqueue jobs to Redis
  - Track job metadata
  - Serve completed assets

### 2. Redis Queue
- **Role**: Distributed job queue with priority support
- **Features**:
  - Job persistence
  - Priority queues (urgent, normal, low)
  - Failed job retry with exponential backoff
  - Job timeout handling
- **Queues**:
  - `generation:high` - Priority jobs
  - `generation:normal` - Standard jobs
  - `generation:low` - Batch jobs
  - `generation:failed` - Failed jobs for retry

### 3. Worker System
- **Role**: Execute Blender generation scripts
- **Types**:
  - **RunPod GPU Workers** - Cloud GPU instances for production
  - **Local Workers** - Development/testing on local machines
- **Worker Process**:
  1. Poll Redis queue for jobs
  2. Download AI model weights (if needed)
  3. Execute Blender Python script
  4. Upload generated assets to storage
  5. Update job status with progress
  6. Clean up temporary files

### 4. Blender Generation Engine
- **Role**: Generate 3D assets using AI models
- **Pipeline**:
  ```
  Text Prompt → Text2Mesh AI → Blender Processing → Export
                     ↓              ↓                  ↓
                 Point Cloud    Rigging/UV       GLB/FBX/OBJ
                               Textures/LODs
  ```
- **Components**:
  - **text2mesh.py** - AI model integration (Shap-E, Point-E)
  - **mesh_processor.py** - Mesh cleanup, optimization
  - **rigger.py** - Auto-rigging with Rigify
  - **texture_generator.py** - UV unwrapping and texture baking
  - **lod_generator.py** - LOD chain generation
  - **exporter.py** - Multi-format export

## AI Models Integration

### Primary Models:
1. **Shap-E** (OpenAI) - Text/Image to 3D
   - Fast generation (~10-15 seconds)
   - Good for props and simple objects
   - Integrated via `transformers` library

2. **Point-E** (OpenAI) - Point cloud generation
   - Higher quality for characters
   - Longer generation time (~1-2 minutes)

3. **ControlNet + Depth** - Texture generation
   - Generate PBR textures from description
   - Albedo, Normal, Roughness, Metallic maps

### Fallback Strategy:
```python
try:
    # Try Shap-E (fast)
    result = generate_with_shap_e(prompt)
except:
    # Fallback to Point-E (quality)
    result = generate_with_point_e(prompt)
```

## Job Lifecycle

```
1. QUEUED      - Job created, waiting for worker
   ↓
2. ASSIGNED    - Worker claimed the job
   ↓
3. DOWNLOADING - Loading AI models/weights
   ↓
4. GENERATING  - AI model generating base mesh (10-20%)
   ↓
5. PROCESSING  - Blender processing pipeline (20-60%)
   │  ├─ Mesh cleanup
   │  ├─ UV unwrapping
   │  ├─ Rigging (if enabled)
   │  └─ Texture generation
   ↓
6. EXPORTING   - Multi-format export (60-80%)
   ↓
7. UPLOADING   - Upload to storage (80-95%)
   ↓
8. FINALIZING  - Metadata generation (95-100%)
   ↓
9. COMPLETED   - Job finished, assets ready
```

## File Storage

### Development (Local):
```
/workspace/generated_assets/
  ├── {job_id}/
      ├── model.glb
      ├── model.fbx
      ├── model.obj
      ├── textures/
      │   ├── albedo.png
      │   ├── normal.png
      │   └── roughness.png
      └── metadata.json
```

### Production (S3/Cloudflare R2):
```
s3://staticwaves-assets/
  ├── {job_id}/
      └── [same structure as above]
```

## Worker Configuration

### Environment Variables:
```bash
# Worker Identity
WORKER_ID=worker-gpu-1
WORKER_TYPE=runpod  # or "local"

# Queue Configuration
REDIS_URL=redis://localhost:6379
QUEUE_NAME=generation:normal

# AI Models
MODEL_CACHE_DIR=/workspace/models
USE_SHAP_E=true
USE_POINT_E=true

# Blender
BLENDER_PATH=/usr/local/blender/blender
BLENDER_PYTHON=/usr/local/blender/python/bin/python3

# Storage
STORAGE_TYPE=local  # or "s3"
STORAGE_PATH=/workspace/generated_assets
S3_BUCKET=staticwaves-assets
S3_REGION=us-east-1

# Performance
MAX_CONCURRENT_JOBS=1  # Per worker
JOB_TIMEOUT=600  # 10 minutes
CLEANUP_TEMP_FILES=true
```

## Scaling Strategy

### Horizontal Scaling:
- Deploy multiple RunPod workers
- Each worker polls same Redis queue
- Auto-scale based on queue depth

### Queue Monitoring:
```python
if queue_depth > 10:
    spawn_additional_worker()
elif queue_depth == 0 and idle_time > 300:
    shutdown_worker()
```

### Cost Optimization:
- Use spot instances for batch jobs
- Scale down to 0 during off-peak
- Cache AI models across workers

## Error Handling

### Retry Logic:
```python
MAX_RETRIES = 3
BACKOFF_MULTIPLIER = 2

if job.attempts < MAX_RETRIES:
    delay = BACKOFF_MULTIPLIER ** job.attempts
    retry_job_after(job, delay)
else:
    mark_as_failed(job)
```

### Failure Categories:
1. **Transient** (retry)
   - Network timeouts
   - GPU OOM (reduce poly budget)
   - Temporary model loading failures

2. **Permanent** (fail immediately)
   - Invalid prompt
   - Unsupported asset type
   - Missing required parameters

## Monitoring & Observability

### Metrics:
- Jobs/minute processed
- Average generation time
- GPU utilization %
- Queue depth by priority
- Success/failure rate
- Worker health status

### Logging:
```python
logger.info(f"Job {job_id}: Starting generation")
logger.info(f"Job {job_id}: Progress 25% - Mesh generated")
logger.info(f"Job {job_id}: Progress 50% - UV unwrapped")
logger.info(f"Job {job_id}: Progress 75% - Rigging complete")
logger.info(f"Job {job_id}: Completed in 45s")
```

## Security

### Worker Sandboxing:
- Run Blender in isolated container
- Limit file system access
- Restrict network access to queue + storage only
- Scan uploaded assets for malicious content

### Authentication:
- Workers authenticate with API using JWT
- Rate limiting on job creation
- User quotas enforced

## Future Enhancements

1. **Priority Queue System** - Premium users get faster processing
2. **Warm Workers** - Keep models loaded in memory
3. **Batch Optimization** - Process similar prompts together
4. **Progressive Generation** - Return low-res preview quickly
5. **Model Fine-tuning** - Custom models for specific art styles
6. **Multi-GPU Support** - Parallelize generation stages

---

**Version**: 1.0.0
**Last Updated**: 2026-01-03
