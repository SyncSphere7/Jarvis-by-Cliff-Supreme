import React from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Chip,
  Tooltip,
} from '@mui/material'
import {
  Psychology,
  Settings,
  Brightness4,
  Brightness7,
  PowerSettingsNew,
} from '@mui/icons-material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../store/store'
import { setTheme } from '../store/settingsSlice'

const Header: React.FC = () => {
  const dispatch = useDispatch()
  const { theme } = useSelector((state: RootState) => state.settings)
  const { isConnected } = useSelector((state: RootState) => state.socket)
  const { godlikeMode, overallHealth } = useSelector((state: RootState) => state.system)

  const handleThemeToggle = () => {
    dispatch(setTheme(theme === 'light' ? 'dark' : 'light'))
  }

  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        {/* Logo and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <Psychology sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
            Supreme Jarvis
          </Typography>
          
          {/* Status Indicators */}
          <Box sx={{ ml: 3, display: 'flex', gap: 1 }}>
            <Chip
              icon={<PowerSettingsNew />}
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              size="small"
              variant="outlined"
            />
            
            {godlikeMode && (
              <Chip
                label="🌟 GODLIKE MODE"
                color="warning"
                size="small"
                sx={{
                  fontWeight: 'bold',
                  animation: 'pulse 2s infinite',
                  '@keyframes pulse': {
                    '0%': { opacity: 1 },
                    '50%': { opacity: 0.7 },
                    '100%': { opacity: 1 },
                  },
                }}
              />
            )}
            
            <Chip
              label={`Health: ${overallHealth}`}
              color={
                overallHealth === 'excellent' ? 'success' :
                overallHealth === 'good' ? 'info' :
                overallHealth === 'demo' ? 'warning' : 'default'
              }
              size="small"
              variant="outlined"
            />
          </Box>
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Toggle theme">
            <IconButton color="inherit" onClick={handleThemeToggle}>
              {theme === 'light' ? <Brightness4 /> : <Brightness7 />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Settings">
            <IconButton color="inherit">
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Header