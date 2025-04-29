import React from 'react';
import ReactDOM from 'react-dom/client';  // React 18 uses 'react-dom/client'
import App from './App';
import reportWebVitals from './reportWebVitals';

// Create root element
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the App component
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Optional: For performance monitoring
reportWebVitals();
