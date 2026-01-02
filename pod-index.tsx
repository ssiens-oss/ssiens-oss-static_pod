import React from 'react';
import ReactDOM from 'react-dom/client';
import PodPipelineApp from './PodPipelineApp';

const root = document.getElementById('root');
if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <PodPipelineApp />
    </React.StrictMode>
  );
}
