import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from playsound3 import playsound
AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Zjg0YzE2MC1kYjc2LTRkMWMtYTA2OS1kYmZmMDhkMDJjY2EiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjRhNmU2MzRkLWFmNGQtNDUwNy1hY2NmLWRjYjcxYzU4ZGJlMCJ9.9Jaww5ZP4Qw6byxpwRpuZasjkFi_9uExDYiIio1Z-cY" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)

import os
import tempfile
import time
from gtts import gTTS
import streamlit as st
# Fallback translation using requests
import requests
import json


# Import translation library with fallback
try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
class TranslationAgent:
    def __init__(self):
        if TRANSLATOR_AVAILABLE:
            self.translator = Translator()
        else:
            self.translator = None
            
        self.languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'tr': 'Turkish',
            'pl': 'Polish',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'et': 'Estonian',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'mt': 'Maltese',
            'ga': 'Irish',
            'cy': 'Welsh',
            'eu': 'Basque',
            'ca': 'Catalan',
            'gl': 'Galician',
            'is': 'Icelandic',
            'mk': 'Macedonian',
            'sq': 'Albanian',
            'be': 'Belarusian',
            'uk': 'Ukrainian',
            'he': 'Hebrew',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'tl': 'Filipino',
            'sw': 'Swahili',
            'am': 'Amharic',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'ne': 'Nepali',
            'or': 'Odia',
            'pa': 'Punjabi',
            'si': 'Sinhala',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ur': 'Urdu',
            'my': 'Myanmar',
            'km': 'Khmer',
            'lo': 'Lao',
            'ka': 'Georgian',
            'hy': 'Armenian',
            'az': 'Azerbaijani',
            'kk': 'Kazakh',
            'ky': 'Kyrgyz',
            'mn': 'Mongolian',
            'tg': 'Tajik',
            'tk': 'Turkmen',
            'uz': 'Uzbek',
            'fa': 'Persian',
            'ps': 'Pashto',
            'sd': 'Sindhi',
            'so': 'Somali',
            'xh': 'Xhosa',
            'zu': 'Zulu',
            'af': 'Afrikaans'
        }
        
        # TTS language mapping for compatibility
        self.tts_map = {
            'zh': 'zh-cn',
            'or': 'hi',
            'ps': 'fa',
            'sd': 'ur',
            'ky': 'ru',
            'kk': 'ru',
            'tg': 'ru',
            'tk': 'ru',
            'uz': 'ru',
            'am': 'ar',
            'my': 'th',
            'km': 'th',
            'lo': 'th',
        }
    
    def text_to_speech(self, text, language='en'):
        """
        Convert text to speech with fallbacks
        """
        try:
            # Map language for TTS compatibility
            tts_lang = self.tts_map.get(language, language)
            
            # Try primary language
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            tts.save(temp_file.name)
            playsound(temp_file.name)
            return temp_file.name
            
        except Exception as e:
            # Fallback to English if original fails
            try:
                if language != 'en':
                    tts = gTTS(text=text, lang='en', slow=False)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    temp_file.close()
                    tts.save(temp_file.name)
                    playsound(temp_file.name)
                    return temp_file.name
                else:
                    raise e
            except:
                raise Exception(f"Text-to-speech failed: {str(e)}")
@session.bind(
    name="speech_agent",
    description="This agent that take text and convert to speech"
)
async def speech_agent(
    agent_context: GenAIContext,
    test_arg
):
    """This agent convert text to speech in multiple languages"""
    agent_context.logger.info("Text to speech conversion has started")
    return TranslationAgent().text_to_speech(test_arg) 


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())