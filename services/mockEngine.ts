import { LogType, LogEntry, QueueItem } from '../types';
import {
  POD_WORKFLOW_MESSAGES,
  SIMULATION_TIMING,
  PROGRESS_MILESTONES,
  getDesignImageUrl,
  getMockupImageUrl,
  generateImageSeed
} from '../config/podConfig';
import {
  generateId,
  createLogEntry,
  sleep
} from '../utils/podUtils';

type LogCallback = (entry: LogEntry) => void;
type ProgressCallback = (val: number) => void;
type QueueCallback = (item: QueueItem) => void;
type ImageCallback = (type: 'design' | 'mockup', url: string) => void;

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
        onLog(createLogEntry(msg, type));
    };

    if (shouldStop()) return;

    addLog(`🚀 Starting ${isBatch ? 'BATCH' : 'SINGLE'} process for: ${dropName}`, LogType.INFO);
    onProgress(PROGRESS_MILESTONES.START);
    await sleep(SIMULATION_TIMING.INITIAL_DELAY);

    // Simulate Image Generation
    addLog(`Creating design assets for ${dropName}...`, LogType.INFO);
    await sleep(SIMULATION_TIMING.IMAGE_GENERATION);

    // Update Design Preview (Random Art)
    const designId = generateImageSeed();
    onImage('design', getDesignImageUrl(designId));
    addLog(`Generated: design_${dropName}_v1.png`, LogType.SUCCESS);
    onProgress(PROGRESS_MILESTONES.DESIGN_COMPLETE);

    if (shouldStop()) return;
    await sleep(SIMULATION_TIMING.MOCKUP_WAIT);

    // Simulate Mockup Generation
    addLog("Applying design to product mockup (Blueprint 6)...", LogType.INFO);
    for (let i = 0; i < SIMULATION_TIMING.MOCKUP_PHASES_COUNT; i++) {
        addLog(`Rendering displacement map phase ${i+1}/${SIMULATION_TIMING.MOCKUP_PHASES_COUNT}...`, LogType.INFO);
        await sleep(SIMULATION_TIMING.MOCKUP_PHASE);
    }

    // Update Mockup Preview
    onImage('mockup', getMockupImageUrl(designId));
    addLog(`Generated: mockup_${dropName}_front.png`, LogType.SUCCESS);
    onProgress(PROGRESS_MILESTONES.MOCKUP_COMPLETE);

    if (shouldStop()) return;

    // Simulate API Upload logic
    addLog("Authenticating with Printify API...", LogType.WARNING);
    await sleep(SIMULATION_TIMING.API_AUTH);

    const queueId = generateId();
    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'pending' });

    addLog("Upload session established. Streaming assets...", LogType.INFO);
    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'uploading' });

    // Simulate workflow messages
    for (let i = 0; i < POD_WORKFLOW_MESSAGES.length; i++) {
        if (shouldStop()) return;
        addLog(POD_WORKFLOW_MESSAGES[i], LogType.INFO);
        onProgress(PROGRESS_MILESTONES.WORKFLOW_START + (i * PROGRESS_MILESTONES.WORKFLOW_STEP_INCREMENT));
        await sleep(SIMULATION_TIMING.WORKFLOW_STEP);
    }

    onQueue({ id: queueId, name: `${dropName} - T-Shirt`, status: 'completed' });
    addLog(`✅ Job Complete for ${dropName}`, LogType.SUCCESS);
    onProgress(PROGRESS_MILESTONES.COMPLETE);
};