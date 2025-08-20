# Supreme Jarvis GUI

A modern, user-friendly web interface for Supreme Jarvis with real-time communication and intuitive design.

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)
```bash
cd gui
python3 launch.py
```

This will:
- Install all dependencies automatically
- Start both backend and frontend servers
- Open your web browser to the GUI
- Handle shutdown gracefully

### Option 2: Manual Launch

#### Backend (Terminal 1)
```bash
cd gui/backend
pip install -r requirements.txt
python3 app.py
```

#### Frontend (Terminal 2)
```bash
cd gui/frontend
npm install
npm run dev
```

Then open http://localhost:3000 in your browser.

## 🌟 Features

### Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live communication with Supreme Jarvis
- **Professional UI**: Clean, intuitive Material-UI design
- **Dark/Light Theme**: Toggle between themes

### Chat Interface
- **Natural Conversation**: Chat with Supreme Jarvis like a human assistant
- **Real-time Processing**: See which engines are working on your request
- **Message History**: Scrollable conversation history
- **Copy & Export**: Easy copying and exporting of conversations

### Supreme Dashboard
- **Engine Monitoring**: Real-time status of all 10 Supreme engines
- **System Health**: Overall system health and performance metrics
- **Godlike Mode**: Visual indicator when supreme powers are active
- **Activity Feed**: Live feed of system activities

### Quick Actions
- **Development**: Code review, debugging, architecture design
- **Analysis**: Performance analysis, data insights, market research
- **Security**: Security audits, quantum encryption, threat assessment
- **Templates**: Pre-built requests for common tasks

### File Integration
- **File Upload**: Drag and drop files for analysis
- **Project Integration**: Connect your project directories
- **Code Preview**: Preview suggested changes before applying

## 🏗️ Architecture

### Frontend (React.js)
- **React 18** with TypeScript
- **Material-UI** for components
- **Redux Toolkit** for state management
- **Socket.IO** for real-time communication
- **Vite** for fast development

### Backend (Flask)
- **Flask** with WebSocket support
- **Flask-SocketIO** for real-time communication
- **CORS** enabled for cross-origin requests
- **Integration** with Supreme Jarvis core modules

## 🔧 Development

### Project Structure
```
gui/
├── frontend/           # React.js frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── store/      # Redux store
│   │   └── main.tsx    # Entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/            # Flask backend
│   ├── app.py          # Main Flask app
│   └── requirements.txt
├── launch.py           # One-click launcher
└── README.md
```

### Available Scripts

#### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run lint` - Lint code

#### Backend
- `python3 app.py` - Start Flask server
- `python3 -m pytest` - Run tests

## 🌐 API Endpoints

### REST API
- `GET /api/health` - Health check
- `GET /api/system/status` - System status
- `POST /api/chat` - Process chat message

### WebSocket Events
- `chat_message` - Send chat message
- `chat_response` - Receive chat response
- `request_system_status` - Request system status
- `system_status` - Receive system status
- `engine_activity` - Engine activity updates

## 🎯 Usage Examples

### Basic Chat
1. Open http://localhost:3000
2. Type your message in the chat input
3. Press Enter or click Send
4. Watch Supreme Jarvis process your request in real-time

### Quick Actions
1. Click on any quick action in the sidebar
2. The template will populate the chat input
3. Customize if needed and send

### System Monitoring
1. Check the status panel on the right
2. Monitor engine activity and system health
3. View real-time activity feed

## 🔒 Security

- **CORS Protection**: Configured for localhost development
- **Input Validation**: All inputs are validated and sanitized
- **WebSocket Security**: Secure WebSocket connections
- **File Upload Security**: Safe file handling and validation

## 🚀 Production Deployment

For production deployment:

1. Build the frontend:
   ```bash
   cd gui/frontend
   npm run build
   ```

2. Configure production settings in backend
3. Use a production WSGI server like Gunicorn
4. Set up reverse proxy with Nginx
5. Configure SSL certificates

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
- Backend (5000): `lsof -ti:5000 | xargs kill -9`
- Frontend (3000): `lsof -ti:3000 | xargs kill -9`

**Dependencies not installing:**
- Make sure you have Node.js and Python 3.8+ installed
- Try clearing npm cache: `npm cache clean --force`
- Try clearing pip cache: `pip cache purge`

**WebSocket connection failed:**
- Check if backend is running on port 5000
- Verify CORS settings in backend
- Check browser console for errors

### Getting Help

If you encounter issues:
1. Check the browser console for errors
2. Check the backend terminal for error messages
3. Verify all dependencies are installed
4. Try restarting both servers

## 📝 License

This project is part of the Supreme Jarvis system.