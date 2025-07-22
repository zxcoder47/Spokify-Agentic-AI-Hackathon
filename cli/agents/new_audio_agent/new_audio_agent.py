import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
import speech_recognition as sr

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiYWU3OTQzYS00ODc3LTQ3Y2MtYjVmOS0zOGVlOWM0ODJjNGYiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjRhNmU2MzRkLWFmNGQtNDUwNy1hY2NmLWRjYjcxYzU4ZGJlMCJ9.tymEEwteF2Gv4hNZUZgrA1lzeQj2vAofdyxQvRnjKY0" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)
@session.bind(
    name="audio_agent",
    description="This agent uses mic access to input line spoken audio and transcribe it into text"
)
async def audio_agent(
    agent_context: GenAIContext
):
    """This agent handles audio in and out stream"""
    agent_context.logger.info("This audio has started")
    return transcribe_with_google_free()
def transcribe_with_google_free(language_code: str = "en-US"):
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

async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()


if __name__ == "__main__":
    asyncio.run(main())

