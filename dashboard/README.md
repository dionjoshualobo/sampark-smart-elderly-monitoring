# SAMPARK Care Dashboard

An integrated health monitoring dashboard with voice assistant, chat interface, and emergency alert features.

## Features

### 1. Health Monitoring Dashboard
- **Real-time Health Metrics**: Heart rate, SpO2, steps, sleep hours
- **Risk Assessment**: ML-powered risk prediction (Low/Medium/High)
- **Caregiver Alerts**: Automatic notifications for health concerns
- **Patient Profile Management**: Edit and manage patient information
- **History Tracking**: View medication and meal compliance history
- **Auto-refresh**: Automatic data updates every 5 seconds

### 2. Integrated Voice Assistant 💬
The dashboard now includes a **floating assistant widget** with multiple interaction modes:

#### Text Chat
- Type messages directly to the health assistant
- Get instant responses about health status
- Ask questions about medications, meals, and symptoms
- Automatic health data extraction from conversations

#### Voice Recognition 🎤
- Click "Start Voice" to speak naturally
- Supports English (Indian accent optimized)
- Automatic speech-to-text conversion
- Voice responses with text-to-speech

#### Emergency Alert 🚨
- One-click emergency button
- Instantly notifies caregiver
- Creates high-priority alert in system
- Sends email notification (if configured)

### 3. Session Management
- Persistent chat history during session
- Automatic session ID generation
- Context-aware conversations
- Health data updates reflected in dashboard

## How to Use

### Starting the System

1. **Start the Backend Server**:
   ```bash
   cd /home/dion/sampark-smart-elderly-monitoring
   source venv/bin/activate
   python backend/app.py
   ```
   Backend will run on `http://127.0.0.1:5000`

2. **Open the Dashboard**:
   - Open `dashboard/index.html` in your web browser
   - Or use: `xdg-open dashboard/index.html`

### Using the Assistant Widget

#### Opening the Assistant
- Click the **💬 floating button** in the bottom-right corner
- The assistant widget will expand showing the chat interface

#### Text Chat Mode
1. Type your message in the text input box
2. Press Enter or click the ➤ send button
3. Wait for the assistant's response
4. Health data is automatically extracted and saved

**Example conversations**:
- "I slept 6 hours last night"
- "I missed my morning medicine"
- "My heart rate is 85 and oxygen is 96"
- "I'm not feeling well, feeling dizzy"

#### Voice Mode
1. Click **"Start Voice"** button (🎤)
2. Speak clearly when you see "Listening..."
3. The assistant will:
   - Convert your speech to text
   - Process the message
   - Respond with both text and voice
4. Voice automatically stops after you finish speaking

**Voice Tips**:
- Speak clearly and at normal pace
- Ensure microphone permissions are granted
- Works best in quiet environments
- Supports English (Indian accent)

#### Emergency Alert
1. Click the **"🚨 Emergency"** button
2. System immediately:
   - Creates high-priority alert
   - Notifies caregiver via email
   - Logs emergency in system
   - Provides voice confirmation

### Dashboard Navigation

#### Overview Tab
- Current risk assessment
- Latest health metrics
- Recent caregiver alerts

#### Patient Profile Tab
- View patient information
- Edit profile details
- Update emergency contacts

#### Meds History Tab
- Track missed medications
- View medication compliance
- Filter by date and risk level

#### Meals History Tab
- Monitor meal compliance
- Track missed meals
- Analyze eating patterns

#### Saved Records Tab
- Complete health record history
- Detailed metrics for each entry
- Risk scores and reasons

## Browser Compatibility

### Recommended Browsers
- **Chrome/Chromium** (Best support for voice features)
- **Edge** (Good support)
- **Firefox** (Limited voice support)
- **Safari** (Limited voice support)

### Required Permissions
- **Microphone Access**: Required for voice recognition
- **Notifications**: Optional for browser alerts

## Technical Details

### Assistant Widget Features
- **Floating UI**: Non-intrusive, always accessible
- **Minimizable**: Click header to minimize/expand
- **Responsive**: Works on desktop and mobile
- **Session Persistence**: Maintains conversation context
- **Auto-scroll**: Automatically scrolls to latest message

### API Integration
The assistant connects to these backend endpoints:
- `POST /assistant-message`: Send messages and get responses
- `GET /health-data/latest`: Fetch latest health data
- `GET /alerts`: Retrieve caregiver alerts

### Data Flow
1. User sends message (text or voice)
2. Message sent to backend with session ID
3. Backend extracts health data using LLM/local parser
4. Risk assessment performed
5. Response generated and returned
6. Dashboard auto-refreshes if new data created
7. Alerts sent to caregiver if needed

## Troubleshooting

### Voice Recognition Issues
**Problem**: "Speech recognition not supported"
- **Solution**: Use Chrome or Edge browser
- **Alternative**: Use text chat mode

**Problem**: "No speech detected"
- **Solution**: 
  - Check microphone permissions
  - Speak louder and clearer
  - Ensure microphone is not muted

**Problem**: "Microphone permission denied"
- **Solution**: 
  - Click the lock icon in browser address bar
  - Allow microphone access
  - Refresh the page

### Connection Issues
**Problem**: "Could not connect to backend"
- **Solution**:
  - Verify backend is running: `curl http://127.0.0.1:5000/`
  - Check backend terminal for errors
  - Ensure port 5000 is not blocked

**Problem**: "Backend waiting" message
- **Solution**:
  - Start the Flask backend server
  - Wait a few seconds for initialization
  - Click "Refresh" button

### Assistant Widget Issues
**Problem**: Widget not appearing
- **Solution**: 
  - Hard refresh browser (Ctrl+Shift+R)
  - Clear browser cache
  - Check browser console for errors

**Problem**: Messages not sending
- **Solution**:
  - Check backend connection status
  - Verify network connectivity
  - Check browser console for errors

## Configuration

### Backend URL
Default: `http://127.0.0.1:5000`

To change, edit line 829 in `index.html`:
```javascript
const backendUrl = "http://127.0.0.1:5000";
```

### Auto-refresh Interval
Default: 5 seconds

To change, edit line 1199 in `index.html`:
```javascript
timer = setInterval(loadDashboard, 5000); // 5000ms = 5 seconds
```

### Voice Recognition Language
Default: English (India) - "en-IN"

To change, edit line 1336 in `index.html`:
```javascript
recognizer.lang = "en-IN"; // Change to your preferred language code
```

## Security Notes

- All data stored locally in browser localStorage
- Session IDs generated using crypto.randomUUID()
- No sensitive data transmitted without encryption in production
- Backend should use HTTPS in production environments

## Development

### File Structure
```
dashboard/
├── index.html          # Main dashboard with integrated assistant
├── app.py             # Streamlit version (alternative)
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

### Customization
The assistant widget can be customized by modifying CSS variables in `index.html`:
- Colors: `--primary`, `--accent`, `--high` (emergency)
- Sizes: `.assistant-widget` width and max-height
- Position: `.assistant-widget` bottom and right values

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs for errors
3. Check browser console for JavaScript errors
4. Ensure all dependencies are installed

## Version History

### v2.0 (Current)
- ✅ Integrated voice assistant widget
- ✅ Text chat interface
- ✅ Voice recognition support
- ✅ Text-to-speech responses
- ✅ Emergency alert button
- ✅ Session management
- ✅ Real-time dashboard updates

### v1.0
- Basic health monitoring dashboard
- Patient profile management
- History tracking
- Auto-refresh functionality