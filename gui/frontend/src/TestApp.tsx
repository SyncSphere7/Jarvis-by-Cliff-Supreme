import React from 'react'
import { Box, Typography, Button, Paper } from '@mui/material'

const TestApp: React.FC = () => {
  return (
    <Box sx={{ p: 4 }}>
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
          🚀 Supreme Jarvis GUI Test
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          If you can see this, the basic React app is working!
        </Typography>
        <Button variant="contained" color="primary">
          Test Button
        </Button>
      </Paper>
    </Box>
  )
}

export default TestApp