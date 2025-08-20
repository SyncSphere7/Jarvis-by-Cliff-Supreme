import React, { useState } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  IconButton,
  Tabs,
  Tab,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material'
import {
  Psychology,
  Security,
  Speed,
  Analytics,
  Memory,
  CloudQueue,
  AutoAwesome,
  Bolt,
  Visibility,
  Settings,
  TrendingUp,
  Timeline,
} from '@mui/icons-material'
import { useSelector } from 'react-redux'
import { RootState } from '../store/store'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell } from 'recharts'
import ControlCentre from './ControlCentre'
import MetricsPanel from './MetricsPanel'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const SupremeDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const { engines, overallHealth, godlikeMode } = useSelector((state: RootState) => state.system)
  const { messages } = useSelector((state: RootState) => state.chat)

  // Mock data for charts
  const performanceData = [
    { time: '00:00', cpu: 45, memory: 62, network: 23 },
    { time: '04:00', cpu: 52, memory: 58, network: 31 },
    { time: '08:00', cpu: 78, memory: 71, network: 45 },
    { time: '12:00', cpu: 85, memory: 79, network: 52 },
    { time: '16:00', cpu: 92, memory: 85, network: 67 },
    { time: '20:00', cpu: 88, memory: 82, network: 58 },
  ]

  const engineDistribution = [
    { name: 'Reasoning', value: 25, color: '#8884d8' },
    { name: 'Knowledge', value: 20, color: '#82ca9d' },
    { name: 'Security', value: 15, color: '#ffc658' },
    { name: 'Analytics', value: 18, color: '#ff7300' },
    { name: 'Communication', value: 12, color: '#00ff88' },
    { name: 'Other', value: 10, color: '#ff0088' },
  ]

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const getEngineIcon = (engineName: string) => {
    const name = engineName.toLowerCase()
    if (name.includes('reasoning')) return <Psychology />
    if (name.includes('security')) return <Security />
    if (name.includes('analytics')) return <Analytics />
    if (name.includes('communication')) return <CloudQueue />
    if (name.includes('knowledge')) return <Memory />
    return <AutoAwesome />
  }

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
              🌟 Supreme Jarvis Dashboard
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              God-like AI Assistant Control Center
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Chip 
              label={godlikeMode ? "SUPREME MODE" : "NORMAL MODE"} 
              color={godlikeMode ? "success" : "default"}
              sx={{ fontWeight: 'bold', mb: 1 }}
            />
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Overall Health: {overallHealth}
            </Typography>
          </Box>
        </Box>
        
        {/* Animated background */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)',
            animation: 'float 6s ease-in-out infinite',
          }}
        />
      </Paper>

      {/* Dashboard Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              fontSize: '1rem',
              fontWeight: 'bold',
            },
          }}
        >
          <Tab icon={<Visibility />} label="Overview" />
          <Tab icon={<Analytics />} label="Analytics" />
          <Tab icon={<Settings />} label="Control Center" />
          <Tab icon={<Timeline />} label="Monitoring" />
        </Tabs>
      </Paper>

      {/* Overview Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* Engine Status Cards */}
          {engines.map((engine, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ 
                height: '100%',
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                color: 'white'
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getEngineIcon(engine.name)}
                    <Typography variant="h6" sx={{ ml: 1, fontWeight: 'bold' }}>
                      {engine.name}
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ mb: 2, opacity: 0.9 }}>
                    Status: {engine.status}
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={engine.activity} 
                    sx={{ 
                      height: 8, 
                      borderRadius: 4,
                      backgroundColor: 'rgba(255,255,255,0.3)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: 'white'
                      }
                    }}
                  />
                  <Typography variant="body2" sx={{ mt: 1, opacity: 0.8 }}>
                    Activity: {engine.activity}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Analytics Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Performance Analytics
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="cpu" stackId="1" stroke="#8884d8" fill="#8884d8" />
                  <Area type="monotone" dataKey="memory" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
                  <Area type="monotone" dataKey="network" stackId="1" stroke="#ffc658" fill="#ffc658" />
                </AreaChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Engine Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={engineDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {engineDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Control Center Tab */}
      <TabPanel value={tabValue} index={2}>
        <ControlCentre />
      </TabPanel>

      {/* Monitoring Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <MetricsPanel />
          </Grid>
        </Grid>
      </TabPanel>

      <style jsx>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.7; }
          100% { opacity: 1; }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </Box>
  )
}

export default SupremeDashboard
