import React from 'react';
import ReactDOM from 'react-dom/client';
import MusicApp from './MusicApp';

const root = document.getElementById('root');
if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <MusicApp />
    </React.StrictMode>
  );
}
