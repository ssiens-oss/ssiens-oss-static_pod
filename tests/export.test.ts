import { describe, it, expect } from 'vitest';
import { queueToCSV, logsToCSV, queueToJSON, logsToJSON } from '../utils/export';
import { LogType } from '../types';

describe('export utilities', () => {
  const mockQueue = [
    { id: 'q1', name: 'Drop1 - T-Shirt', status: 'completed' as const },
    { id: 'q2', name: 'Drop2 - Hoodie', status: 'pending' as const }
  ];

  const mockLogs = [
    { id: 'l1', timestamp: '14:23:45', message: 'Test message', type: LogType.INFO },
    { id: 'l2', timestamp: '14:23:46', message: 'Success message', type: LogType.SUCCESS }
  ];

  describe('queueToCSV', () => {
    it('should convert queue to CSV with headers', () => {
      const csv = queueToCSV(mockQueue);
      const lines = csv.split('\n');

      expect(lines[0]).toBe('Name,Status,ID');
      expect(lines.length).toBe(3); // header + 2 items
    });

    it('should properly quote queue item names', () => {
      const csv = queueToCSV(mockQueue);
      expect(csv).toContain('"Drop1 - T-Shirt"');
      expect(csv).toContain('"Drop2 - Hoodie"');
    });

    it('should include all queue data', () => {
      const csv = queueToCSV(mockQueue);
      expect(csv).toContain('completed');
      expect(csv).toContain('pending');
      expect(csv).toContain('q1');
      expect(csv).toContain('q2');
    });
  });

  describe('logsToCSV', () => {
    it('should convert logs to CSV with headers', () => {
      const csv = logsToCSV(mockLogs);
      const lines = csv.split('\n');

      expect(lines[0]).toBe('Timestamp,Type,Message,ID');
      expect(lines.length).toBe(3); // header + 2 logs
    });

    it('should properly quote log messages', () => {
      const csv = logsToCSV(mockLogs);
      expect(csv).toContain('"Test message"');
      expect(csv).toContain('"Success message"');
    });

    it('should escape quotes in messages', () => {
      const logsWithQuotes = [
        { id: 'l1', timestamp: '14:23:45', message: 'Message with "quotes"', type: LogType.INFO }
      ];
      const csv = logsToCSV(logsWithQuotes);
      expect(csv).toContain('""quotes""');
    });

    it('should include all log data', () => {
      const csv = logsToCSV(mockLogs);
      expect(csv).toContain('14:23:45');
      expect(csv).toContain('INFO');
      expect(csv).toContain('SUCCESS');
    });
  });

  describe('queueToJSON', () => {
    it('should convert queue to formatted JSON', () => {
      const json = queueToJSON(mockQueue);
      const parsed = JSON.parse(json);

      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed).toHaveLength(2);
      expect(parsed[0]).toEqual(mockQueue[0]);
    });

    it('should format JSON with indentation', () => {
      const json = queueToJSON(mockQueue);
      expect(json).toContain('\n  ');
    });
  });

  describe('logsToJSON', () => {
    it('should convert logs to formatted JSON', () => {
      const json = logsToJSON(mockLogs);
      const parsed = JSON.parse(json);

      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed).toHaveLength(2);
      expect(parsed[0]).toEqual(mockLogs[0]);
    });

    it('should format JSON with indentation', () => {
      const json = logsToJSON(mockLogs);
      expect(json).toContain('\n  ');
    });
  });
});
