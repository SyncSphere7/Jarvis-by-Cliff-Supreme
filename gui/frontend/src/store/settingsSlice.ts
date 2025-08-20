import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UserProfile {
  userId: string
  name: string
  role: string
  experienceLevel: string
}

interface SettingsState {
  theme: 'light' | 'dark'
  userProfile: UserProfile
  preferences: {
    complexity: string
    style: string
    quantumPowers: boolean
    codingFocus: string
  }
}

const initialState: SettingsState = {
  theme: 'light',
  userProfile: {
    userId: 'default_user',
    name: 'User',
    role: 'developer',
    experienceLevel: 'intermediate',
  },
  preferences: {
    complexity: 'detailed',
    style: 'technical',
    quantumPowers: true,
    codingFocus: 'full_stack',
  },
}

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload
    },
    setUserProfile: (state, action: PayloadAction<Partial<UserProfile>>) => {
      state.userProfile = { ...state.userProfile, ...action.payload }
    },
    setPreferences: (state, action: PayloadAction<Partial<SettingsState['preferences']>>) => {
      state.preferences = { ...state.preferences, ...action.payload }
    },
  },
})

export const { setTheme, setUserProfile, setPreferences } = settingsSlice.actions

export default settingsSlice.reducer