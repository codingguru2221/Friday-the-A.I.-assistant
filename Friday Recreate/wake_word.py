import speech_recognition as sr
import time

def detect_wake_word(wake_words=["hey friday", "hello friday", "hi friday", "okay friday","wake up friday"]):
    """
    Continuously listens for any of the wake words and returns True when detected
    
    Args:
        wake_words (list): List of wake word phrases to listen for
    
    Returns:
        bool: True if wake word detected, False if error
    """
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        r.energy_threshold = 300
        r.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                print("Waiting for wake word...")
                audio = r.listen(source, timeout=None)
                text = r.recognize_google(audio, language='en-US').lower()
                
                # Check if any wake word variation is in the text
                if any(wake_word in text for wake_word in wake_words):
                    print("Wake word detected!")
                    return True
                    
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Error connecting to Google Speech Recognition service")
                return False
            except Exception as e:
                print(f"Error: {str(e)}")
                continue 