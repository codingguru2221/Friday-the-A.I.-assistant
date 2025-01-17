import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
import pyaudio
import datetime 
import calendar
import webbrowser
from wake_word import detect_wake_word
import requests  # Add this import at the top
import json 
import os  # Add this import at the top with the others
import google.generativeai as genai  # pip install google-generativeai
from typing import Optional
from urllib.parse import quote_plus  # Add this import at the top
import yt_dlp  # pip install yt-dlp
import pafy  # pip install pafy youtube-dl
import pygame  # pip install pygame
from youtubesearchpython import VideosSearch  # pip install youtube-search-python
import time
import pyautogui
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # pip install webdriver-manager

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[1].id)
engine.setProperty('voice', voices[1].id)

# Add these near the top with other constants
GEMINI_API_KEY = "your-api-key"

# Initialize AI models
genai.configure(api_key=GEMINI_API_KEY)

# Add this near the top with other global variables
pygame.mixer.init()

def load_users():
    """Load users from JSON file"""
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {'users': []}

def save_users(users_data):
    """Save users to JSON file"""
    with open('users.json', 'w') as f:
        json.dump(users_data, f, indent=4)

def login_user():
    
    """Handle user login or registration"""
    users_data = load_users()
    
    speak("Welcome to Project Friday 2.0. Please tell me your name")
    user_name = takeCommand().lower()
    
    # Check if user exists
    for user in users_data['users']:
        if user['name'].lower() == user_name:
            speak(f"Welcome back, {get_title(user)}")
            return user
    
    # New user registration
    speak("I haven't met you before. Please tell me your gender (male/female)")
    gender = takeCommand().lower()
    
    # Create new user
    new_user = {
        'name': user_name,
        'gender': gender,
        'is_admin': False  # Only manually set this to True for admin users
    }
    
    users_data['users'].append(new_user)
    save_users(users_data)
    
    speak(f"Thank you for registering, {get_title(new_user)}")
    return new_user

def get_title(user):
    """Return appropriate title based on user type and gender"""
    if user['is_admin']:
        return f"Master {user['name']}"
    elif user['gender'] == 'female':
        return f"Ma'am {user['name']}"
    else:
        return f"Sir {user['name']}"

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        # Add energy threshold and dynamic ambient noise adjustment
        r.energy_threshold = 300
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        # Change language to generic English for better recognition
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")

    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that...")
        return "None"
    except sr.RequestError:
        print("Sorry, there was an error with the speech recognition service...")
        return "None"
    except Exception as e:
        print("Say that again please...")  
        return "None"
    return query

def wish_me(current_user):
    hour = datetime.datetime.now().hour
    day = calendar.day_name[datetime.datetime.now().weekday()]
    
    if hour >= 0 and hour < 12:
        greeting = "Good Morning"
    elif hour >= 12 and hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    title = get_title(current_user)
    speak(f"Hello {title}! {greeting}! Today is {day}. I am Friday, your AI assistant. How can I help you?")

def get_weather(city):
    """Get weather information for a given city"""
    # Replace with your actual API key from OpenWeatherMap
    api_key = "bc984e49929aa542528c1b5d28bf6aed"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    try:
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'  # For Celsius
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            return f"The temperature in {city} is {temp:.1f}°C with {desc}. The humidity is {humidity}%"
        else:
            return "Sorry, I couldn't fetch the weather information."
            
    except Exception as e:
        return f"An error occurred while fetching weather data: {str(e)}"

def get_ai_response(query: str) -> Optional[str]:
    """Get response from Gemini AI model"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        print(f"Error with Gemini: {str(e)}")
        return None

def automate_youtube(query):
    """
    Automates YouTube search and video playback using Selenium
    """
    try:
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        # Uncomment below line to run in headless mode (no GUI)
        # chrome_options.add_argument("--headless")
        
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                options=chrome_options)
        
        # Navigate to YouTube
        driver.get("https://www.youtube.com")
        
        # Accept cookies if the popup appears (adjust selector based on your region)
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Accept all']"))
            )
            cookie_button.click()
        except:
            pass  # Cookie popup might not appear
        
        # Find and fill the search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_box.send_keys(query)
        search_box.submit()
        
        # Wait for search results and click the first video
        first_video = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
        first_video.click()
        
        # Let the video play for a while (you can adjust or remove this)
        time.sleep(5)
        
        return driver  # Return the driver in case you need to control it later
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

if __name__ == "__main__":
    wake_word_detected = False
    current_user = None
    
    while True:
        if not wake_word_detected:
            wake_word_detected = detect_wake_word()
            if wake_word_detected:
                if current_user is None:
                    current_user = login_user()
                wish_me(current_user)
        
        if wake_word_detected:
            query = takeCommand().lower()

            # General conversation handlers
            if any(word in query for word in ['hello', 'hi', 'hey']):
                speak("Hello! How can I help you today?")
            
            elif 'how are you' in query:
                speak("I'm doing well, thank you for asking! How are you?")
            
            elif any(word in query for word in ['what is your name', 'who are you']):
                speak("I am Friday, your AI assistant, created to help you with various tasks.")
            
            elif 'what can you do' in query:
                speak("I can help you with various tasks like opening websites, answering questions, telling time, and having conversations.")
            
            elif any(word in query for word in ['thank', 'thanks']):
                speak("You're welcome! Is there anything else I can help you with?")
            
            elif 'time' in query:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The current time is {current_time}")
            
            elif 'date' in query:
                current_date = datetime.datetime.now().strftime("%B %d, %Y")
                speak(f"Today's date is {current_date}")
            
            elif 'joke' in query:
                speak("Here's a joke: Why don't programmers like nature? It has too many bugs!")
            
            elif 'weather' in query:
                speak("Which city would you like to know the weather for?")
                city_query = takeCommand().lower()
                if city_query != "none":
                    weather_info = get_weather(city_query)
                    speak(weather_info)
                else:
                    speak("Sorry, I couldn't understand the city name.")
            
            elif 'open youtube' in query:
                speak("Opening YouTube...")
                webbrowser.open("https://www.youtube.com")
            
            # Add new music playing functionality
            elif 'play music' in query or 'play song' in query:
                speak("What song would you like me to play?")
                song_query = takeCommand().lower()
                if song_query != "none":
                    speak(f"Playing {song_query} on YouTube...")
                    driver = automate_youtube(f"{song_query} official audio")
                    if driver:
                        speak("Video is now playing. Let me know if you need anything else!")
                    else:
                        speak("Sorry, I encountered an error while trying to play the video.")
                else:
                    speak("Sorry, I couldn't understand the song name.")
            
            elif any(word in query for word in ['goodbye', 'bye', 'exit', 'stop']):
                speak("Goodbye! Have a great day!")
                break
            
            elif 'shut down' in query or 'power off' in query or 'rest' in query:
                # Stop any playing music before going to sleep
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                        speak("Stopping music and going to sleep. Wake me up when you need me!")
                    else:
                        speak("Okay, I'll go to sleep now. Wake me up when you need me!")
                except:
                    speak("Okay, I'll go to sleep now. Wake me up when you need me!")
                    
                wake_word_detected = False
                continue
            
            elif 'none' in query or query == '':
                continue  # Just continue the loop without resetting wake_word_detected
            
            else:
                speak("Let me think about that...")
                response = get_ai_response(query)
                if response:
                    speak(response)
                    continue
                
                # If Gemini fails, use the default response
                speak("I am still learning new things and am not able to help you with that. if you have any other question then say that i I'll help you with that")
