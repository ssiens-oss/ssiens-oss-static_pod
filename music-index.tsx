import React from 'react';
import ReactDOM from 'react-dom/client';
import MusicApp from './MusicApp';
import './index.css';  // Uses existing Tailwind styles

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MusicApp />
  </React.StrictMode>
);
