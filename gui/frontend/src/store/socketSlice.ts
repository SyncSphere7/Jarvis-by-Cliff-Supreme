import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { io, Socket } from 'socket.io-client'

interface SocketState {
  socket: Socket | null
  isConnected: boolean
  error: string | null
}

const initialState: SocketState = {
  socket: null,
  isConnected: false,
  error: null,
}

const socketSlice = createSlice({
  name: 'socket',
  initialState,
  reducers: {
    setSocket: (state, action: PayloadAction<Socket>) => {
      state.socket = action.payload
    },
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    clearSocket: (state) => {
      state.socket = null
      state.isConnected = false
      state.error = null
    },
  },
})

export const { setSocket, setConnected, setError, clearSocket } = socketSlice.actions

// Thunk actions
export const connectSocket = () => (dispatch: any) => {
  try {
    const socket = io('http://localhost:5001', {
      transports: ['websocket', 'polling'],
    })

    socket.on('connect', () => {
      console.log('Connected to Supreme Jarvis backend')
      dispatch(setConnected(true))
      dispatch(setError(null))
    })

    socket.on('disconnect', () => {
      console.log('Disconnected from Supreme Jarvis backend')
      dispatch(setConnected(false))
    })

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error)
      dispatch(setError(error.message))
      dispatch(setConnected(false))
    })

    dispatch(setSocket(socket))
  } catch (error) {
    console.error('Failed to create socket connection:', error)
    dispatch(setError('Failed to connect to Supreme Jarvis'))
  }
}

export const disconnectSocket = () => (dispatch: any, getState: any) => {
  const { socket } = getState().socket
  if (socket) {
    socket.disconnect()
    dispatch(clearSocket())
  }
}

export default socketSlice.reducer