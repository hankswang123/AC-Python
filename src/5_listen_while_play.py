# -*- coding: utf-8 -*-
import pygame
import time
import threading
import speech_recognition as sr

# Initialize the pygame mixer for playing mp3 files
pygame.mixer.init()

def play_mp3(file_path):
    
    # Load the MP3 file
    pygame.mixer.music.load(file_path)
    
    # Play the MP3 file
    pygame.mixer.music.play()
    
    # Keep the script running until the music stops
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def audio_callback(recognizer, audio):
    try:
        print("Recognizing audio...")
        prompt = recognizer.recognize_whisper(audio, model="base", language="chinese")
        print(prompt)
#        assistant.answer(prompt, webcam_stream.read(encode=True))

    except sr.UnknownValueError:
        print("There was an error processing the audio.")

def listen_for_questions():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:

    #        print("Press 'Enter' to ask a question...")
    #        input()  # Wait for user to press Enter
        print("Listening for questions...")
        with microphone as source:
            audio = recognizer.listen(source)

        try:
            # Recognize the speech using OpenAI's Whisper model
            speech_text = recognizer.recognize_whisper(audio, model="base", language="english")
            print(f"User said: {speech_text}")

            # Check if the speech is a question
            # if "?" in speech_text:
            #     print("Question detected! Pausing music.")
            #     pygame.mixer.music.pause()
            #     break

            if "Stop" in speech_text:
                print("Question detected! Pausing music.")
                pygame.mixer.music.pause()

            if "Continue" in speech_text:
                print("Question detected! Continue to play music.")
                pygame.mixer.music.unpause()

            if "End" in speech_text:
                print("Question detected! Pausing music.")
                pygame.mixer.music.stop()
                break

        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service")

#if __name__ == "__main__":

 #   file_path = "sap_news.mp3"
 #   play_mp3(file_path)

 # Specify the mp3 file path
mp3_file = "sap_news.mp3"
play_mp3(mp3_file)

# # Create threads for playing music and listening for questions
# music_thread = threading.Thread(target=play_mp3, args=(mp3_file,))
# listen_thread = threading.Thread(target=listen_for_questions)

# # Start the threads
# listen_thread.start()
# music_thread.start()

# # Wait for the threads to complete
# listen_thread.join()
# music_thread.join()

recognizer = sr.Recognizer()
microphone = sr.Microphone()
with microphone as source:
    recognizer.adjust_for_ambient_noise(source)

stop_listening = recognizer.listen_in_background(microphone, audio_callback, phrase_time_limit=8)
stop_listening(wait_for_stop=False)