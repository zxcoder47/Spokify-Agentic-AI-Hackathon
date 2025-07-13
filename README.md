# Google Free Speech Recognition

A simple Python script that uses Google's free speech recognition service to transcribe audio from your microphone in real-time. No API keys required!

## Features

- **100% Free**: Uses Google's free speech recognition service
- **No API Keys**: Works without any authentication or registration
- **Multi-language Support**: Supports 5 languages (English, Spanish, German, French, Italian)
- **Real-time Processing**: Listens to your microphone and transcribes speech instantly
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

### Python Dependencies
```bash
pip install SpeechRecognition
```

### System Dependencies
- **Windows**: No additional dependencies required
- **macOS**: Install `portaudio` using Homebrew:
  ```bash
  brew install portaudio
  ```
- **Linux**: Install `portaudio` and `python3-dev`:
  ```bash
  sudo apt-get install portaudio19-dev python3-dev
  ```

## Installation

1. Clone or download the script
2. Install the required Python package:
   ```bash
   pip install SpeechRecognition
   ```
3. Run the script:
   ```bash
   python text_to_speach3.py
   ```

## Usage

### Basic Usage

1. Run the script:
   ```bash
   python text_to_speach.py
   ```

2. Select your language:
   ```
   Select language:
   1. English (US)
   2. Spanish (Spain)
   3. German
   4. French
   5. Italian
   Enter language choice (1-5): 1
   ```

3. Wait for the microphone to adjust:
   ```
   Adjusting for ambient noise...
   ```

4. Start speaking when you see:
   ```
   Listening...
   ```

5. The transcription will appear:
   ```
   Recognizing with Google Free API...
   Transcription: Hello, this is a test of the speech recognition system.
   ```

### Supported Languages

| Language | Code | Description |
|----------|------|-------------|
| English (US) | en-US | American English |
| Spanish (Spain) | es-ES | Castilian Spanish |
| German | de-DE | Standard German |
| French | fr-FR | Standard French |
| Italian | it-IT | Standard Italian |

## How It Works

1. **Microphone Setup**: The script initializes your system's default microphone
2. **Noise Adjustment**: Automatically adjusts for ambient noise in your environment
3. **Audio Capture**: Listens for speech with a 15-second timeout
4. **Speech Recognition**: Sends audio to Google's free speech recognition service
5. **Text Output**: Returns the transcribed text

## Code Structure

### Functions

#### `transcribe_with_google_free(language_code: str = "en-US") -> Optional[str]`
Main transcription function that:
- Sets up the microphone and recognizer
- Captures audio from the microphone
- Sends audio to Google's free speech recognition API
- Returns the transcribed text or None if failed

**Parameters:**
- `language_code`: Language code for recognition (default: "en-US")

**Returns:**
- `str`: Transcribed text if successful
- `None`: If transcription fails

#### `main()`
User interface function that:
- Displays language options
- Gets user input for language selection
- Calls the transcription function

## Error Handling

The script handles several types of errors:

- **UnknownValueError**: When speech is unclear or inaudible
- **RequestError**: When there's a network or service issue
- **General Exception**: Any other unexpected errors

## Example Output

```
Google Free Speech Recognition (No API key needed)

Select language:
1. English (US)
2. Spanish (Spain)
3. German
4. French
5. Italian
Enter language choice (1-5): 1

Adjusting for ambient noise...
Listening...
Recognizing with Google Free API...
Transcription: Hello world, this is a test of speech recognition.
```

## Troubleshooting

### Common Issues

1. **No microphone detected**:
   - Check if your microphone is properly connected
   - Ensure microphone permissions are granted to Python

2. **"Could not understand audio"**:
   - Speak more clearly and loudly
   - Reduce background noise
   - Check microphone positioning

3. **Network errors**:
   - Ensure you have an active internet connection
   - Google's service may be temporarily unavailable

4. **Import errors**:
   - Make sure SpeechRecognition is installed: `pip install SpeechRecognition`

### Performance Tips

- **Quiet Environment**: Use in a quiet room for best results
- **Clear Speech**: Speak clearly and at a moderate pace
- **Good Microphone**: Use a quality microphone if possible
- **Internet Connection**: Ensure stable internet connection

## Technical Details

### Dependencies
- `speech_recognition`: Python library for performing speech recognition
- `typing`: For type hints (Optional)

### Audio Processing
- **Timeout**: 15 seconds for audio capture
- **Format**: Audio is automatically converted to the format expected by Google's API
- **Noise Reduction**: Automatic ambient noise adjustment

### Privacy
- Audio is sent to Google's servers for processing
- No audio data is stored locally
- Google's privacy policy applies to the speech recognition service

## License

This script is provided as-is for educational and personal use. Please respect Google's terms of service when using their speech recognition API.

## Contributing

Feel free to submit issues and enhancement requests!

## Changelog

### Version 1.0
- Initial release with Google Free Speech Recognition
- Multi-language support
- Real-time transcription
- Error handling and user-friendly interface
