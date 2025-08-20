import React, { useEffect, useState } from 'react'
import { Box, Container, Typography, Paper, Grid, Card, CardContent, Fab, Tooltip } from '@mui/material'
import { Dashboard, Chat, Close } from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import StatusPanel from './components/StatusPanel'
import SupremeDashboard from './components/SupremeDashboard'
import DebugInfo from './components/DebugInfo'
import { connectSocket, disconnectSocket } from './store/socketSlice'
import { RootState } from './store/store'

const App: React.FC = () => {
  const dispatch = useDispatch()
  const { isConnected } = useSelector((state: RootState) => state.socket)
  const [showDashboard, setShowDashboard] = useState(false)

  useEffect(() => {
    // Connect to WebSocket on app start
    dispatch(connectSocket())

    // Cleanup on unmount
    return () => {
      dispatch(disconnectSocket())
    }
  }, [dispatch])

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      {showDashboard ? (
        /* Supreme Dashboard View */
        <Box sx={{ flex: 1, overflow: 'auto', p: 2, backgroundColor: '#f5f5f5' }}>
          <SupremeDashboard />
        </Box>
      ) : (
        /* Chat Interface View */
        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Sidebar */}
          <Box sx={{ width: 280, flexShrink: 0 }}>
            <Sidebar />
          </Box>
          
          {/* Main Chat Area */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <ChatInterface />
          </Box>
          
          {/* Status Panel */}
          <Box sx={{ width: 320, flexShrink: 0 }}>
            <StatusPanel />
          </Box>
        </Box>
      )}
      
      {/* Floating Action Button to Toggle Views */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
          '&:hover': {
            background: 'linear-gradient(45deg, #FE6B8B 60%, #FF8E53 100%)',
          },
        }}
        onClick={() => setShowDashboard(!showDashboard)}
      >
        <Tooltip title={showDashboard ? "Switch to Chat" : "Open Supreme Dashboard"}>
          {showDashboard ? <Chat /> : <Dashboard />}
        </Tooltip>
      </Fab>
      
      {/* Connection Status */}
      {!isConnected && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 16,
            left: 16,
            zIndex: 1000,
          }}
        >
          <Paper
            sx={{
              p: 2,
              backgroundColor: 'error.main',
              color: 'error.contrastText',
            }}
          >
            <Typography variant="body2">
              Disconnected from Supreme Jarvis
            </Typography>
          </Paper>
        </Box>
      )}
      
      {/* Debug Info */}
      <DebugInfo />
    </Box>
  )
}

export default App