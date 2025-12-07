import { LogType, LogEntry, QueueItem } from '../types';

type LogCallback = (entry: LogEntry) => void;
type ProgressCallback = (val: number) => void;
type QueueCallback = (item: QueueItem) => void;
type ImageCallback = (type: 'design' | 'mockup', url: string) => void;

const generateId = () => Math.random().toString(36).substr(2, 9);
const timestamp = () => new Date().toLocaleTimeString('en-US', { hour12: false });

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const MOCK_MESSAGES = [
    "Initializing generative module...",
    "Loading blueprints from manifest...",
    "Connecting to Provider API (ID: 1)...",
    "Asset compilation started...",
    "Rendering layers with composite mode: MULTIPLY",
    "Exporting high-res PNG (300 DPI)...",
    "Verifying output integrity...",
    "Preparing JSON payload for Printify..."
];

export const runSimulation = async (
    dropName: string,
    isBatch: boolean,
    onLog: LogCallback,
    onProgress: ProgressCallback,
    onQueue: QueueCallback,
    onImage: ImageCallback,
    shouldStop: () => boolean
) => {
    const addLog = (msg: string, type: LogType = LogType.INFO) => {
        onLog({
            id: generateId(),
            timestamp: timestamp(),
            message: msg,
            type
        });
    };

    if (shouldStop()) return;

    addLog(`🚀 Starting ${isBatch ? 'BATCH' : 'SINGLE'} process for: ${dropName}`, LogType.INFO);
    onProgress(5);
    await sleep(600);

    // Simulate Image Generation
    addLog(`Creating design assets for ${dropName}...`, LogType.INFO);
    await sleep(800);
    
    // Update Design Preview (Random Art)
    const designId = Math.floor(Math.random() * 1000);
    onImage('design', `https://picsum.photos/seed/${designId}/800/800`);
    addLog(`Generated: design_${dropName}_v1.png`, LogType.SUCCESS);
    onProgress(25);

    if (shouldStop()) return;
    await sleep(1000);

    // Simulate Mockup Generation
    addLog("Applying design to product mockup (Blueprint 6)...", LogType.INFO);
    for (let i = 0; i < 3; i++) {
        addLog(`Rendering displacement map phase ${i+1}/3...`, LogType.INFO);
        await sleep(300);
    }

    // Update Mockup Preview
    onImage('mockup', `https://picsum.photos/seed/${designId + 500}/800/800`); 
    addLog(`Generated: mockup_${dropName}_front.png`, LogType.SUCCESS);
    onProgress(50);

    if (shouldStop()) return;

    // Simulate API Upload logic
    addLog("Authenticating with Printify API...", LogType.WARNING);
    await sleep(500);
    
    const queueId = generateId();
    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'pending' });
    
    addLog("Upload session established. Streaming assets...", LogType.INFO);
    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'uploading' });
    
    // Simulate messages
    for (let i = 0; i < MOCK_MESSAGES.length; i++) {
        if (shouldStop()) return;
        addLog(MOCK_MESSAGES[i], LogType.INFO);
        onProgress(50 + (i * 5));
        await sleep(400);
    }

    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'completed' });
    addLog(`✅ Job Complete for ${dropName}`, LogType.SUCCESS);
    onProgress(100);
};