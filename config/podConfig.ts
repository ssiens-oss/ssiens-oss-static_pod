import { EngineConfig, EditorState } from '../types';

/**
 * Centralized POD Studio Configuration
 * Contains all app constants, defaults, and configuration
 */

// ==================== APP BRANDING ====================
export const APP_BRANDING = {
  name: 'StaticWaves',
  version: '6.0',
  fullName: 'StaticWaves POD Studio',
  tagline: 'POD STUDIO v6.0'
} as const;

// ==================== DEFAULT CONFIGURATION ====================
export const DEFAULT_ENGINE_CONFIG: EngineConfig = {
  dropName: 'Drop7',
  designCount: 10,
  blueprintId: 6,
  providerId: 1,
  batchList: ''
};

export const DEFAULT_EDITOR_STATE: EditorState = {
  scale: 1,
  translateX: 0,
  translateY: 0
};

// ==================== POD WORKFLOW MESSAGES ====================
export const POD_WORKFLOW_MESSAGES = [
  "Initializing generative module...",
  "Loading blueprints from manifest...",
  "Connecting to Provider API (ID: 1)...",
  "Asset compilation started...",
  "Rendering layers with composite mode: MULTIPLY",
  "Exporting high-res PNG (300 DPI)...",
  "Verifying output integrity...",
  "Preparing JSON payload for Printify..."
] as const;

// ==================== EDITOR CONTROLS ====================
export const EDITOR_ZOOM_FACTOR = {
  IN: 1.1,
  OUT: 0.9
} as const;

export const EDITOR_MOVE_STEP = 10;

// ==================== SIMULATION TIMING ====================
export const SIMULATION_TIMING = {
  INITIAL_DELAY: 600,
  IMAGE_GENERATION: 800,
  MOCKUP_PHASE: 300,
  MOCKUP_PHASES_COUNT: 3,
  MOCKUP_WAIT: 1000,
  API_AUTH: 500,
  WORKFLOW_STEP: 400
} as const;

// ==================== PROGRESS MILESTONES ====================
export const PROGRESS_MILESTONES = {
  START: 5,
  DESIGN_COMPLETE: 25,
  MOCKUP_COMPLETE: 50,
  WORKFLOW_START: 50,
  WORKFLOW_STEP_INCREMENT: 5,
  COMPLETE: 100
} as const;

// ==================== IMAGE SEEDS ====================
export const IMAGE_CONFIG = {
  DESIGN_SEED_RANGE: 1000,
  MOCKUP_SEED_OFFSET: 500,
  DESIGN_SIZE: 800,
  MOCKUP_SIZE: 800
} as const;

// ==================== QUEUE STATUS ====================
export type QueueStatus = 'pending' | 'uploading' | 'completed' | 'failed';

// ==================== HELPER FUNCTIONS ====================
export const getDesignImageUrl = (seed: number): string =>
  `https://picsum.photos/seed/${seed}/${IMAGE_CONFIG.DESIGN_SIZE}/${IMAGE_CONFIG.DESIGN_SIZE}`;

export const getMockupImageUrl = (seed: number): string =>
  `https://picsum.photos/seed/${seed + IMAGE_CONFIG.MOCKUP_SEED_OFFSET}/${IMAGE_CONFIG.MOCKUP_SIZE}/${IMAGE_CONFIG.MOCKUP_SIZE}`;

export const generateImageSeed = (): number =>
  Math.floor(Math.random() * IMAGE_CONFIG.DESIGN_SEED_RANGE);
