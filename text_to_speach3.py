"""
Google Free Speech Recognition Script

A simple Python script that uses Google's free speech recognition service 
to transcribe audio from your microphone in real-time. No API keys required!

Features:
- 100% Free (uses Google's free speech recognition service)
- No API Keys needed
- Multi-language support (English, Spanish, German, French, Italian)
- Real-time processing
- Cross-platform compatibility

Requirements:
- Python 3.6+
- SpeechRecognition library: pip install SpeechRecognition
- Working microphone
- Internet connection

Usage:
1. Run: python text_to_speach3.py
2. Select language (1-5)
3. Speak when prompted
4. View transcription results

Author: AI Assistant
Version: 1.0
"""

import speech_recognition as sr
from typing import Optional

# Free API options - No API keys needed for basic functionality

def transcribe_with_google_free(language_code: str = "en-US") -> Optional[str]:
    """
    Transcribe audio using Google's FREE speech recognition service (no API key needed)
    This is completely free and works without any authentication
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        with mic as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, timeout=15)

        print("Recognizing with Google Free API...")
        # Use Google's free speech recognition service
        text = recognizer.recognize_google(audio, language=language_code)
        print(f"Transcription: {text}")
        return text
        
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Error with the recognition service: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """
    Main function to demonstrate Google Free Speech Recognition
    """
    print("Google Free Speech Recognition (No API key needed)")
    
    # Language options
    languages = {
        "1": "en-US",
        "2": "es-ES", 
        "3": "de-DE",
        "4": "fr-FR",
        "5": "it-IT"
    }
    
    print("\nSelect language:")
    print("1. English (US)")
    print("2. Spanish (Spain)")
    print("3. German")
    print("4. French")
    print("5. Italian")
    
    lang_choice = input("Enter language choice (1-5): ").strip()
    language_code = languages.get(lang_choice, "en-US")
    
    # Run Google free speech recognition
    transcribe_with_google_free(language_code)

if __name__ == "__main__":
    main()