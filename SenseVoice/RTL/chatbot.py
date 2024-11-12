import threading
import pyaudio
import speech_recognition as sr

# -*- coding: utf-8 -*-
import os
import json

from tencentcloud.common import credential
#import asr as asr
import RTL.tts_rt as tts_rt
#import llm as llm

# Overview:
# This is the chatbot class that will be used to interact with the user
# User can interupt the chatbot by speaking to it at any time, 
# But the chatbot will not stop the current playback if user speaks are detected
# Until the current playback is finished, the chatbot can play the new response
class Chatbot:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.playback_lock = threading.Lock()

        self.is_playing = False
        self.playback_thread = None

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        self.stop_listening = None  # To store the stop function for listen_in_background

    def play_audio(self, data):
        with self.playback_lock:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()

            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=16000,
                                      output=True)
            self.is_playing = True
            self.stream.write(data)
            self.is_playing = False

    def stop_audio(self):
        print("Stopping audio before playback_lock")
        with self.playback_lock:
            print("Stopping audio begin")
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                print("Audio stopped successfully")

            self.is_playing = False

    def recognize_user_input(self, recognizer, audio):
        try:
            # user_input = asr.asr_sensevoice(audio)
            # print(f"User said: {user_input}")
            print("User input detected")
            # Stop the current playback
            self.stop_audio()

            # Generate TTS data based on `user_input`
#            fake_response_audio_data = b'\x00\x01' * 4000  # Replace with actual TTS data
#            fake_rate = 16000

            audio_data = tts_rt.handle_tts( credential.Credential(
                            os.environ.get("TENCENTCLOUD_SECRET_ID"),
                            os.environ.get("TENCENTCLOUD_SECRET_KEY")),
                            '这是一段测试音频，旨在测试tts能正常工作,请忽略这段音频,谢谢,Ensure that you manage the shared audio resources (like stopping and starting playback) safely using locks or other synchronization mechanisms to avoid race conditions.Ensure that you manage the shared audio resources (like stopping and starting playback) safely using locks or other synchronization mechanisms to avoid race conditions'
                            )

            # Play the new response
            #self.play_audio(audio_data)
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

        # Start listening for user input in the background
        self.listen_for_interrupt()

        audio_data = tts_rt.handle_tts( credential.Credential(
                        os.environ.get("TENCENTCLOUD_SECRET_ID"),
                        os.environ.get("TENCENTCLOUD_SECRET_KEY")),
                        '测试开始了，这是一段测试音频。cease all audio playback and start the chatbot.'
                        )
#        self.play_audio(audio_data)
        self.start_playback(audio_data)

        # Keep the chatbot running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.close()

    def close(self):
        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)  # Stop listening in background
        self.stop_audio()  # Stop any ongoing playback
        self.p.terminate()  # Terminate PyAudio when done with the chatbot

if __name__ == "__main__":
    chatbot = Chatbot()
    chatbot.start_chatbot()