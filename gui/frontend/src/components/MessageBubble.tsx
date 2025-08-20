import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  ContentCopy,
  Person,
  Psychology,
  Info,
} from '@mui/icons-material'
import { Message } from '../store/chatSlice'

interface MessageBubbleProps {
  message: Message
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user'
  const isSystem = message.type === 'system'

  const handleCopy = () => {
    try {
      navigator.clipboard.writeText(message.content)
    } catch (error) {
      console.error('Failed to copy message:', error)
    }
  }

  const formatTime = (date: Date) => {
    try {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch (error) {
      return 'Invalid time'
    }
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          maxWidth: '70%',
          display: 'flex',
          flexDirection: isUser ? 'row-reverse' : 'row',
          alignItems: 'flex-start',
          gap: 1,
        }}
      >
        {/* Avatar */}
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            backgroundColor: isUser ? 'primary.main' : isSystem ? 'info.main' : 'secondary.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            flexShrink: 0,
          }}
        >
          {isUser ? <Person /> : isSystem ? <Info /> : <Psychology />}
        </Box>

        {/* Message Content */}
        <Box sx={{ flex: 1 }}>
          <Paper
            sx={{
              p: 2,
              backgroundColor: isUser
                ? 'primary.main'
                : isSystem
                ? 'info.light'
                : 'background.paper',
              color: isUser ? 'primary.contrastText' : 'text.primary',
              borderRadius: 2,
              position: 'relative',
            }}
          >
            {/* Message Text */}
            <Typography
              variant="body1"
              sx={{
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {message.content}
            </Typography>

            {/* Metadata for Assistant Messages */}
            {!isUser && !isSystem && (
              <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
                {message.confidence && (
                  <Chip
                    label={`${(message.confidence * 100).toFixed(0)}% confident`}
                    size="small"
                    color="success"
                    variant="outlined"
                  />
                )}
                
                {message.processingTime && (
                  <Chip
                    label={`${message.processingTime.toFixed(2)}s`}
                    size="small"
                    variant="outlined"
                  />
                )}
                
                {message.enginesUsed && message.enginesUsed.length > 0 && (
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {message.enginesUsed.map((engine) => (
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
              </Box>
            )}

            {/* Copy Button */}
            <Tooltip title="Copy message">
              <IconButton
                size="small"
                onClick={handleCopy}
                sx={{
                  position: 'absolute',
                  top: 4,
                  right: 4,
                  opacity: 0.7,
                  '&:hover': { opacity: 1 },
                }}
              >
                <ContentCopy fontSize="small" />
              </IconButton>
            </Tooltip>
          </Paper>

          {/* Timestamp */}
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              display: 'block',
              mt: 0.5,
              textAlign: isUser ? 'right' : 'left',
            }}
          >
            {formatTime(message.timestamp)}
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}

export default MessageBubble