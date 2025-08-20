import React from 'react'
import { Box, Typography, Button } from '@mui/material'
import { useSelector } from 'react-redux'
import { RootState } from '../store/store'

const ReduxTest: React.FC = () => {
  // Test Redux store access
  const systemState = useSelector((state: RootState) => {
    console.log('Redux state:', state)
    return state?.system
  })
  
  const socketState = useSelector((state: RootState) => {
    console.log('Socket state:', state?.socket)
    return state?.socket
  })

  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Typography variant="h4" gutterBottom>
        Redux Store Test
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 2 }}>
        System State: {systemState ? '✅ Available' : '❌ Undefined'}
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 2 }}>
        Socket State: {socketState ? '✅ Available' : '❌ Undefined'}
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 2 }}>
        Engines: {systemState?.engines?.length || 0}
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>
        Socket Connected: {socketState?.isConnected ? 'Yes' : 'No'}
      </Typography>
      
      <Button 
        variant="contained" 
        color="primary"
        onClick={() => console.log('Current Redux state:', { systemState, socketState })}
      >
        Log State
      </Button>
    </Box>
  )
}

export default ReduxTest
