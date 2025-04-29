import React, { useContext } from 'react';
import { Typography, Paper } from '@mui/material';
import AuthContext from '../context/auth';
import SpamChecker from './SpamChecker';

const Dashboard = () => {
  const { user } = useContext(AuthContext);

  return (
    <div style={{ padding: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.name}
      </Typography>
      <Paper style={{ padding: '2rem', marginBottom: '2rem' }}>
        <Typography variant="body1">
          Use the spam checker below to analyze your emails for spam content.
        </Typography>
      </Paper>
      <SpamChecker />
    </div>
  );
};

export default Dashboard;