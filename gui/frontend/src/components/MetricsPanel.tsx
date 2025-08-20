import React, { useEffect, useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material'
import {
  Memory,
  Speed,
  Storage,
  NetworkWifi,
  TrendingUp,
  Warning,
} from '@mui/icons-material'
import { useSelector } from 'react-redux'
import { RootState } from '../store/store'

interface SystemMetrics {
  status: string
  timestamp: string
  system_metrics: {
    timestamp: number
    cpu_percent: number
    memory_percent: number
    disk_usage_percent: number
    network_bytes_sent: number
    network_bytes_recv: number
    uptime_seconds: number
    load_average: number[]
  }
  engine_metrics: Record<string, any>
  uptime: string
}

interface PerformanceReport {
  report_generated: string
  period_seconds: number
  metrics_count: number
  averages: {
    cpu_percent: number
    memory_percent: number
    disk_usage_percent: number
  }
  latest: {
    cpu_percent: number
    memory_percent: number
    disk_usage_percent: number
    load_average: number[]
  }
  engine_performance: Record<string, any>
}

const MetricsPanel: React.FC = () => {
  const socketState = useSelector((state: RootState) => state?.socket)
  const socket = socketState?.socket || null
  
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [performanceReport, setPerformanceReport] = useState<PerformanceReport | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Request metrics on component mount and set up periodic updates
  useEffect(() => {
    if (!socket) return
    
    const requestMetrics = () => {
      try {
        fetch('/api/system/metrics')
          .then(response => response.json())
          .then(data => {
            setSystemMetrics(data)
            setError(null)
          })
          .catch(err => {
            console.error('Failed to fetch system metrics:', err)
            setError('Failed to load system metrics')
          })
        
        fetch('/api/system/performance')
          .then(response => response.json())
          .then(data => {
            setPerformanceReport(data)
            setError(null)
          })
          .catch(err => {
            console.error('Failed to fetch performance report:', err)
            setError('Failed to load performance report')
          })
      } catch (error) {
        console.error('Failed to request metrics:', error)
        setError('Failed to request metrics')
      }
    }
    
    // Initial request
    requestMetrics()
    
    // Set up periodic updates every 10 seconds
    const interval = setInterval(requestMetrics, 10000)
    
    return () => {
      clearInterval(interval)
    }
  }, [socket])
  
  // Format uptime
  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }
  
  // Get health color based on percentage
  const getHealthColor = (percentage: number) => {
    if (percentage > 90) return 'error'
    if (percentage > 75) return 'warning'
    return 'success'
  }
  
  // Get health status text
  const getHealthStatus = (percentage: number) => {
    if (percentage > 90) return 'Critical'
    if (percentage > 75) return 'Warning'
    return 'Healthy'
  }
  
  if (error) {
    return (
      <Paper sx={{ height: '100%', borderRadius: 0, borderLeft: 1, borderColor: 'divider' }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            System Metrics
          </Typography>
          <Typography color="error">{error}</Typography>
        </Box>
      </Paper>
    )
  }
  
  if (!systemMetrics || !performanceReport) {
    return (
      <Paper sx={{ height: '100%', borderRadius: 0, borderLeft: 1, borderColor: 'divider' }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            System Metrics
          </Typography>
          <Typography>Loading metrics...</Typography>
        </Box>
      </Paper>
    )
  }
  
  const metrics = systemMetrics.system_metrics
  const report = performanceReport
  
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
          System Metrics
        </Typography>
        
        {/* System Health Summary */}
        <Card sx={{ mb: 2 }}>
          <CardContent sx={{ pb: '16px !important' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2">System Health</Typography>
              <Chip
                label={getHealthStatus(metrics.cpu_percent)}
                color={getHealthColor(metrics.cpu_percent)}
                size="small"
              />
            </Box>
            
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Speed fontSize="small" />
                  <Typography variant="caption">
                    Uptime: {formatUptime(metrics.uptime_seconds)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUp fontSize="small" />
                  <Typography variant="caption">
                    Load: {metrics.load_average[0]?.toFixed(2) || '0.00'}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
        
        {/* Resource Usage */}
        <Typography variant="subtitle1" gutterBottom fontWeight="medium" sx={{ mt: 2 }}>
          Resource Usage
        </Typography>
        
        <Grid container spacing={2}>
          {/* CPU Usage */}
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ pb: '16px !important' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Speed fontSize="small" color="primary" />
                    <Typography variant="subtitle2">CPU Usage</Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {metrics.cpu_percent.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metrics.cpu_percent}
                  sx={{ height: 6, borderRadius: 3 }}
                  color={getHealthColor(metrics.cpu_percent)}
                />
              </CardContent>
            </Card>
          </Grid>
          
          {/* Memory Usage */}
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ pb: '16px !important' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Memory fontSize="small" color="primary" />
                    <Typography variant="subtitle2">Memory Usage</Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {metrics.memory_percent.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metrics.memory_percent}
                  sx={{ height: 6, borderRadius: 3 }}
                  color={getHealthColor(metrics.memory_percent)}
                />
              </CardContent>
            </Card>
          </Grid>
          
          {/* Disk Usage */}
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ pb: '16px !important' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Storage fontSize="small" color="primary" />
                    <Typography variant="subtitle2">Disk Usage</Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {metrics.disk_usage_percent.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metrics.disk_usage_percent}
                  sx={{ height: 6, borderRadius: 3 }}
                  color={getHealthColor(metrics.disk_usage_percent)}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        {/* Performance Averages */}
        <Typography variant="subtitle1" gutterBottom fontWeight="medium" sx={{ mt: 2 }}>
          Performance Averages
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center', pb: '16px !important' }}>
                <Typography variant="caption" color="text.secondary">CPU</Typography>
                <Typography variant="h6">{report.averages.cpu_percent.toFixed(1)}%</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center', pb: '16px !important' }}>
                <Typography variant="caption" color="text.secondary">Memory</Typography>
                <Typography variant="h6">{report.averages.memory_percent.toFixed(1)}%</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center', pb: '16px !important' }}>
                <Typography variant="caption" color="text.secondary">Disk</Typography>
                <Typography variant="h6">{report.averages.disk_usage_percent.toFixed(1)}%</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        {/* Engine Performance */}
        {Object.keys(systemMetrics.engine_metrics).length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle1" gutterBottom fontWeight="medium">
              Engine Performance
            </Typography>
            
            <List dense>
              {Object.entries(systemMetrics.engine_metrics).map(([engineName, engineMetrics]) => (
                <ListItem key={engineName} sx={{ px: 0 }}>
                  <ListItemText
                    primary={engineName}
                    secondary={
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mt: 0.5 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="caption">Success Rate</Typography>
                          <Typography variant="caption">{engineMetrics.success_rate?.toFixed(1) || '0.0'}%</Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={engineMetrics.success_rate || 0}
                          sx={{ height: 4, borderRadius: 2 }}
                          color="primary"
                        />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="caption">Response Time</Typography>
                          <Typography variant="caption">{engineMetrics.average_response_time?.toFixed(2) || '0.00'}ms</Typography>
                        </Box>
                      </Box>
                    }
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </Box>
    </Paper>
  )
}

export default MetricsPanel