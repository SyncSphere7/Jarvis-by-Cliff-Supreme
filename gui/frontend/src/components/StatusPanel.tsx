import React, { useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Card,
  CardContent,
  Grid,
} from '@mui/material'
import {
  Circle,
  TrendingUp,
  Memory,
  Speed,
  Security,
} from '@mui/icons-material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../store/store'
import { setEngines, setSystemStatus } from '../store/systemSlice'

const StatusPanel: React.FC = () => {
  const dispatch = useDispatch()
  
  // SAFE SELECTORS - Handle undefined state
  const systemState = useSelector((state: RootState) => state?.system)
  const socketState = useSelector((state: RootState) => state?.socket)
  
  // Safe destructuring with defaults
  const engines = systemState?.engines || []
  const overallHealth = systemState?.overallHealth || 'unknown'
  const godlikeMode = systemState?.godlikeMode || false
  const activeSessions = systemState?.activeSessions || 0
  const uptime = systemState?.uptime || '0m'
  const socket = socketState?.socket || null

  // Request system status on component mount and set up periodic updates
  useEffect(() => {
    if (!socket) return

    const requestStatus = () => {
      try {
        socket.emit('request_system_status')
      } catch (error) {
        console.error('Failed to request system status:', error)
      }
    }

    // Initial request
    requestStatus()

    // Set up periodic updates every 5 seconds
    const interval = setInterval(requestStatus, 5000)

    // Listen for system status updates
    const handleSystemStatus = (status: any) => {
      try {
        if (status && status.engines) {
          dispatch(setEngines(status.engines))
        }
        if (status) {
          dispatch(setSystemStatus({
            overallHealth: status.overall_health || 'unknown',
            godlikeMode: status.godlike_mode || false,
            activeSessions: status.active_sessions || 1,
            uptime: status.uptime || '0m',
          }))
        }
      } catch (error) {
        console.error('Error handling system status:', error)
      }
    }

    const handleEngineActivity = (activity: any) => {
      try {
        if (activity && activity.engines) {
          dispatch(setEngines(activity.engines))
        }
      } catch (error) {
        console.error('Error handling engine activity:', error)
      }
    }

    socket.on('system_status', handleSystemStatus)
    socket.on('engine_activity', handleEngineActivity)

    return () => {
      clearInterval(interval)
      socket.off('system_status', handleSystemStatus)
      socket.off('engine_activity', handleEngineActivity)
    }
  }, [socket, dispatch])

  // SAFE COLOR FUNCTIONS - Never return 'default'
  const getStatusColor = (status: string): 'success' | 'info' | 'error' | 'warning' => {
    if (!status) return 'info'
    
    switch (status) {
      case 'active':
        return 'success'
      case 'idle':
        return 'info'
      case 'error':
        return 'error'
      case 'demo':
        return 'warning'
      default:
        return 'info' // NEVER return 'default'
    }
  }

  const getHealthColor = (health: string): 'success' | 'info' | 'error' | 'warning' => {
    if (!health) return 'info'
    
    switch (health) {
      case 'excellent':
        return 'success'
      case 'good':
        return 'info'
      case 'demo':
        return 'warning'
      default:
        return 'info' // NEVER return 'default'
    }
  }

  // SAFE COLOR ACCESS - Never access theme.palette[colorName].main
  const getSafeColor = (theme: any, colorName: string) => {
    try {
      // Validate inputs
      if (!theme || !theme.palette || !colorName) {
        return theme?.palette?.grey?.[500] || '#9e9e9e'
      }
      
      // Ensure we never try to access 'default' color
      const safeColorName = colorName === 'default' ? 'info' : colorName
      
      // Check if the color exists in the palette
      if (theme.palette[safeColorName] && theme.palette[safeColorName].main) {
        return theme.palette[safeColorName].main
      }
      
      // Fallback to grey
      return theme.palette.grey?.[500] || '#9e9e9e'
    } catch (error) {
      console.warn('Color access error, using fallback:', error)
      return '#9e9e9e' // Hardcoded fallback
    }
  }

  return (
    <Paper
      sx={{
        height: '100%',
        borderRadius: 0,
        borderLeft: 1,
        borderColor: 'divider',
        overflow: 'auto',
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>

        {/* Overall Health */}
        <Card sx={{ mb: 2 }}>
          <CardContent sx={{ pb: '16px !important' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2">Overall Health</Typography>
              <Chip
                label={overallHealth}
                color={getHealthColor(overallHealth)}
                size="small"
              />
            </Box>
            
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Memory fontSize="small" />
                  <Typography variant="caption">Sessions: {activeSessions}</Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Speed fontSize="small" />
                  <Typography variant="caption">Uptime: {uptime}</Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Godlike Mode Status */}
        {godlikeMode && (
          <Card sx={{ mb: 2, backgroundColor: 'warning.light' }}>
            <CardContent sx={{ pb: '16px !important' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Security color="warning" />
                <Typography variant="subtitle2" color="warning.dark">
                  🌟 GODLIKE MODE ACTIVE
                </Typography>
              </Box>
              <Typography variant="caption" color="warning.dark">
                All supreme capabilities enabled
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>

      <Divider />

      {/* Engine Status */}
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom fontWeight="medium">
          Supreme Engines
        </Typography>

        <List dense>
          {engines.map((engine) => (
            <ListItem key={engine.name} sx={{ px: 0 }}>
              <Box sx={{ width: '100%' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Circle
                      sx={{
                        fontSize: 8,
                        color: (theme) => {
                          const colorName = getStatusColor(engine.status)
                          return getSafeColor(theme, colorName)
                        },
                      }}
                    />
                    <Typography variant="body2" fontWeight="medium">
                      {engine.name}
                    </Typography>
                  </Box>
                  <Chip
                    label={engine.status}
                    color={getStatusColor(engine.status)}
                    size="small"
                    variant="outlined"
                  />
                </Box>
                
                {/* Activity Bar */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={engine.activity || 0}
                    sx={{ flex: 1, height: 4, borderRadius: 2 }}
                    color={getStatusColor(engine.status)}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {engine.activity || 0}%
                  </Typography>
                </Box>
                
                {engine.lastUsed && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                    Last used: {new Date(engine.lastUsed).toLocaleTimeString()}
                  </Typography>
                )}
              </Box>
            </ListItem>
          ))}
        </List>

        {engines.length === 0 && (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
            Loading engine status...
          </Typography>
        )}
      </Box>

      <Divider />

      {/* Activity Feed */}
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom fontWeight="medium">
          Recent Activity
        </Typography>

        <List dense>
          <ListItem sx={{ px: 0 }}>
            <ListItemText
              primary="System initialized"
              secondary="All engines online"
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
          
          <ListItem sx={{ px: 0 }}>
            <ListItemText
              primary="Godlike mode activated"
              secondary="Supreme capabilities enabled"
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
          
          <ListItem sx={{ px: 0 }}>
            <ListItemText
              primary="User connected"
              secondary="WebSocket connection established"
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
        </List>
      </Box>
    </Paper>
  )
}

export default StatusPanel