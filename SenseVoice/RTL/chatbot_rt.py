import threading
import time
import pyaudio
import speech_recognition as sr

# -*- coding: utf-8 -*-
import os
import json

from tencentcloud.common import credential
import asr as asr
import RTL.tts_rt as tts_rt
import RTL.llm_rt as llm_rt

# Overview:
# rt: Real Time
# This is the chatbot class that will be used to interact with the user
# User can interupt the chatbot by speaking to it at any time, the chatbot will stop 
# the current playback if user speaks are detected
# The chatbot will listen for user input, recognize the input, and generate a response
# The response will be played back to the user
# The chatbot will continue to listen for user input until the user exits the program

# Some key features of the chatbot:
# The user can exit the program by pressing 'q'
# The chatbot will close the PyAudio instance when done
# The chatbot will also stop any ongoing playback when done
# The chatbot will use locks to ensure that shared audio resources are managed safely
# The chatbot will use threading to handle playback and listening in the background
# The chatbot will use events to signal stopping playback
class Chatbot:

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None

        self.is_playing = False
        self.stop_event = threading.Event()  # Event to signal stopping
        self.playback_thread = None
        self.playback_lock = threading.Lock()

        self.greeting = "Chatbot is ready to start, please ask your question"
        self.cred = credential.Credential(
                                os.environ.get("TENCENTCLOUD_SECRET_ID"),
                                os.environ.get("TENCENTCLOUD_SECRET_KEY"))

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        self.stop_listening = None  # To store the stop function for listen_in_background

    def play_audio(self, data):
        self.stop_event.clear()  # Clear the stop event before starting playback
        self.stream = self.p.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=16000,
                                    output=True)
        self.is_playing = True

     # Playback loop with checks for stop event
        chunk_size = 1024
        for i in range(0, len(data), chunk_size):
            if self.stop_event.is_set():  # Check if stop_audio was called
                print("stop_event is set by stop_audio, breaking the loop to finalize playback")
                break
            self.stream.write(data[i:i + chunk_size])

        self._finalize_playback()

    def _finalize_playback(self):
        with self.playback_lock:
            if self.stream is not None:
                    self.stream.stop_stream()
                    print("Stream stopped in _finalize_playback")
                    self.stream.close()
                    print("Stream closed in _finalize_playback")
                    self.stream = None
                    print("Stream is set to None in _finalize_playback")
            self.is_playing = False

    def stop_audio(self):
        if self.is_playing is True:
            print("Stopping audio playback")
            self.stop_event.set()  # Signal to stop playback immediately
            time.sleep(0.1)  # Wait for the playback loop to break

            print("stop_event is set in stop_audio")
            with self.playback_lock:
                if self.stream is not None:
                    print("Stream is not None in stop_audio")
                    print("Start to stop stream due to stream is not None in stop_audio")
                    self.stream.stop_stream()
                    print("Stream stopped in in stop_audio")
                    self.stream.close()
                    print("Stream closed in in stop_audio")
                    self.stream = None
                    print("Stream is set to None in in stop_audio")
                self.is_playing = False
                print("Stop successfully")

    def recognize_user_input(self, recognizer, audio):
        try:
            print("Start recognizing user input by sensorvoice model")
            user_input = asr.asr_sensevoice(audio)
            #print("Start recognizing user input by whisper model")
            #user_input = recognizer.recognize_whisper(audio, model="small", language="english")
            if user_input and user_input.strip():
                print(f"User said: {user_input}")

                # Stop the current playback
                self.stop_audio()

                # Generate TTS data based on `user_input` by calling Hunyuan for answer

                resp = llm_rt.answer(self.cred, prompt=user_input)

                # audio_data = tts1.handle_tts( credential.Credential(
                #                 os.environ.get("TENCENTCLOUD_SECRET_ID"),
                #                 os.environ.get("TENCENTCLOUD_SECRET_KEY")),
                #                 '这是一段测试音频，旨在测试tts能正常工作,请忽略这段音频,谢谢,Ensure that you manage the shared audio resources (like stopping and starting playback) safely using locks or other synchronization mechanisms to avoid race conditions.Ensure that you manage the shared audio resources (like stopping and starting playback) safely using locks or other synchronization mechanisms to avoid race conditions'
                #                 )
                
                # Only play the first 100 characters of the response
                # due to the limitation of tencent cloud tts
                audio_data = tts_rt.handle_tts( self.cred, resp[0:100] ) 

                # Play the new response
                self.start_playback(audio_data)

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Error with recognition service; {e}")

    def listen_for_interrupt(self):
        self.stop_listening = self.recognizer.listen_in_background(self.microphone, self.recognize_user_input, phrase_time_limit=3)

    def start_playback(self, data):
        if self.playback_thread and self.playback_thread.is_alive():
            self.stop_audio()
            self.playback_thread.join()

        self.playback_thread = threading.Thread(target=self.play_audio, args=(data,))
        self.playback_thread.start()

    def start_chatbot(self):

        # Start the chatbot by playing a greeting message        
        audio_data = tts_rt.handle_tts( self.cred, self.greeting )
        self.start_playback(audio_data)

        # Start listening for user input in the background
        self.listen_for_interrupt()

        # user can press 'q' to exit the program
        while True:
            if input() == 'q':
                break        
        self.close()

    def close(self):
        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)  # Stop listening in background
        self.stop_audio()  # Stop any ongoing playback
        self.p.terminate()  # Terminate PyAudio when done with the chatbot

if __name__ == "__main__":
    chatbot = Chatbot()
    chatbot.start_chatbot()