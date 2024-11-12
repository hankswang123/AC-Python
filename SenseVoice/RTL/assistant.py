# -*- coding: utf-8 -*-
import os
import json
import pygame
import speech_recognition as sr

from tencentcloud.common import credential
import asr as asr
import tts as tts
import llm as llm

# 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
cred = credential.Credential(
       os.environ.get("TENCENTCLOUD_SECRET_ID"),
       os.environ.get("TENCENTCLOUD_SECRET_KEY"))

# Play the audio file, e.g. mp3/wav news file
def play_mp3(file_path):
    # Initialize the pygame mixer for playing mp3 files
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load(file_path)
    
    # Play the MP3 file
    pygame.mixer.music.play()
    
    # Keep the script running until the music stops
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Main loop for listening for questions
# The loop listens for questions and pauses the music when a question is detected
# The loop resumes the music when the question is answered
def audio_callback(recognizer, audio):

    print("Listening for questions...")

    try:
        speech_text = asr.asr_sensevoice(audio)
        if speech_text:

            #Question detected! Pause the music
            pygame.mixer.music.pause()
            position = pygame.mixer.music.get_pos() / 1000
            print(f"Playback paused at position: {position} seconds due to voice detected")

            #for debug purpose
            speech_text = "the main content of the audio file" 

            #Call Hunyuan to answer the question
            resp = llm.answer(cred, 
                            prompt=speech_text+"+"+str(position))

            #Speak out the answer
            resp_json = json.loads(resp)
            tts.handle_tts(cred, text=resp_json["Response"]["Answer"])

#             if "Stop" in speech_text:
#                 print("Question detected! Pausing music.")
#                 pygame.mixer.music.pause()

#             if "Continue" in speech_text:
#                 print("Question detected! Continue to play music.")
#                 pygame.mixer.music.unpause()

#             if "End" in speech_text:
#                 print("Question detected! Pausing music.")
#                 pygame.mixer.music.stop()
# #                break
#             else:
#                 print("No reseek needed. Resuming music.")
                # position = pygame.mixer.music.set_pos(float(resp_json["Response"]["Seek"]))
                # if position:
                #     print(f"Resuming music at position: {position}")
                #     pygame.mixer.music.set_pos(position)
#                pygame.mixer.music.unpause()
        else:
#            pygame.mixer.music.unpause()
            print("No question detected. Resuming playback.")

    except sr.UnknownValueError:
        print("Could not understand the audio")
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service")

# Main function
if __name__ == "__main__":

# Initialize the recognizer and microphone
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    # Start the background listening thread, user's questions will be detected in the background
    # the callback function audio_callback, will be called when a question is detected
    # the music will be paused and the question will be answered
    # user's questions length will be limited to 8 seconds
    stop_listening = recognizer.listen_in_background(microphone, audio_callback, phrase_time_limit=8)

    # Main loop for playing the music
    play_mp3("sap_news.mp3")

    # user can press 'q' to exit the program
    while True:
        if input() == 'q':
            break

    stop_listening(wait_for_stop=False)