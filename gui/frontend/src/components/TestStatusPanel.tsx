import React from 'react'
import { Box, Typography, Button } from '@mui/material'

const TestStatusPanel: React.FC = () => {
  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Typography variant="h4" gutterBottom>
        StatusPanel Test
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        If you can see this, the basic component is working!
      </Typography>
      <Button variant="contained" color="primary">
        Test Button
      </Button>
    </Box>
  )
}

export default TestStatusPanel
