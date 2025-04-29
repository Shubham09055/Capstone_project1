import React, { useState } from 'react';
import { 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  Card, 
  CardContent,
  LinearProgress,
  Chip,
  Box
} from '@mui/material';
import { checkSpam } from '../services/spam';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Register necessary chart components
ChartJS.register(ArcElement, Tooltip, Legend);

const SpamChecker = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  // Handle form submission to check spam
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null); // Reset error before each submission
    try {
      const response = await checkSpam(text);
      setResult(response);
      setHistory((prev) => [...prev, { text, ...response }]);
    } catch (err) {
      setError('Failed to fetch spam check result. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Prepare data for Doughnut chart
  const data = {
    labels: ['Ham', 'Spam'],
    datasets: [
      {
        data: result 
          ? [
              result.confidence * (result.isSpam ? 0.2 : 1),
              result.confidence * (result.isSpam ? 1 : 0.2),
            ]
          : [50, 50],
        backgroundColor: ['#4CAF50', '#F44336'],
        hoverBackgroundColor: ['#66BB6A', '#EF5350'],
      },
    ],
  };

  return (
    <div style={{ padding: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Email Spam Detector
      </Typography>
      
      <Paper style={{ padding: '2rem', marginBottom: '2rem' }}>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Email Text"
            multiline
            rows={6}
            variant="outlined"
            fullWidth
            value={text}
            onChange={(e) => setText(e.target.value)}
            margin="normal"
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !text.trim()}
            style={{ marginTop: '1rem' }}
          >
            Check for Spam
          </Button>
        </form>
      </Paper>

      {/* Loading Progress */}
      {loading && <LinearProgress />}

      {/* Error message */}
      {error && <Typography color="error" variant="body1" gutterBottom>{error}</Typography>}

      {/* Result display */}
      {result && (
        <Card style={{ marginBottom: '2rem' }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Result
            </Typography>
            <Box display="flex" alignItems="center" marginBottom="1rem">
              <Typography variant="body1" style={{ marginRight: '1rem' }}>
                This email is:
              </Typography>
              <Chip
                label={result.isSpam ? 'SPAM' : 'NOT SPAM'}
                color={result.isSpam ? 'secondary' : 'primary'}
              />
            </Box>
            <Typography variant="body1" gutterBottom>
              Confidence: {(result.confidence * 100).toFixed(2)}%
            </Typography>
            <div style={{ height: '300px' }}>
              <Doughnut data={data} options={{ maintainAspectRatio: false }} />
            </div>
          </CardContent>
        </Card>
      )}

      {/* History Section */}
      {history.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              History
            </Typography>
            {history.map((item, index) => (
              <div key={index} style={{ marginBottom: '1rem', padding: '1rem', borderBottom: '1px solid #eee' }}>
                <Typography variant="body2" style={{ fontStyle: 'italic' }}>
                  "{item.text.length > 50 ? `${item.text.substring(0, 50)}...` : item.text}"
                </Typography>
                <Chip
                  label={item.isSpam ? 'SPAM' : 'NOT SPAM'}
                  color={item.isSpam ? 'secondary' : 'primary'}
                  size="small"
                  style={{ marginTop: '0.5rem' }}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SpamChecker;
