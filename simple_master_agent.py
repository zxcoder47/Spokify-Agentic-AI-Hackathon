"""
Simple Master Agent for Speech Recognition

A simplified version of the master agent that provides basic orchestration
for speech recognition tasks with essential features only.

Features:
- Basic session management
- Single and continuous transcription modes
- Simple statistics tracking
- Easy-to-use interface

Author: AI Assistant
Version: 1.0 (Simple)
"""

import datetime
import time
from typing import Optional

# Import your speech recognition module
from text_to_speach3 import transcribe_with_google_free


class SimpleMasterAgent:
    """
    Simple Master Agent for Speech Recognition
    
    Provides basic orchestration for speech recognition tasks with
    essential features in a user-friendly interface.
    """
    
    def __init__(self):
        """Initialize the Simple Master Agent"""
        self.session_start = datetime.datetime.now()
        self.total_transcriptions = 0
        self.successful_transcriptions = 0
        self.transcription_history = []
        self.is_running = False
        
        # Supported languages
        self.languages = {
            "1": {"code": "en-US", "name": "English (US)"},
            "2": {"code": "es-ES", "name": "Spanish (Spain)"},
            "3": {"code": "de-DE", "name": "German"},
            "4": {"code": "fr-FR", "name": "French"},
            "5": {"code": "it-IT", "name": "Italian"}
        }
        
        print("🤖 Simple Master Agent initialized!")
        print(f"📅 Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("🎤 SIMPLE SPEECH RECOGNITION AGENT")
        print("="*50)
        print("1. Single Transcription")
        print("2. Continuous Listening")
        print("3. View Statistics")
        print("4. Show History")
        print("5. Help")
        print("6. Exit")
        print("="*50)
    
    def get_language_choice(self) -> str:
        """Get language selection from user"""
        print("\n🌐 Select Language:")
        for key, lang in self.languages.items():
            print(f"{key}. {lang['name']}")
        
        while True:
            choice = input("\nEnter language choice (1-5): ").strip()
            if choice in self.languages:
                return self.languages[choice]['code']
            else:
                print("Invalid choice. Please enter 1-5.")
    
    def single_transcription(self):
        """Run a single transcription"""
        language_code = self.get_language_choice()
        
        print(f"\n🎯 Starting transcription in {language_code}")
        start_time = time.time()
        
        try:
            # Run transcription
            result = transcribe_with_google_free(language_code)
            duration = time.time() - start_time
            
            # Update statistics
            self.total_transcriptions += 1
            
            if result:
                self.successful_transcriptions += 1
                # Save to history
                self.transcription_history.append({
                    'time': datetime.datetime.now().strftime('%H:%M:%S'),
                    'text': result,
                    'language': language_code,
                    'success': True
                })
                print(f"✅ Transcription completed in {duration:.2f} seconds")
            else:
                self.transcription_history.append({
                    'time': datetime.datetime.now().strftime('%H:%M:%S'),
                    'text': "No speech detected",
                    'language': language_code,
                    'success': False
                })
                print("❌ No speech detected")
                
        except Exception as e:
            self.total_transcriptions += 1
            self.transcription_history.append({
                'time': datetime.datetime.now().strftime('%H:%M:%S'),
                'text': f"Error: {str(e)}",
                'language': language_code,
                'success': False
            })
            print(f"❌ Error: {e}")
    
    def continuous_mode(self):
        """Run continuous listening mode"""
        language_code = self.get_language_choice()
        
        print(f"\n🔄 Starting continuous mode in {language_code}")
        print("Press Ctrl+C to stop")
        
        self.is_running = True
        
        try:
            while self.is_running:
                print("\n--- Listening (Ctrl+C to stop) ---")
                
                start_time = time.time()
                result = transcribe_with_google_free(language_code)
                duration = time.time() - start_time
                
                self.total_transcriptions += 1
                
                if result:
                    self.successful_transcriptions += 1
                    self.transcription_history.append({
                        'time': datetime.datetime.now().strftime('%H:%M:%S'),
                        'text': result,
                        'language': language_code,
                        'success': True
                    })
                    print(f"📝 Transcribed: {result}")
                else:
                    print("⚠️  No speech detected, continuing...")
                
                time.sleep(1)  # Brief pause
                
        except KeyboardInterrupt:
            print("\n🛑 Continuous mode stopped")
        finally:
            self.is_running = False
    
    def show_statistics(self):
        """Display session statistics"""
        success_rate = (self.successful_transcriptions / max(self.total_transcriptions, 1)) * 100
        session_duration = datetime.datetime.now() - self.session_start
        
        print("\n📊 SESSION STATISTICS")
        print("="*35)
        print(f"Session Duration: {str(session_duration).split('.')[0]}")
        print(f"Total Transcriptions: {self.total_transcriptions}")
        print(f"Successful: {self.successful_transcriptions}")
        print(f"Failed: {self.total_transcriptions - self.successful_transcriptions}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*35)
    
    def show_history(self):
        """Display transcription history"""
        if not self.transcription_history:
            print("\n📋 No transcriptions yet.")
            return
        
        print("\n📋 TRANSCRIPTION HISTORY")
        print("="*50)
        
        # Show last 10 entries
        recent_history = self.transcription_history[-10:]
        
        for i, entry in enumerate(recent_history, 1):
            status = "✅" if entry['success'] else "❌"
            print(f"{i:2d}. {status} [{entry['time']}] {entry['language']}: {entry['text'][:40]}...")
        
        if len(self.transcription_history) > 10:
            print(f"\n... and {len(self.transcription_history) - 10} more entries")
    
    def show_help(self):
        """Display help information"""
        print("\n📖 HELP - SIMPLE SPEECH RECOGNITION AGENT")
        print("="*50)
        print("1. Single Transcription - Record and transcribe once")
        print("2. Continuous Listening - Keep listening and transcribing")
        print("3. View Statistics     - Show session performance")
        print("4. Show History        - View recent transcriptions")
        print("5. Help               - Show this help message")
        print("6. Exit               - Exit the agent")
        print("\n💡 Tips:")
        print("• Speak clearly and at moderate pace")
        print("• Use a quiet environment")
        print("• Ensure good internet connection")
        print("• Press Ctrl+C to stop continuous mode")
        print("="*50)
    
    def run(self):
        """Main execution loop"""
        while True:
            try:
                self.display_menu()
                choice = input("\n🤖 Enter your choice (1-6): ").strip()
                
                if choice == "1":
                    self.single_transcription()
                elif choice == "2":
                    self.continuous_mode()
                elif choice == "3":
                    self.show_statistics()
                elif choice == "4":
                    self.show_history()
                elif choice == "5":
                    self.show_help()
                elif choice == "6":
                    print("\n👋 Thank you for using Simple Master Agent!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Agent interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("🔄 Continuing...")


def main():
    """Main function to run the Simple Master Agent"""
    try:
        agent = SimpleMasterAgent()
        agent.run()
    except Exception as e:
        print(f"❌ Failed to start Simple Master Agent: {e}")


if __name__ == "__main__":
    main()
