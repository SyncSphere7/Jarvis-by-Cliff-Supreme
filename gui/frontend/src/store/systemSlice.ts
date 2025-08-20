import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface Engine {
  name: string
  status: 'active' | 'idle' | 'error' | 'demo'
  activity: number
  lastUsed?: string
}

interface SystemState {
  engines: Engine[]
  overallHealth: string
  godlikeMode: boolean
  activeSessions: number
  uptime: string
}

const initialState: SystemState = {
  engines: [],
  overallHealth: 'unknown',
  godlikeMode: false,
  activeSessions: 0,
  uptime: '0m',
}

const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    setEngines: (state, action: PayloadAction<Engine[]>) => {
      state.engines = action.payload
    },
    updateEngine: (state, action: PayloadAction<{ name: string; updates: Partial<Engine> }>) => {
      const engine = state.engines.find(e => e.name === action.payload.name)
      if (engine) {
        Object.assign(engine, action.payload.updates)
      }
    },
    setSystemStatus: (state, action: PayloadAction<{
      overallHealth: string
      godlikeMode: boolean
      activeSessions: number
      uptime: string
    }>) => {
      state.overallHealth = action.payload.overallHealth
      state.godlikeMode = action.payload.godlikeMode
      state.activeSessions = action.payload.activeSessions
      state.uptime = action.payload.uptime
    },
  },
})

export const { setEngines, updateEngine, setSystemStatus } = systemSlice.actions

export default systemSlice.reducer