import { configureStore } from '@reduxjs/toolkit'
import chatReducer from './chatSlice'
import socketReducer from './socketSlice'
import systemReducer from './systemSlice'
import settingsReducer from './settingsSlice'

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    socket: socketReducer,
    system: systemReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['socket/setSocket'],
        ignoredPaths: ['socket.socket'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch