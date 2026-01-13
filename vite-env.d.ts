/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MUSIC_API_URL?: string;
  // Add more env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
