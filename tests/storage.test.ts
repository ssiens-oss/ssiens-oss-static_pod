import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  saveConfig,
  loadConfig,
  saveQueue,
  loadQueue,
  saveLogs,
  loadLogs,
  clearAllStorage
} from '../utils/storage';
import { DEFAULT_ENGINE_CONFIG } from '../config/podConfig';
import { LogType } from '../types';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('storage utilities', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  describe('config persistence', () => {
    it('should save config to localStorage', () => {
      const config = { ...DEFAULT_ENGINE_CONFIG, dropName: 'TestDrop' };
      saveConfig(config);

      const stored = localStorageMock.getItem('pod_studio_config');
      expect(stored).toBeTruthy();
      expect(JSON.parse(stored!)).toEqual(config);
    });

    it('should load config from localStorage', () => {
      const config = { ...DEFAULT_ENGINE_CONFIG, dropName: 'TestDrop' };
      localStorageMock.setItem('pod_studio_config', JSON.stringify(config));

      const loaded = loadConfig();
      expect(loaded).toEqual(config);
    });

    it('should return null when no config exists', () => {
      const loaded = loadConfig();
      expect(loaded).toBeNull();
    });

    it('should return null for invalid JSON', () => {
      localStorageMock.setItem('pod_studio_config', 'invalid json');
      const loaded = loadConfig();
      expect(loaded).toBeNull();
    });
  });

  describe('queue persistence', () => {
    it('should save queue to localStorage', () => {
      const queue = [
        { id: 'q1', name: 'Drop1 - T-Shirt', status: 'completed' as const }
      ];
      saveQueue(queue);

      const stored = localStorageMock.getItem('pod_studio_queue');
      expect(stored).toBeTruthy();
      expect(JSON.parse(stored!)).toEqual(queue);
    });

    it('should load queue from localStorage', () => {
      const queue = [
        { id: 'q1', name: 'Drop1 - T-Shirt', status: 'completed' as const }
      ];
      localStorageMock.setItem('pod_studio_queue', JSON.stringify(queue));

      const loaded = loadQueue();
      expect(loaded).toEqual(queue);
    });

    it('should return empty array when no queue exists', () => {
      const loaded = loadQueue();
      expect(loaded).toEqual([]);
    });

    it('should return empty array for invalid JSON', () => {
      localStorageMock.setItem('pod_studio_queue', 'invalid json');
      const loaded = loadQueue();
      expect(loaded).toEqual([]);
    });
  });

  describe('logs persistence', () => {
    it('should save logs to localStorage', () => {
      const logs = [
        { id: 'l1', timestamp: '14:23:45', message: 'Test', type: LogType.INFO }
      ];
      saveLogs(logs);

      const stored = localStorageMock.getItem('pod_studio_logs');
      expect(stored).toBeTruthy();
      expect(JSON.parse(stored!)).toEqual(logs);
    });

    it('should only save last 100 logs', () => {
      const logs = Array.from({ length: 150 }, (_, i) => ({
        id: `l${i}`,
        timestamp: '14:23:45',
        message: `Message ${i}`,
        type: LogType.INFO
      }));
      saveLogs(logs);

      const stored = localStorageMock.getItem('pod_studio_logs');
      const parsed = JSON.parse(stored!);
      expect(parsed).toHaveLength(100);
      expect(parsed[0].message).toBe('Message 50'); // Should start from index 50
    });

    it('should load logs from localStorage', () => {
      const logs = [
        { id: 'l1', timestamp: '14:23:45', message: 'Test', type: LogType.INFO }
      ];
      localStorageMock.setItem('pod_studio_logs', JSON.stringify(logs));

      const loaded = loadLogs();
      expect(loaded).toEqual(logs);
    });

    it('should return empty array when no logs exist', () => {
      const loaded = loadLogs();
      expect(loaded).toEqual([]);
    });
  });

  describe('clearAllStorage', () => {
    it('should clear all POD storage keys', () => {
      localStorageMock.setItem('pod_studio_config', '{}');
      localStorageMock.setItem('pod_studio_queue', '[]');
      localStorageMock.setItem('pod_studio_logs', '[]');

      clearAllStorage();

      expect(localStorageMock.getItem('pod_studio_config')).toBeNull();
      expect(localStorageMock.getItem('pod_studio_queue')).toBeNull();
      expect(localStorageMock.getItem('pod_studio_logs')).toBeNull();
    });
  });
});
