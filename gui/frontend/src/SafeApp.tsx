import React, { useEffect, useState } from 'react'
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material'
import { io, Socket } from 'socket.io-client'

interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

const SafeApp: React.FC = () => {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome to Supreme Jarvis! I\'m ready to help you.',
      timestamp: new Date(),
    }
  ])
  const [currentInput, setCurrentInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    // Connect to backend
    const newSocket = io('http://localhost:5001', {
      transports: ['websocket', 'polling'],
    })

    newSocket.on('connect', () => {
      console.log('Connected to backend')
      setIsConnected(true)
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from backend')
      setIsConnected(false)
    })

    newSocket.on('chat_response', (response: any) => {
      const message: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: response.response || 'No response',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, message])
      setIsProcessing(false)
    })

    newSocket.on('error', (error: any) => {
      console.error('Socket error:', error)
      setIsProcessing(false)
    })

    setSocket(newSocket)

    return () => {
      newSocket.disconnect()
    }
  }, [])

  const handleSendMessage = () => {
    if (!currentInput.trim() || isProcessing || !socket) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: currentInput,
      timestamp: new Date(),
    }
    
    setMessages(prev => [...prev, userMessage])
    setIsProcessing(true)
    
    const messageToSend = currentInput
    setCurrentInput('')

    // Send to backend
    socket.emit('chat_message', {
      message: messageToSend,
      user_profile: {
        user_id: 'user',
        name: 'User',
        preferences: {},
        context: { role: 'user' }
      }
    })
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🚀 Supreme Jarvis
          </Typography>
          <Chip
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            variant="outlined"
            sx={{ color: 'white' }}
          />
        </Toolbar>
      </AppBar>

      {/* Messages */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <List>
          {messages.map((message) => (
            <ListItem key={message.id}>
              <Paper
                sx={{
                  p: 2,
                  width: '100%',
                  backgroundColor: message.type === 'user' ? '#e3f2fd' : '#f5f5f5',
                }}
              >
                <Typography variant="body2" color="primary" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {message.type === 'user' ? '👤 You' : 
                   message.type === 'system' ? '🔧 System' : '🤖 Supreme Jarvis'}
                </Typography>
                <Typography variant="body1">
                  {message.content}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Paper>
            </ListItem>
          ))}
        </List>

        {isProcessing && (
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              🤔 Supreme Jarvis is thinking...
            </Typography>
          </Box>
        )}
      </Box>

      {/* Input */}
      <Paper sx={{ p: 2, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder="Ask Supreme Jarvis anything..."
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isProcessing}
            variant="outlined"
            size="small"
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!currentInput.trim() || isProcessing}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  )
}

export default SafeApp