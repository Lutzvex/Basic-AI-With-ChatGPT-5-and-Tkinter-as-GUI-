# Keyshia AI - Advanced Chatbot GUI

A modern PyQt5-based AI chatbot GUI that integrates GPT-5 and DALL-E 3 with your existing voice assistant features.

## 🚀 Features

- **Modern GUI Interface**: Clean, dark-themed chat interface with chat bubbles
- **GPT-5 Integration**: Real-time chat with GPT-5 API
- **DALL-E 3 Image Generation**: Generate images directly from text prompts
- **Voice Commands**: Integrated voice recognition and speech synthesis
- **Chat History**: Export and manage conversation history
- **Voice Assistant Bridge**: Seamlessly connects with your existing voice assistant

## 📋 Requirements

- Python 3.7+
- PyQt5
- OpenAI Python client
- Additional packages listed in `requirements.txt`

## 🔧 Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   - Create a `.env` file in the project directory
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

4. **Run the application**:
   ```bash
   python run_chatbot.py
   ```

## 🎯 Usage

### Basic Chat
- Type messages in the text input and press Enter or click Send
- Use voice commands by clicking the microphone button

### Image Generation
- Type "generate image: [your description]" in the chat
- Or use the dedicated image generator in the sidebar

### Voice Commands
- **"wake up"** - Activate voice recognition
- **"generate image: [description]"** - Generate images
- **"clear chat"** - Clear conversation history

### File Sharing
- Click the 📎 button to attach files
- Drag and drop files directly into the chat area

## 🔗 Integration with Existing Voice Assistant

The GUI seamlessly integrates with your existing voice assistant features:

1. **Voice Recognition**: Uses the same speech recognition engine
2. **Text-to-Speech**: Uses the same pyttsx3 engine
3. **Commands**: All existing voice commands work through the GUI
4. **Features**: Camera, music, web browsing, etc. are accessible via GUI

## 🎨 Customization

### Themes
- Dark theme is enabled by default
- Modify `config.py` to change colors and styling

### Voice Settings
- Adjust voice rate and volume in `config.py`
- Change voice selection in `voice_bridge.py`

## 📁 File Structure

```
├── ai_chatbot_gui.py      # Main GUI application
├── run_chatbot.py         # Launcher script
├── config.py             # Configuration settings
├── voice_bridge.py       # Voice assistant integration
├── requirements.txt      # Dependencies
├── README.md            # This file
└── .env                 # API keys (create this)
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module found" errors**:
   - Run `pip install -r requirements.txt`

2. **Voice recognition not working**:
   - Check microphone permissions
   - Ensure PyAudio is installed correctly

3. **API errors**:
   - Verify your OpenAI API key in `.env`
   - Check internet connection

4. **GUI not displaying**:
   - Ensure PyQt5 is properly installed
   - Try running with `python -m ai_chatbot_gui`

## 🔄 Updating

To update the application:
1. Pull the latest changes
2. Run `pip install -r requirements.txt` to update dependencies
3. Restart the application

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Ensure all dependencies are correctly installed
3. Verify your API key configuration
