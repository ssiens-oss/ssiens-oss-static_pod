import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import ProductionApp from './ProductionApp';

// Detect mode from environment or URL
const isProduction = import.meta.env.MODE === 'production' ||
                     window.location.search.includes('mode=production');

const isDevelopment = window.location.search.includes('mode=development');

// Choose which app to render
const AppComponent = (isDevelopment || !isProduction) ? App : ProductionApp;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppComponent />
  </React.StrictMode>
);
