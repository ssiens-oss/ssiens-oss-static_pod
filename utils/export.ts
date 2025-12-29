/**
 * Export utilities for downloading and saving designs
 */

export interface ExportOptions {
  filename: string;
  format: 'png' | 'jpg' | 'svg' | 'json';
  quality?: number; // 0-1 for jpg/png
}

/**
 * Download an image from a URL
 */
export const downloadImage = async (
  imageUrl: string,
  options: ExportOptions
): Promise<void> => {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${options.filename}.${options.format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Failed to download image:', error);
    throw new Error('Failed to download image. Please try again.');
  }
};

/**
 * Convert canvas to blob and download
 */
export const downloadCanvas = (
  canvas: HTMLCanvasElement,
  options: ExportOptions
): void => {
  canvas.toBlob(
    (blob) => {
      if (!blob) {
        throw new Error('Failed to create blob from canvas');
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${options.filename}.${options.format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
    `image/${options.format}`,
    options.quality || 0.95
  );
};

/**
 * Export design with transformations applied
 */
export const exportTransformedImage = async (
  imageUrl: string,
  transform: { scale: number; translateX: number; translateY: number },
  options: ExportOptions
): Promise<void> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';

    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }

      // Set canvas size to original image size
      canvas.width = img.width;
      canvas.height = img.height;

      // Apply transformations
      ctx.save();
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.scale(transform.scale, transform.scale);
      ctx.translate(transform.translateX, transform.translateY);
      ctx.translate(-canvas.width / 2, -canvas.height / 2);

      // Draw image
      ctx.drawImage(img, 0, 0);
      ctx.restore();

      // Download
      try {
        downloadCanvas(canvas, options);
        resolve();
      } catch (error) {
        reject(error);
      }
    };

    img.onerror = () => {
      reject(new Error('Failed to load image'));
    };

    img.src = imageUrl;
  });
};

/**
 * Export queue data as JSON
 */
export const exportQueueData = (
  queueData: any[],
  filename: string
): void => {
  const jsonStr = JSON.stringify(queueData, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Export logs as text file
 */
export const exportLogs = (
  logs: Array<{ timestamp: string; message: string; type: string }>,
  filename: string
): void => {
  const logText = logs
    .map((log) => `[${log.timestamp}] [${log.type}] ${log.message}`)
    .join('\n');

  const blob = new Blob([logText], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Copy image to clipboard
 */
export const copyImageToClipboard = async (imageUrl: string): Promise<void> => {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();

    await navigator.clipboard.write([
      new ClipboardItem({
        [blob.type]: blob,
      }),
    ]);
  } catch (error) {
    console.error('Failed to copy image:', error);
    throw new Error('Failed to copy image to clipboard');
  }
};
