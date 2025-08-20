import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Chip,
} from '@mui/material'
import {
  ExpandMore,
  Computer,
  Psychology,
  Shield,
  Speed as SpeedIcon,
  Tune,
  AutoAwesome,
  Save,
  Refresh,
  CheckCircle,
  Error,
  Info,
  Storage,
  NetworkCheck,
  Mic,
  Language,
  Settings,
} from '@mui/icons-material'

const ControlCentre: React.FC = () => {
  // Control Centre State
  const [controlSettings, setControlSettings] = useState({
    // Initialize with default values
    systemAccess: false,
    fileOperations: false,
    appLaunching: false,
    terminalAccess: false,
    networkAccess: false,
    aimlApiEnabled: false,
    gpt4Enabled: false,
    claudeEnabled: false,
    geminiEnabled: false,
    autoModelSelection: false,
    privacyMode: true,
    dataCollection: false,
    conversationHistory: false,
    apiLogging: false,
    quantumEncryption: false,
    zeroTrustMode: false,
    autoOptimization: false,
    predictiveCaching: false,
    infiniteScaling: false,
    responseSpeed: 0.3,
    memoryUsage: 0.2,
    voiceControl: false,
    webSearch: false,
    codeGeneration: false,
    imageProcessing: false,
    realTimeAnalysis: false,
    autonomousMode: false,
    supremeReasoning: false,
    supremeCommunication: false,
    supremeKnowledge: false,
    supremeAnalytics: false,
    supremeSecurity: false,
    supremeLearning: false,
    supremeAutomation: false,
    supremeScalability: false,
    supremeControl: false,
  })

  const [selectedAIModel, setSelectedAIModel] = useState('gpt-4o')
  const [responseTimeout, setResponseTimeout] = useState(10)
  const [maxTokens, setMaxTokens] = useState(300)
  const [aiModels, setAiModels] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Socket.IO connection for real-time data
  useEffect(() => {
    const socket = (window as any).socket

    if (socket) {
      // Request AI models status
      socket.emit('get_ai_models')
      socket.on('ai_models_status', (data: any) => {
        setAiModels(data.models)
        setLoading(false)
      })

      // Request control settings
      socket.emit('get_control_settings')
      socket.on('control_settings', (data: any) => {
        if (data.settings) {
          setControlSettings(data.settings)
        }
        setLoading(false)
      })

      // Handle settings updates
      socket.on('control_settings_updated', (data: any) => {
        if (data.success) {
          console.log('Settings updated successfully')
        }
      })

      // Handle errors
      socket.on('error', (data: any) => {
        setError(data.message)
        setLoading(false)
      })

      return () => {
        socket.off('ai_models_status')
        socket.off('control_settings')
        socket.off('control_settings_updated')
        socket.off('error')
      }
    }
  }, [])

  const handleControlChange = (setting: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setControlSettings(prev => ({
      ...prev,
      [setting]: event.target.checked
    }))
  }

  const handleSliderChange = (setting: string) => (event: Event, newValue: number | number[]) => {
    setControlSettings(prev => ({
      ...prev,
      [setting]: newValue as number
    }))
  }

  const saveSettings = () => {
    const socket = (window as any).socket
    if (socket) {
      socket.emit('update_control_settings', { settings: controlSettings })
      console.log('Saving settings:', controlSettings)
    } else {
      console.log('Socket not available, settings saved locally:', controlSettings)
    }
  }

  const resetSettings = () => {
    // TODO: Implement settings reset
    console.log('Resetting settings')
  }

  const getStatusColor = (enabled: boolean) => enabled ? 'success' : 'error'
  const getStatusIcon = (enabled: boolean) => enabled ? <CheckCircle /> : <Error />

  if (loading) {
    return (
      <Box sx={{ width: '100%', textAlign: 'center', py: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Loading Control Centre...
        </Typography>
        <LinearProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ width: '100%', textAlign: 'center', py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Error loading Control Centre: {error}
        </Alert>
        <Button variant="contained" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </Box>
    )
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Control Actions */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={saveSettings}
            sx={{ background: 'linear-gradient(45deg, #4CAF50 30%, #45a049 90%)' }}
          >
            Save Settings
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={resetSettings}
          >
            Reset to Default
          </Button>
          <Alert severity="info" sx={{ flex: 1 }}>
            Changes are applied immediately. Use Save Settings to persist changes.
          </Alert>
          <Chip 
            label="LIVE DATA" 
            color="success" 
            size="small"
            icon={<CheckCircle />}
          />
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* System Access Controls */}
        <Grid item xs={12} md={6}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Computer sx={{ mr: 1 }} />
                <Typography variant="h6">System Access Controls</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.systemAccess}
                        onChange={handleControlChange('systemAccess')}
                        color="primary"
                      />
                    }
                    label="System Access"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Allow Jarvis to access your computer system
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.fileOperations}
                        onChange={handleControlChange('fileOperations')}
                        color="primary"
                      />
                    }
                    label="File Operations"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Read, write, and manage files on your computer
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.appLaunching}
                        onChange={handleControlChange('appLaunching')}
                        color="primary"
                      />
                    }
                    label="App Launching"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Launch applications and programs
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.terminalAccess}
                        onChange={handleControlChange('terminalAccess')}
                        color="primary"
                      />
                    }
                    label="Terminal Access"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Execute terminal commands
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.networkAccess}
                        onChange={handleControlChange('networkAccess')}
                        color="primary"
                      />
                    }
                    label="Network Access"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Access internet and network resources
                  </Typography>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* AI Model Controls */}
        <Grid item xs={12} md={6}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Psychology sx={{ mr: 1 }} />
                <Typography variant="h6">AI Model Controls</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.aimlApiEnabled}
                        onChange={handleControlChange('aimlApiEnabled')}
                        color="primary"
                      />
                    }
                    label="AIML API"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Enable AIML API integration
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.gpt4Enabled}
                        onChange={handleControlChange('gpt4Enabled')}
                        color="primary"
                      />
                    }
                    label="GPT-4 Model"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Enable GPT-4 for reasoning tasks
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.claudeEnabled}
                        onChange={handleControlChange('claudeEnabled')}
                        color="primary"
                      />
                    }
                    label="Claude Model"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Enable Claude for coding tasks
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.autoModelSelection}
                        onChange={handleControlChange('autoModelSelection')}
                        color="primary"
                      />
                    }
                    label="Auto Model Selection"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Automatically select best model for each task
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Default AI Model</InputLabel>
                    <Select
                      value={selectedAIModel}
                      label="Default AI Model"
                      onChange={(e) => setSelectedAIModel(e.target.value)}
                    >
                      {Object.entries(aiModels).map(([modelId, modelInfo]: [string, any]) => (
                        <MenuItem key={modelId} value={modelId}>
                          {modelInfo.name || modelId} {modelInfo.available ? '✅' : '❌'}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  {Object.keys(aiModels).length > 0 && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Available Models: {Object.values(aiModels).filter((m: any) => m.available).length} / {Object.keys(aiModels).length}
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Privacy & Security Controls */}
        <Grid item xs={12} md={6}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Shield sx={{ mr: 1 }} />
                <Typography variant="h6">Privacy & Security</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.privacyMode}
                        onChange={handleControlChange('privacyMode')}
                        color="primary"
                      />
                    }
                    label="Privacy Mode"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Enhanced privacy protection
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.dataCollection}
                        onChange={handleControlChange('dataCollection')}
                        color="primary"
                      />
                    }
                    label="Data Collection"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Collect usage data for improvement
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.conversationHistory}
                        onChange={handleControlChange('conversationHistory')}
                        color="primary"
                      />
                    }
                    label="Conversation History"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Store conversation history
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.quantumEncryption}
                        onChange={handleControlChange('quantumEncryption')}
                        color="primary"
                      />
                    }
                    label="Quantum Encryption"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Use quantum-resistant encryption
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.zeroTrustMode}
                        onChange={handleControlChange('zeroTrustMode')}
                        color="primary"
                      />
                    }
                    label="Zero Trust Mode"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Strict security verification
                  </Typography>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Performance Controls */}
        <Grid item xs={12} md={6}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SpeedIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Performance Controls</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.autoOptimization}
                        onChange={handleControlChange('autoOptimization')}
                        color="primary"
                      />
                    }
                    label="Auto Optimization"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Automatically optimize performance
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.predictiveCaching}
                        onChange={handleControlChange('predictiveCaching')}
                        color="primary"
                      />
                    }
                    label="Predictive Caching"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Cache frequently used data
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.infiniteScaling}
                        onChange={handleControlChange('infiniteScaling')}
                        color="primary"
                      />
                    }
                    label="Infinite Scaling"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Scale resources automatically
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Response Speed</Typography>
                  <Slider
                    value={controlSettings.responseSpeed}
                    onChange={handleSliderChange('responseSpeed')}
                    min={0.1}
                    max={1.0}
                    step={0.1}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Memory Usage Limit</Typography>
                  <Slider
                    value={controlSettings.memoryUsage}
                    onChange={handleSliderChange('memoryUsage')}
                    min={0.1}
                    max={1.0}
                    step={0.1}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Feature Controls */}
        <Grid item xs={12} md={6}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Tune sx={{ mr: 1 }} />
                <Typography variant="h6">Feature Controls</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.voiceControl}
                        onChange={handleControlChange('voiceControl')}
                        color="primary"
                      />
                    }
                    label="Voice Control"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Enable voice commands and responses
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.webSearch}
                        onChange={handleControlChange('webSearch')}
                        color="primary"
                      />
                    }
                    label="Web Search"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Search the internet for information
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.codeGeneration}
                        onChange={handleControlChange('codeGeneration')}
                        color="primary"
                      />
                    }
                    label="Code Generation"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Generate and modify code
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.imageProcessing}
                        onChange={handleControlChange('imageProcessing')}
                        color="primary"
                      />
                    }
                    label="Image Processing"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Process and analyze images
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.realTimeAnalysis}
                        onChange={handleControlChange('realTimeAnalysis')}
                        color="primary"
                      />
                    }
                    label="Real-time Analysis"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Analyze data in real-time
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={controlSettings.autonomousMode}
                        onChange={handleControlChange('autonomousMode')}
                        color="primary"
                      />
                    }
                    label="Autonomous Mode"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Allow Jarvis to act autonomously
                  </Typography>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Supreme Capabilities */}
        <Grid item xs={12}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AutoAwesome sx={{ mr: 1 }} />
                <Typography variant="h6">Supreme Capabilities</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {[
                  'Reasoning', 'Communication', 'Knowledge', 'Analytics', 
                  'Security', 'Learning', 'Automation', 'Scalability', 'Control'
                ].map((capability) => (
                  <Grid item xs={12} sm={6} md={4} key={capability}>
                    <Paper sx={{ p: 2, border: 1, borderColor: 'divider' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <AutoAwesome sx={{ mr: 1, fontSize: 20 }} />
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            Supreme {capability}
                          </Typography>
                        </Box>
                        <Switch
                          checked={controlSettings[`supreme${capability}` as keyof typeof controlSettings] as boolean}
                          onChange={handleControlChange(`supreme${capability}` as keyof typeof controlSettings)}
                          color="primary"
                          size="small"
                        />
                      </Box>
                      <Chip 
                        label={controlSettings[`supreme${capability}` as keyof typeof controlSettings] ? 'ACTIVE' : 'INACTIVE'}
                        color={controlSettings[`supreme${capability}` as keyof typeof controlSettings] ? 'success' : 'default'}
                        size="small"
                        sx={{ fontSize: '0.7rem' }}
                      />
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* System Status Summary */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              System Status Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {Object.values(controlSettings).filter(Boolean).length}
                  </Typography>
                  <Typography variant="body2">Active Features</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {Object.values(aiModels).filter((m: any) => m.available).length}
                  </Typography>
                  <Typography variant="body2">Available AI Models</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {Math.round(controlSettings.responseSpeed * 100)}%
                  </Typography>
                  <Typography variant="body2">Response Speed</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {controlSettings.quantumEncryption ? 'ON' : 'OFF'}
                  </Typography>
                  <Typography variant="body2">Quantum Security</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {controlSettings.autonomousMode ? 'ON' : 'OFF'}
                  </Typography>
                  <Typography variant="body2">Autonomous Mode</Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default ControlCentre
