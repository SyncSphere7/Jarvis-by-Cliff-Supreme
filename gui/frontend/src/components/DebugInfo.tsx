import React from 'react'
import { Box, Typography, Paper } from '@mui/material'
import { useSelector } from 'react-redux'
import { RootState } from '../store/store'

const DebugInfo: React.FC = () => {
  const { isConnected, error } = useSelector((state: RootState) => state.socket)
  const { messages, isProcessing } = useSelector((state: RootState) => state.chat)

  if (process.env.NODE_ENV === 'production') {
    return null
  }

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 16,
        left: 16,
        p: 2,
        backgroundColor: 'rgba(0,0,0,0.8)',
        color: 'white',
        fontSize: '12px',
        zIndex: 9999,
        maxWidth: 300,
      }}
    >
      <Typography variant="caption" display="block">
        Debug Info:
      </Typography>
      <Typography variant="caption" display="block">
        Connected: {isConnected ? '✅' : '❌'}
      </Typography>
      <Typography variant="caption" display="block">
        Processing: {isProcessing ? '⏳' : '✅'}
      </Typography>
      <Typography variant="caption" display="block">
        Messages: {messages.length}
      </Typography>
      {error && (
        <Typography variant="caption" display="block" color="error">
          Error: {error}
        </Typography>
      )}
    </Paper>
  )
}

export default DebugInfo