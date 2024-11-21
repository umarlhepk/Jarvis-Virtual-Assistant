import speech_recognition as sr
import webbrowser
import pyttsx3
import pygame
import requests
import os
from gtts import gTTS
from openai import OpenAI

# Initialize components
recognizer = sr.Recognizer()
engine = pyttsx3.init()
news_api_key = "YOUR_NEWS_API_KEY"  # Replace with your actual key
openai_api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual key

# Command mappings
commands = {
    "open google": lambda: webbrowser.open("https://www.google.com"),
    "open facebook": lambda: webbrowser.open("https://www.facebook.com"),
    "open youtube": lambda: webbrowser.open("https://www.youtube.com"),
    "open linkedin": lambda: webbrowser.open("https://www.linkedin.com"),
}

music_library = {
    "song1": "https://example.com/song1",
    "song2": "https://example.com/song2",
    # Add more songs here
}

# Speak using Google Text-to-Speech
def speak(text):
    tts = gTTS(text)
    tts.save("temp.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    os.remove("temp.mp3")

# Fetch and read top news
def fetch_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=sa&apiKey={news_api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get("articles", [])[:5]  # Limit to top 5 headlines
            for article in articles:
                speak(article["title"])
        else:
            speak("Unable to fetch news at the moment.")
    except Exception as e:
        print(f"Error fetching news: {e}")
        speak("An error occurred while fetching news.")

# Handle OpenAI processing
def ai_process(command):
    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis."},
                {"role": "user", "content": command},
            ],
        )
        response = completion["choices"][0]["message"]["content"]
        return response
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "I'm sorry, I encountered an error with OpenAI."

# Process the user command
def process_command(command):
    command = command.lower()
    if command in commands:
        commands[command]()  # Execute mapped command
    elif command.startswith("play"):
        song = command.split(" ", 1)[-1]
        if song in music_library:
            webbrowser.open(music_library[song])
            speak(f"Playing {song}.")
        else:
            speak("Sorry, I couldn't find that song.")
    elif "news" in command:
        fetch_news()
    else:
        response = ai_process(command)
        speak(response)

# Listen for commands
def listen_for_command():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)  # Handle background noise
            print("Listening...")
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.WaitTimeoutError:
        print("Listening timed out.")
    return None

# Main loop
if __name__ == "__main__":
    speak("Initializing Jarvis...")
    while True:
        try:
            print("Say 'Jarvis' to activate.")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                wake_word = recognizer.recognize_google(audio).lower()
                if wake_word == "jarvis":
                    speak("Yes?")
                    command = listen_for_command()
                    if command:
                        process_command(command)
        except Exception as e:
            print(f"An error occurred: {e}")
