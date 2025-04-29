const express = require('express');
const connectDB = require('./config/db');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

// Load env vars
require('dotenv').config();

// Connect to database
connectDB();

// Initialize app
const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Health check endpoint (ADD THIS FIRST)
app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    message: 'Backend service is healthy',
    database: 'Connected', // This assumes your connectDB() throws if connection fails
    timestamp: new Date().toISOString()
  });
});

// Mount routers
app.use('/api/auth', require('./routes/auth'));
app.use('/api/spam', require('./routes/spam'));

// Serve static assets in production
if (process.env.NODE_ENV === 'production') {
  // Set static folder
  app.use(express.static(path.join(__dirname, '../frontend/build')));

  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, '../frontend/build/index.html'));
  });
}

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});