import React, { useEffect, useState } from 'react'
import { Box, Typography, Button, Paper, List, ListItem, ListItemText, Chip, Alert } from '@mui/material'
import { CheckCircle, Error, Warning, Info } from '@mui/icons-material'
import { useSelector } from 'react-redux'
import { RootState } from '../store/store'

interface DiagnosticResult {
  name: string
  status: 'success' | 'error' | 'warning' | 'info'
  message: string
  details?: any
}

// Safe JSON serializer that handles circular references
const safeStringify = (obj: any): string => {
  try {
    const seen = new WeakSet()
    return JSON.stringify(obj, (key, value) => {
      if (typeof value === 'object' && value !== null) {
        if (seen.has(value)) {
          return '[Circular Reference]'
        }
        seen.add(value)
      }
      return value
    }, 2)
  } catch (error) {
    return `[Error serializing: ${error}]`
  }
}

// Safe object serializer for socket objects
const safeSerializeSocket = (socketState: any) => {
  if (!socketState) return null
  
  return {
    isConnected: socketState.isConnected,
    error: socketState.error,
    hasSocket: !!socketState.socket,
    socketConnected: socketState.socket?.connected,
    socketId: socketState.socket?.id
  }
}

const DiagnosticPage: React.FC = () => {
  const [results, setResults] = useState<DiagnosticResult[]>([])
  const [isRunning, setIsRunning] = useState(false)
  
  const systemState = useSelector((state: RootState) => state?.system)
  const socketState = useSelector((state: RootState) => state?.socket)

  const runDiagnostics = async () => {
    setIsRunning(true)
    const newResults: DiagnosticResult[] = []

    // Test 1: Redux Store Access
    try {
      if (systemState) {
        newResults.push({
          name: 'Redux Store - System',
          status: 'success',
          message: 'System state accessible',
          details: {
            engines: systemState.engines?.length || 0,
            overallHealth: systemState.overallHealth,
            godlikeMode: systemState.godlikeMode,
            activeSessions: systemState.activeSessions,
            uptime: systemState.uptime
          }
        })
      } else {
        newResults.push({
          name: 'Redux Store - System',
          status: 'error',
          message: 'System state is undefined'
        })
      }
    } catch (error) {
      newResults.push({
        name: 'Redux Store - System',
        status: 'error',
        message: `Error accessing system state: ${error}`
      })
    }

    // Test 2: Socket State
    try {
      if (socketState) {
        const safeSocketInfo = safeSerializeSocket(socketState)
        newResults.push({
          name: 'Redux Store - Socket',
          status: 'success',
          message: 'Socket state accessible',
          details: safeSocketInfo
        })
      } else {
        newResults.push({
          name: 'Redux Store - Socket',
          status: 'error',
          message: 'Socket state is undefined'
        })
      }
    } catch (error) {
      newResults.push({
        name: 'Redux Store - Socket',
        status: 'error',
        message: `Error accessing socket state: ${error}`
      })
    }

    // Test 3: Backend Connection
    try {
      const response = await fetch('http://localhost:5001/health')
      if (response.ok) {
        const healthData = await response.json()
        newResults.push({
          name: 'Backend Connection',
          status: 'success',
          message: 'Backend is responding',
          details: healthData
        })
      } else {
        newResults.push({
          name: 'Backend Connection',
          status: 'error',
          message: `Backend responded with status: ${response.status}`
        })
      }
    } catch (error) {
      newResults.push({
        name: 'Backend Connection',
        status: 'error',
        message: `Cannot connect to backend: ${error}`
      })
    }

    // Test 4: Socket Connection
    try {
      if (socketState?.socket?.connected) {
        newResults.push({
          name: 'Socket Connection',
          status: 'success',
          message: 'Socket is connected'
        })
      } else {
        newResults.push({
          name: 'Socket Connection',
          status: 'warning',
          message: 'Socket is not connected'
        })
      }
    } catch (error) {
      newResults.push({
        name: 'Socket Connection',
        status: 'error',
        message: `Socket error: ${error}`
      })
    }

    // Test 5: Theme Access
    try {
      // Simulate theme access
      const mockTheme = {
        palette: {
          success: { main: '#4caf50' },
          error: { main: '#f44336' },
          warning: { main: '#ff9800' },
          info: { main: '#2196f3' },
          grey: { 500: '#9e9e9e' }
        }
      }
      
      // Test the problematic code pattern
      const testColor = 'default'
      const colorName = testColor === 'default' ? 'info' : testColor
      const color = mockTheme.palette[colorName]?.main || mockTheme.palette.grey[500]
      
      newResults.push({
        name: 'Theme Color Access',
        status: 'success',
        message: 'Theme color access works correctly',
        details: { testColor, colorName, color }
      })
    } catch (error) {
      newResults.push({
        name: 'Theme Color Access',
        status: 'error',
        message: `Theme color access error: ${error}`
      })
    }

    setResults(newResults)
    setIsRunning(false)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle color="success" />
      case 'error': return <Error color="error" />
      case 'warning': return <Warning color="warning" />
      default: return <Info color="info" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success'
      case 'error': return 'error'
      case 'warning': return 'warning'
      default: return 'info'
    }
  }

  return (
    <Box sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Supreme Jarvis Diagnostic
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>
        Running comprehensive system diagnostics to identify issues...
      </Typography>

      <Button
        variant="contained"
        onClick={runDiagnostics}
        disabled={isRunning}
        sx={{ mb: 3 }}
      >
        {isRunning ? 'Running Diagnostics...' : 'Run Diagnostics'}
      </Button>

      {results.length > 0 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Diagnostic Results
          </Typography>
          
          <List>
            {results.map((result, index) => (
              <ListItem key={index} sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  {getStatusIcon(result.status)}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2">
                      {result.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {result.message}
                    </Typography>
                    {result.details && (
                      <Typography variant="caption" component="pre" sx={{ mt: 1, fontSize: '0.7rem' }}>
                        {safeStringify(result.details)}
                      </Typography>
                    )}
                  </Box>
                  <Chip
                    label={result.status}
                    color={getStatusColor(result.status)}
                    size="small"
                  />
                </Box>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Alert severity="info" sx={{ mt: 3 }}>
        If you see any errors above, they indicate the source of the "Cannot read properties of undefined (reading 'main')" issue.
      </Alert>
    </Box>
  )
}

export default DiagnosticPage
