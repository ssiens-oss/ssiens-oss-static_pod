/**
 * MashDeck Global State Store
 * Centralized state management using Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useStore = create(
  devtools(
    (set, get) => ({
      // ===== WebSocket State =====
      ws: null,
      wsConnected: false,
      wsReconnecting: false,

      connectWebSocket: () => {
        const ws = new WebSocket('ws://localhost:8080/ws');

        ws.onopen = () => {
          console.log('WebSocket connected');
          set({ ws, wsConnected: true, wsReconnecting: false });
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          get().handleWebSocketMessage(data);
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          set({ wsConnected: false });

          // Auto-reconnect after 3 seconds
          if (!get().wsReconnecting) {
            set({ wsReconnecting: true });
            setTimeout(() => {
              get().connectWebSocket();
            }, 3000);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          get().addNotification({
            type: 'error',
            message: 'WebSocket connection error'
          });
        };

        set({ ws });
      },

      disconnectWebSocket: () => {
        const { ws } = get();
        if (ws) {
          ws.close();
          set({ ws: null, wsConnected: false });
        }
      },

      handleWebSocketMessage: (data) => {
        const { type, ...payload } = data;

        switch (type) {
          case 'generation_started':
            get().updateGeneration(payload.job_id, { status: 'generating' });
            get().addNotification({
              type: 'info',
              message: 'Song generation started'
            });
            break;

          case 'generation_completed':
            get().updateGeneration(payload.job_id, {
              status: 'completed',
              output: payload.output
            });
            get().addNotification({
              type: 'success',
              message: 'Song generation completed!'
            });
            break;

          case 'generation_failed':
            get().updateGeneration(payload.job_id, {
              status: 'failed',
              error: payload.error
            });
            get().addNotification({
              type: 'error',
              message: `Generation failed: ${payload.error}`
            });
            break;

          case 'freestyle_generated':
            get().addNotification({
              type: 'success',
              message: 'Freestyle rap generated!'
            });
            break;

          case 'battle_round_completed':
            get().addNotification({
              type: 'info',
              message: 'Battle round completed'
            });
            break;

          case 'battle_ended':
            get().addNotification({
              type: 'success',
              message: `Battle ended! Winner: ${payload.winner}`
            });
            break;

          case 'settings_updated':
            set({ settings: payload.settings });
            break;

          default:
            console.log('Unknown WebSocket message type:', type);
        }
      },

      // ===== Generation State =====
      generations: {},

      addGeneration: (jobId, data) => {
        set((state) => ({
          generations: {
            ...state.generations,
            [jobId]: {
              ...data,
              status: 'queued',
              createdAt: new Date().toISOString()
            }
          }
        }));
      },

      updateGeneration: (jobId, updates) => {
        set((state) => ({
          generations: {
            ...state.generations,
            [jobId]: {
              ...state.generations[jobId],
              ...updates,
              updatedAt: new Date().toISOString()
            }
          }
        }));
      },

      clearGenerations: () => {
        set({ generations: {} });
      },

      // ===== Settings State =====
      settings: {
        theme: 'dark',
        notifications_enabled: true,
        auto_save: true,
        default_style: 'edm',
        default_bpm: 120
      },

      updateSettings: (newSettings) => {
        set((state) => ({
          settings: {
            ...state.settings,
            ...newSettings
          }
        }));
      },

      // ===== Notification State =====
      notifications: [],
      notificationId: 0,

      addNotification: (notification) => {
        const id = get().notificationId + 1;
        const newNotification = {
          id,
          ...notification,
          timestamp: new Date().toISOString()
        };

        set((state) => ({
          notifications: [...state.notifications, newNotification],
          notificationId: id
        }));

        // Auto-remove after 5 seconds
        setTimeout(() => {
          get().removeNotification(id);
        }, 5000);

        return id;
      },

      removeNotification: (id) => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id)
        }));
      },

      clearNotifications: () => {
        set({ notifications: [] });
      },

      // ===== Project State =====
      projects: [],
      currentProject: null,

      createProject: (name, type = 'song') => {
        const project = {
          id: `project_${Date.now()}`,
          name,
          type,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          data: {}
        };

        set((state) => ({
          projects: [...state.projects, project],
          currentProject: project
        }));

        get().addNotification({
          type: 'success',
          message: `Project "${name}" created`
        });

        return project;
      },

      updateProject: (projectId, updates) => {
        set((state) => ({
          projects: state.projects.map((p) =>
            p.id === projectId
              ? { ...p, ...updates, updatedAt: new Date().toISOString() }
              : p
          ),
          currentProject:
            state.currentProject?.id === projectId
              ? { ...state.currentProject, ...updates }
              : state.currentProject
        }));
      },

      deleteProject: (projectId) => {
        set((state) => ({
          projects: state.projects.filter((p) => p.id !== projectId),
          currentProject:
            state.currentProject?.id === projectId ? null : state.currentProject
        }));

        get().addNotification({
          type: 'info',
          message: 'Project deleted'
        });
      },

      setCurrentProject: (project) => {
        set({ currentProject: project });
      },

      // ===== Battle State =====
      battleActive: false,
      battleRounds: [],
      battleWinner: null,

      startBattle: () => {
        set({
          battleActive: true,
          battleRounds: [],
          battleWinner: null
        });
      },

      addBattleRound: (round) => {
        set((state) => ({
          battleRounds: [...state.battleRounds, round]
        }));
      },

      endBattle: (winner) => {
        set({
          battleActive: false,
          battleWinner: winner
        });
      },

      // ===== Freestyle State =====
      freestyleActive: false,
      freestyleMessages: [],

      startFreestyle: () => {
        set({
          freestyleActive: true,
          freestyleMessages: []
        });
      },

      addFreestyleMessage: (message) => {
        set((state) => ({
          freestyleMessages: [...state.freestyleMessages, message]
        }));
      },

      stopFreestyle: () => {
        set({
          freestyleActive: false
        });
      },

      // ===== Audio Player State =====
      currentAudio: null,
      isPlaying: false,
      currentTime: 0,
      duration: 0,

      setCurrentAudio: (audioPath) => {
        set({
          currentAudio: audioPath,
          isPlaying: false,
          currentTime: 0
        });
      },

      togglePlayback: () => {
        set((state) => ({
          isPlaying: !state.isPlaying
        }));
      },

      updatePlaybackTime: (time) => {
        set({ currentTime: time });
      },

      setDuration: (duration) => {
        set({ duration });
      },

      // ===== System Stats =====
      stats: {
        total_generations: 0,
        completed: 0,
        failed: 0,
        in_progress: 0,
        websocket_connections: 0
      },

      updateStats: (newStats) => {
        set({ stats: newStats });
      },

      // ===== Initialize =====
      initialize: () => {
        get().connectWebSocket();
      },

      // ===== Cleanup =====
      cleanup: () => {
        get().disconnectWebSocket();
      }
    }),
    { name: 'MashDeck Store' }
  )
);

export default useStore;
