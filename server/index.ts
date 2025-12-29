import express, { Request, Response } from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Health Check
app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    message: 'StaticWaves POD API is running',
    timestamp: new Date().toISOString()
  });
});

// Get Providers
app.get('/api/providers', (req: Request, res: Response) => {
  res.json([
    { id: 1, name: 'Printify' },
    { id: 2, name: 'Printful' },
    { id: 3, name: 'Custom Provider' }
  ]);
});

// Get Blueprints
app.get('/api/blueprints', (req: Request, res: Response) => {
  res.json([
    { id: 1, name: 'T-Shirt (Front)', category: 'apparel' },
    { id: 2, name: 'T-Shirt (Back)', category: 'apparel' },
    { id: 3, name: 'Hoodie', category: 'apparel' },
    { id: 4, name: 'Mug (11oz)', category: 'drinkware' },
    { id: 5, name: 'Poster', category: 'prints' },
    { id: 6, name: 'Canvas', category: 'prints' }
  ]);
});

// Generate Design (Placeholder)
app.post('/api/design/generate', async (req: Request, res: Response) => {
  const { prompt, dropName, blueprintId, style } = req.body;

  // Simulate processing delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Return mock URLs (in production, this would call AI service)
  res.json({
    designUrl: `https://picsum.photos/seed/${Date.now()}/800/800`,
    mockupUrl: `https://picsum.photos/seed/${Date.now() + 1000}/800/800`,
    designId: `design_${Date.now()}`
  });
});

// Upload to Provider (Placeholder)
app.post('/api/provider/upload', async (req: Request, res: Response) => {
  const { designUrl, mockupUrl, dropName, providerId, blueprintId } = req.body;

  // Simulate upload delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  // Random success/failure for demo
  const success = Math.random() > 0.1;

  if (success) {
    res.json({
      productId: `prod_${Date.now()}`,
      status: 'success',
      message: `Successfully uploaded ${dropName} to provider ${providerId}`
    });
  } else {
    res.status(500).json({
      productId: null,
      status: 'failed',
      message: 'Failed to upload to provider'
    });
  }
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: any) => {
  console.error('Error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not found',
    message: `Route ${req.method} ${req.path} not found`
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 StaticWaves POD API running on http://localhost:${PORT}`);
  console.log(`📡 Health check: http://localhost:${PORT}/api/health`);
});

export default app;
