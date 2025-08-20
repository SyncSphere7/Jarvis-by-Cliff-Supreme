import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Divider,
} from '@mui/material'
import {
  Send,
  Clear,
  AttachFile,
} from '@mui/icons-material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../store/store'
import {
  addMessage,
  setProcessing,
  setActiveEngines,
  setCurrentInput,
  clearMessages,
  Message,
} from '../store/chatSlice'
import MessageBubble from './MessageBubble'

const ChatInterface: React.FC = () => {
  const dispatch = useDispatch()
  const { messages, isProcessing, activeEngines, currentInput } = useSelector(
    (state: RootState) => state.chat
  )
  const { socket } = useSelector((state: RootState) => state.socket)
  const { userProfile, preferences } = useSelector((state: RootState) => state.settings)
  
  // Ensure we have valid user profile data
  const safeUserProfile = userProfile || {
    userId: 'default_user',
    name: 'User',
    role: 'user',
    experienceLevel: 'intermediate'
  }
  
  const safePreferences = preferences || {
    complexity: 'detailed',
    style: 'technical',
    quantumPowers: true,
    codingFocus: 'full_stack'
  }
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Set up socket event listeners
  useEffect(() => {
    if (!socket) return

    const handleChatResponse = (response: any) => {
      try {
        const message: Message = {
          id: Date.now().toString(),
          type: 'assistant',
          content: response.response || 'No response received',
          timestamp: new Date(),
          confidence: response.confidence || 0,
          enginesUsed: response.engines_used || [],
          processingTime: response.processing_time || 0,
        }
        
        dispatch(addMessage(message))
        dispatch(setProcessing(false))
        dispatch(setActiveEngines([]))
      } catch (error) {
        console.error('Error handling chat response:', error)
        dispatch(setProcessing(false))
        dispatch(setActiveEngines([]))
      }
    }

    const handleProcessingStatus = (status: any) => {
      try {
        dispatch(setActiveEngines(status.engines_active || []))
      } catch (error) {
        console.error('Error handling processing status:', error)
      }
    }

    const handleError = (error: any) => {
      console.error('Socket error:', error)
      dispatch(setProcessing(false))
      dispatch(setActiveEngines([]))
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'system',
        content: `Error: ${error.message || 'Unknown error occurred'}`,
        timestamp: new Date(),
      }
      dispatch(addMessage(errorMessage))
    }

    socket.on('chat_response', handleChatResponse)
    socket.on('processing_status', handleProcessingStatus)
    socket.on('error', handleError)

    return () => {
      socket.off('chat_response', handleChatResponse)
      socket.off('processing_status', handleProcessingStatus)
      socket.off('error', handleError)
    }
  }, [socket, dispatch])

  const handleSendMessage = () => {
    if (!currentInput.trim() || isProcessing) return

    try {
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: currentInput,
        timestamp: new Date(),
      }
      
      dispatch(addMessage(userMessage))
      dispatch(setProcessing(true))
      
      const messageToSend = currentInput
      dispatch(setCurrentInput(''))

      if (socket && socket.connected) {
        // Send to backend via WebSocket
        socket.emit('chat_message', {
          message: messageToSend,
          user_profile: {
            user_id: safeUserProfile.userId,
            name: safeUserProfile.name,
            preferences: safePreferences,
            context: { role: safeUserProfile.role }
          }
        })
      } else {
        // Fallback: show error if not connected
        dispatch(setProcessing(false))
        const errorMessage: Message = {
          id: Date.now().toString(),
          type: 'system',
          content: 'Not connected to Supreme Jarvis backend. Please check the connection.',
          timestamp: new Date(),
        }
        dispatch(addMessage(errorMessage))
      }
    } catch (error) {
      console.error('Error sending message:', error)
      dispatch(setProcessing(false))
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'system',
        content: 'Error sending message. Please try again.',
        timestamp: new Date(),
      }
      dispatch(addMessage(errorMessage))
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  const handleClearChat = () => {
    dispatch(clearMessages())
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Chat Header */}
      <Paper
        sx={{
          p: 2,
          borderRadius: 0,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center' }}>
          <Typography variant="h6">
            Chat with Supreme Jarvis
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {/* Active Engines */}
            {activeEngines.length > 0 && (
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Typography variant="body2" color="text.secondary">
                  Active:
                </Typography>
                {activeEngines.map((engine) => (
                  <Chip
                    key={engine}
                    label={engine}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            )}
            
            <IconButton onClick={handleClearChat} size="small">
              <Clear />
            </IconButton>
          </Box>
        </Box>
      </Paper>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          backgroundColor: 'background.default',
        }}
      >
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {/* Processing Indicator */}
        {isProcessing && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              p: 2,
              mb: 2,
            }}
          >
            <CircularProgress size={20} />
            <Typography variant="body2" color="text.secondary">
              Supreme Jarvis is thinking...
            </Typography>
            {activeEngines.length > 0 && (
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                {activeEngines.map((engine) => (
                  <Chip
                    key={engine}
                    label={engine}
                    size="small"
                    color="primary"
                    variant="filled"
                  />
                ))}
              </Box>
            )}
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper
        sx={{
          p: 2,
          borderRadius: 0,
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            placeholder="Ask Supreme Jarvis anything..."
            value={currentInput}
            onChange={(e) => dispatch(setCurrentInput(e.target.value))}
            onKeyPress={handleKeyPress}
            disabled={isProcessing}
            variant="outlined"
            size="small"
          />
          
          <IconButton color="primary" disabled>
            <AttachFile />
          </IconButton>
          
          <IconButton
            color="primary"
            onClick={handleSendMessage}
            disabled={!currentInput.trim() || isProcessing}
          >
            <Send />
          </IconButton>
        </Box>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Press Enter to send, Shift+Enter for new line
        </Typography>
      </Paper>
    </Box>
  )
}

export default ChatInterface