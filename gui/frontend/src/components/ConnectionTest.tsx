import React, { useEffect, useState } from 'react'
import { Box, Typography, Button, Paper, Alert, Chip } from '@mui/material'
import { CheckCircle, Error, Refresh } from '@mui/icons-material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../store/store'
import { connectSocket, disconnectSocket } from '../store/socketSlice'

const ConnectionTest: React.FC = () => {
  const [testResults, setTestResults] = useState<any>({})
  const [isTesting, setIsTesting] = useState(false)
  
  const dispatch = useDispatch()
  const socketState = useSelector((state: RootState) => state?.socket)

  const runConnectionTest = async () => {
    setIsTesting(true)
    const results: any = {}

    // Test 1: Backend Health
    try {
      const response = await fetch('http://localhost:5001/health')
      results.backend = {
        status: response.ok ? 'success' : 'error',
        message: response.ok ? 'Backend responding' : `HTTP ${response.status}`,
        data: response.ok ? await response.json() : null
      }
    } catch (error) {
      results.backend = {
        status: 'error',
        message: `Connection failed: ${error}`,
        data: null
      }
    }

    // Test 2: Socket Connection
    try {
      if (socketState?.socket?.connected) {
        results.socket = {
          status: 'success',
          message: 'Socket connected',
          data: { socketId: socketState.socket.id }
        }
      } else {
        results.socket = {
          status: 'error',
          message: 'Socket not connected',
          data: { isConnected: socketState?.isConnected, hasSocket: !!socketState?.socket }
        }
      }
    } catch (error) {
      results.socket = {
        status: 'error',
        message: `Socket error: ${error}`,
        data: null
      }
    }

    // Test 3: Socket Reconnection
    try {
      if (!socketState?.socket?.connected) {
        dispatch(disconnectSocket())
        setTimeout(() => {
          dispatch(connectSocket())
        }, 1000)
        results.reconnection = {
          status: 'info',
          message: 'Attempting reconnection...',
          data: null
        }
      } else {
        results.reconnection = {
          status: 'success',
          message: 'Socket already connected',
          data: null
        }
      }
    } catch (error) {
      results.reconnection = {
        status: 'error',
        message: `Reconnection failed: ${error}`,
        data: null
      }
    }

    setTestResults(results)
    setIsTesting(false)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle color="success" />
      case 'error': return <Error color="error" />
      case 'info': return <Refresh color="info" />
      default: return <Error color="error" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success'
      case 'error': return 'error'
      case 'info': return 'info'
      default: return 'error'
    }
  }

  useEffect(() => {
    runConnectionTest()
  }, [])

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Connection Test
      </Typography>
      
      <Button
        variant="contained"
        onClick={runConnectionTest}
        disabled={isTesting}
        startIcon={<Refresh />}
        sx={{ mb: 3 }}
      >
        {isTesting ? 'Testing...' : 'Test Connection'}
      </Button>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Test Results
        </Typography>
        
        {Object.entries(testResults).map(([testName, result]: [string, any]) => (
          <Box key={testName} sx={{ mb: 2, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              {getStatusIcon(result.status)}
              <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
                {testName}
              </Typography>
              <Chip
                label={result.status}
                color={getStatusColor(result.status)}
                size="small"
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {result.message}
            </Typography>
            {result.data && (
              <Typography variant="caption" component="pre" sx={{ mt: 1, fontSize: '0.7rem' }}>
                {JSON.stringify(result.data, null, 2)}
              </Typography>
            )}
          </Box>
        ))}
      </Paper>

      <Alert severity="info" sx={{ mt: 2 }}>
        Current Socket State: {socketState?.isConnected ? 'Connected' : 'Disconnected'}
      </Alert>
    </Box>
  )
}

export default ConnectionTest
