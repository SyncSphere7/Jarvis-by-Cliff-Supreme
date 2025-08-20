import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  confidence?: number
  enginesUsed?: string[]
  processingTime?: number
}

interface ChatState {
  messages: Message[]
  isProcessing: boolean
  activeEngines: string[]
  currentInput: string
}

const initialState: ChatState = {
  messages: [
    {
      id: '1',
      type: 'system',
      content: 'Welcome to Supreme Jarvis! I\'m ready to assist you with my god-like capabilities. How can I help you today?',
      timestamp: new Date(),
    }
  ],
  isProcessing: false,
  activeEngines: [],
  currentInput: '',
}

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload)
    },
    setProcessing: (state, action: PayloadAction<boolean>) => {
      state.isProcessing = action.payload
    },
    setActiveEngines: (state, action: PayloadAction<string[]>) => {
      state.activeEngines = action.payload
    },
    setCurrentInput: (state, action: PayloadAction<string>) => {
      state.currentInput = action.payload
    },
    clearMessages: (state) => {
      state.messages = [initialState.messages[0]] // Keep welcome message
    },
  },
})

export const {
  addMessage,
  setProcessing,
  setActiveEngines,
  setCurrentInput,
  clearMessages,
} = chatSlice.actions

export default chatSlice.reducer