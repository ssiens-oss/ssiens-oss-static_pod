/**
 * Music API Service - Frontend client for StaticWaves Music API
 */

interface MusicSpec {
  bpm: number;
  key: string;
  duration: number;
  vibe: {
    energy: number;
    dark: number;
    dreamy: number;
    aggressive: number;
  };
  genre_mix: {
    [key: string]: number;
  };
  instruments: {
    [key: string]: string;
  };
  stems: boolean;
  seed?: number;
}

interface JobStatus {
  job_id: string;
  status: string;
  progress: number;
  message?: string;
  output_urls?: {
    [key: string]: string;
  };
}

interface GenerateResponse {
  job_id: string;
  status: string;
  credits_charged: string;
  estimated_time: string;
}


const API_BASE = import.meta.env.VITE_MUSIC_API_URL || 'http://localhost:8000';


export async function generateMusic(spec: MusicSpec): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(spec),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate music');
  }

  return response.json();
}


export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await fetch(`${API_BASE}/status/${jobId}`);

  if (!response.ok) {
    throw new Error('Failed to get job status');
  }

  return response.json();
}


export function getDownloadUrl(jobId: string, fileType: string = 'mix'): string {
  return `${API_BASE}/download/${jobId}/${fileType}`;
}


/**
 * Poll job status until completion
 */
export async function waitForCompletion(
  jobId: string,
  onProgress?: (progress: number) => void
): Promise<JobStatus> {
  return new Promise((resolve, reject) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);

        if (onProgress) {
          onProgress(status.progress);
        }

        if (status.status === 'completed') {
          clearInterval(pollInterval);
          resolve(status);
        } else if (status.status === 'failed') {
          clearInterval(pollInterval);
          reject(new Error(status.message || 'Music generation failed'));
        }
      } catch (error) {
        clearInterval(pollInterval);
        reject(error);
      }
    }, 2000); // Poll every 2 seconds

    // Timeout after 5 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      reject(new Error('Music generation timed out'));
    }, 5 * 60 * 1000);
  });
}


/**
 * Generate music and wait for completion
 */
export async function generateAndWait(
  spec: MusicSpec,
  onProgress?: (progress: number) => void
): Promise<{ jobId: string; audioUrl: string; stems: string[] }> {
  // Start generation
  const { job_id } = await generateMusic(spec);

  // Wait for completion
  const status = await waitForCompletion(job_id, onProgress);

  // Get audio URL
  const audioUrl = getDownloadUrl(job_id, 'mix');

  // Get stem names
  const stems = status.output_urls
    ? Object.keys(status.output_urls).filter(k => k !== 'mix')
    : [];

  return {
    jobId: job_id,
    audioUrl,
    stems,
  };
}
