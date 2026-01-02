/**
 * StaticWaves Music Integration for Unity
 * Real-time adaptive music system for Unity games
 *
 * Usage:
 * 1. Add this script to a GameObject in your scene
 * 2. Configure server URL in inspector
 * 3. Call SetMusicContext() to change music based on gameplay
 */

using UnityEngine;
using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace StaticWaves
{
    /// <summary>
    /// Music context that drives adaptive music
    /// </summary>
    [Serializable]
    public class MusicContext
    {
        [Range(0f, 1f)] public float energy = 0.5f;
        [Range(0f, 1f)] public float tension = 0.5f;
        [Range(0f, 1f)] public float darkness = 0.5f;
        [Range(0f, 1f)] public float complexity = 0.5f;

        public string ToJson()
        {
            return JsonUtility.ToJson(this);
        }
    }

    /// <summary>
    /// Main StaticWaves music controller
    /// </summary>
    public class StaticWavesMusic : MonoBehaviour
    {
        [Header("Server Configuration")]
        [Tooltip("WebSocket server URL")]
        public string serverUrl = "ws://localhost:8765";

        [Tooltip("Automatically connect on start")]
        public bool autoConnect = true;

        [Header("Music State")]
        [Tooltip("Current music context")]
        public MusicContext currentContext = new MusicContext();

        [Tooltip("Transition speed for context changes (seconds)")]
        [Range(0.1f, 5f)]
        public float transitionSpeed = 1.0f;

        [Header("Debug")]
        public bool showDebugLogs = true;

        // Private members
        private ClientWebSocket webSocket;
        private CancellationTokenSource cancellationToken;
        private AudioSource audioSource;
        private Queue<float[]> audioBufferQueue = new Queue<float[]>();
        private object queueLock = new object();
        private bool isConnected = false;
        private MusicContext targetContext;
        private float[] currentAudioBuffer;
        private int bufferIndex = 0;

        // Constants
        private const int SAMPLE_RATE = 32000;
        private const int BUFFER_SIZE = 1024;

        #region Unity Lifecycle

        private void Awake()
        {
            // Add audio source if not present
            audioSource = GetComponent<AudioSource>();
            if (audioSource == null)
            {
                audioSource = gameObject.AddComponent<AudioSource>();
            }

            audioSource.loop = true;
            audioSource.playOnAwake = false;

            targetContext = currentContext;
        }

        private void Start()
        {
            if (autoConnect)
            {
                Connect();
            }
        }

        private void Update()
        {
            // Smooth transition to target context
            if (targetContext != currentContext)
            {
                float t = Time.deltaTime / transitionSpeed;
                currentContext.energy = Mathf.Lerp(currentContext.energy, targetContext.energy, t);
                currentContext.tension = Mathf.Lerp(currentContext.tension, targetContext.tension, t);
                currentContext.darkness = Mathf.Lerp(currentContext.darkness, targetContext.darkness, t);
                currentContext.complexity = Mathf.Lerp(currentContext.complexity, targetContext.complexity, t);

                SendControlUpdate();
            }
        }

        private void OnDestroy()
        {
            Disconnect();
        }

        private void OnApplicationQuit()
        {
            Disconnect();
        }

        #endregion

        #region Public API

        /// <summary>
        /// Connect to StaticWaves server
        /// </summary>
        public async void Connect()
        {
            if (isConnected)
            {
                Log("Already connected");
                return;
            }

            try
            {
                webSocket = new ClientWebSocket();
                cancellationToken = new CancellationTokenSource();

                await webSocket.ConnectAsync(new Uri(serverUrl), cancellationToken.Token);
                isConnected = true;

                Log($"✓ Connected to {serverUrl}");

                // Start receiving audio
                _ = ReceiveAudioLoop();

                // Start playing
                if (!audioSource.isPlaying)
                {
                    audioSource.Play();
                }

                // Send initial context
                SendControlUpdate();
            }
            catch (Exception e)
            {
                LogError($"Connection failed: {e.Message}");
                isConnected = false;
            }
        }

        /// <summary>
        /// Disconnect from server
        /// </summary>
        public void Disconnect()
        {
            if (!isConnected) return;

            try
            {
                cancellationToken?.Cancel();
                webSocket?.Dispose();
                isConnected = false;

                Log("✓ Disconnected");
            }
            catch (Exception e)
            {
                LogError($"Disconnect error: {e.Message}");
            }
        }

        /// <summary>
        /// Set music context (instant change)
        /// </summary>
        public void SetMusicContext(MusicContext context)
        {
            currentContext = context;
            targetContext = context;
            SendControlUpdate();
        }

        /// <summary>
        /// Set music context (smooth transition)
        /// </summary>
        public void TransitionToContext(MusicContext context)
        {
            targetContext = context;
        }

        /// <summary>
        /// Quick presets for common game states
        /// </summary>
        public void SetExploration()
        {
            TransitionToContext(new MusicContext
            {
                energy = 0.3f,
                tension = 0.1f,
                darkness = 0.2f,
                complexity = 0.4f
            });
        }

        public void SetCombat()
        {
            TransitionToContext(new MusicContext
            {
                energy = 0.9f,
                tension = 0.8f,
                darkness = 0.6f,
                complexity = 0.7f
            });
        }

        public void SetBoss()
        {
            TransitionToContext(new MusicContext
            {
                energy = 1.0f,
                tension = 0.95f,
                darkness = 0.8f,
                complexity = 0.9f
            });
        }

        public void SetPuzzle()
        {
            TransitionToContext(new MusicContext
            {
                energy = 0.4f,
                tension = 0.5f,
                darkness = 0.3f,
                complexity = 0.6f
            });
        }

        public void SetVictory()
        {
            TransitionToContext(new MusicContext
            {
                energy = 0.7f,
                tension = 0.2f,
                darkness = 0.1f,
                complexity = 0.5f
            });
        }

        #endregion

        #region Private Methods

        private async void SendControlUpdate()
        {
            if (!isConnected || webSocket == null) return;

            try
            {
                string json = currentContext.ToJson();
                byte[] buffer = Encoding.UTF8.GetBytes(json);

                await webSocket.SendAsync(
                    new ArraySegment<byte>(buffer),
                    WebSocketMessageType.Text,
                    true,
                    cancellationToken.Token
                );

                Log($"Sent context: E={currentContext.energy:F2} T={currentContext.tension:F2}");
            }
            catch (Exception e)
            {
                LogError($"Send error: {e.Message}");
            }
        }

        private async Task ReceiveAudioLoop()
        {
            byte[] receiveBuffer = new byte[BUFFER_SIZE * 2]; // Int16 = 2 bytes

            try
            {
                while (isConnected && !cancellationToken.Token.IsCancellationRequested)
                {
                    var result = await webSocket.ReceiveAsync(
                        new ArraySegment<byte>(receiveBuffer),
                        cancellationToken.Token
                    );

                    if (result.MessageType == WebSocketMessageType.Binary)
                    {
                        // Convert Int16 PCM to float
                        float[] audioSamples = new float[result.Count / 2];
                        for (int i = 0; i < audioSamples.Length; i++)
                        {
                            short sample = (short)((receiveBuffer[i * 2 + 1] << 8) | receiveBuffer[i * 2]);
                            audioSamples[i] = sample / 32768f;
                        }

                        // Add to queue
                        lock (queueLock)
                        {
                            audioBufferQueue.Enqueue(audioSamples);

                            // Limit queue size
                            while (audioBufferQueue.Count > 10)
                            {
                                audioBufferQueue.Dequeue();
                            }
                        }
                    }
                }
            }
            catch (Exception e)
            {
                if (isConnected)
                {
                    LogError($"Receive error: {e.Message}");
                    isConnected = false;
                }
            }
        }

        private void OnAudioFilterRead(float[] data, int channels)
        {
            // Fill audio buffer from queue
            for (int i = 0; i < data.Length; i += channels)
            {
                // Get next sample
                float sample = GetNextAudioSample();

                // Fill all channels
                for (int ch = 0; ch < channels; ch++)
                {
                    data[i + ch] = sample;
                }
            }
        }

        private float GetNextAudioSample()
        {
            // If current buffer is exhausted, get next from queue
            if (currentAudioBuffer == null || bufferIndex >= currentAudioBuffer.Length)
            {
                lock (queueLock)
                {
                    if (audioBufferQueue.Count > 0)
                    {
                        currentAudioBuffer = audioBufferQueue.Dequeue();
                        bufferIndex = 0;
                    }
                    else
                    {
                        // No audio available - return silence
                        return 0f;
                    }
                }
            }

            // Return sample and increment
            return currentAudioBuffer[bufferIndex++];
        }

        private void Log(string message)
        {
            if (showDebugLogs)
            {
                Debug.Log($"[StaticWaves] {message}");
            }
        }

        private void LogError(string message)
        {
            Debug.LogError($"[StaticWaves] {message}");
        }

        #endregion
    }

    #region Helper Extensions

    /// <summary>
    /// Extension methods for easy StaticWaves integration
    /// </summary>
    public static class StaticWavesExtensions
    {
        public static void PushMusicEvent(this GameObject gameObject, string eventName, float intensity = 1.0f)
        {
            var music = FindObjectOfType<StaticWavesMusic>();
            if (music == null) return;

            // Simple event → context mapping
            switch (eventName.ToLower())
            {
                case "combat_start":
                    music.SetCombat();
                    break;
                case "boss_enter":
                    music.SetBoss();
                    break;
                case "puzzle_start":
                    music.SetPuzzle();
                    break;
                case "victory":
                    music.SetVictory();
                    break;
                case "exploration":
                    music.SetExploration();
                    break;
                default:
                    // Custom event - adjust tension
                    var context = music.currentContext;
                    context.tension = intensity;
                    music.TransitionToContext(context);
                    break;
            }
        }
    }

    #endregion
}
