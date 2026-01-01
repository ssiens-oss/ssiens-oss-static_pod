import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import ProductionApp from './ProductionApp';
import DashboardApp from './DashboardApp';

// Detect mode from environment or URL
const urlParams = new URLSearchParams(window.location.search);
const mode = urlParams.get('mode');

const isProduction = import.meta.env.MODE === 'production' || mode === 'production';
const isDashboard = mode === 'dashboard';
const isDevelopment = mode === 'development';

// Choose which app to render
let AppComponent;
if (isDashboard) {
  AppComponent = DashboardApp;
} else if (isDevelopment || (!isProduction && !isDashboard)) {
  AppComponent = App;
} else {
  AppComponent = ProductionApp;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppComponent />
  </React.StrictMode>
);
