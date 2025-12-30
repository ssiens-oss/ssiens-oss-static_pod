import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  generateId,
  timestamp,
  sleep,
  createLogEntry,
  parseBatchList,
  calculateBatchProgress
} from '../utils/podUtils';
import { LogType } from '../types';

describe('podUtils', () => {
  describe('generateId', () => {
    it('should generate a non-empty string', () => {
      const id = generateId();
      expect(id).toBeTruthy();
      expect(typeof id).toBe('string');
      expect(id.length).toBeGreaterThan(0);
    });

    it('should generate unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
    });
  });

  describe('timestamp', () => {
    it('should return a time string in HH:MM:SS format', () => {
      const time = timestamp();
      expect(time).toMatch(/^\d{1,2}:\d{2}:\d{2}$/);
    });
  });

  describe('sleep', () => {
    it('should resolve after specified time', async () => {
      const start = Date.now();
      await sleep(100);
      const end = Date.now();
      expect(end - start).toBeGreaterThanOrEqual(95); // Allow small margin
    });
  });

  describe('createLogEntry', () => {
    it('should create a log entry with all required fields', () => {
      const message = 'Test message';
      const entry = createLogEntry(message);

      expect(entry).toHaveProperty('id');
      expect(entry).toHaveProperty('timestamp');
      expect(entry).toHaveProperty('message', message);
      expect(entry).toHaveProperty('type', LogType.INFO);
    });

    it('should respect custom log type', () => {
      const entry = createLogEntry('Error message', LogType.ERROR);
      expect(entry.type).toBe(LogType.ERROR);
    });

    it('should generate unique IDs for each entry', () => {
      const entry1 = createLogEntry('Message 1');
      const entry2 = createLogEntry('Message 2');
      expect(entry1.id).not.toBe(entry2.id);
    });
  });

  describe('parseBatchList', () => {
    it('should parse comma-separated drops', () => {
      const result = parseBatchList('Drop1, Drop2, Drop3');
      expect(result).toEqual(['Drop1', 'Drop2', 'Drop3']);
    });

    it('should handle extra spaces', () => {
      const result = parseBatchList('  Drop1  ,  Drop2  ,  Drop3  ');
      expect(result).toEqual(['Drop1', 'Drop2', 'Drop3']);
    });

    it('should filter empty strings', () => {
      const result = parseBatchList('Drop1,,Drop2,  ,Drop3');
      expect(result).toEqual(['Drop1', 'Drop2', 'Drop3']);
    });

    it('should return empty array for empty input', () => {
      const result = parseBatchList('');
      expect(result).toEqual([]);
    });

    it('should handle single drop', () => {
      const result = parseBatchList('SingleDrop');
      expect(result).toEqual(['SingleDrop']);
    });
  });

  describe('calculateBatchProgress', () => {
    it('should calculate 0% progress at start', () => {
      const progress = calculateBatchProgress(0, 3, 0);
      expect(progress).toBe(0);
    });

    it('should calculate correct progress for first batch midway', () => {
      const progress = calculateBatchProgress(0, 3, 50);
      expect(progress).toBeCloseTo(16.67, 1);
    });

    it('should calculate correct progress for second batch start', () => {
      const progress = calculateBatchProgress(1, 3, 0);
      expect(progress).toBeCloseTo(33.33, 1);
    });

    it('should calculate correct progress for second batch midway', () => {
      const progress = calculateBatchProgress(1, 3, 50);
      expect(progress).toBeCloseTo(50, 1);
    });

    it('should calculate 100% progress at end', () => {
      const progress = calculateBatchProgress(2, 3, 100);
      expect(progress).toBe(100);
    });

    it('should handle single batch', () => {
      const progress = calculateBatchProgress(0, 1, 50);
      expect(progress).toBe(50);
    });
  });
});
