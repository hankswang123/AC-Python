import threading
import time
import pyaudio
import pygame
import speech_recognition as sr

# -*- coding: utf-8 -*-
import os
import json

from tencentcloud.common import credential
import asr as asr
import RTL.tts_rt as tts_rt
import RTL.llm_chataudio as llm_ca
import RTL.llm_zhipu as llm_zp

# During News playing, user can speak to ask questions of the news played
class Chataudio:

    def __init__(self, mp3_file):
        self.p = pyaudio.PyAudio()
        self.stream = None

        self.is_playing = False
        self.stop_event = threading.Event()  # Event to signal stopping
        self.playback_thread = None
        self.playback_lock = threading.Lock()

        self.greetings = "Chat audio is ready to start, you can ask question during news is playing"
        self.cred = credential.Credential(
                                os.environ.get("TENCENTCLOUD_SECRET_ID"),
                                os.environ.get("TENCENTCLOUD_SECRET_KEY"))

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # To store the stop function for listen_in_background
        self.stop_listening = None  

        # Initialize the pygame mixer for playing mp3 files
        pygame.mixer.init()
        self.mp3 = mp3_file
        self.current_position = None
        self.new_position = None

        self.first_time = True
        self.index = -1
      

# Play the audio file, e.g. mp3/wav news file
    def play_mp3(self):

        # Load the MP3 file
        pygame.mixer.music.load(self.mp3)  
                
        # Play the MP3 file
        pygame.mixer.music.play()
        
        # Keep the script running until the music stops
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def pause_mp3(self):
        print("Pause mp3 playing")
        self.current_position = pygame.mixer.music.get_pos()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def continue_mp3(self):
        if self.new_position is None:
            self.new_position = self.current_position / 1000

        print(f"Continue mp3 playing at {self.new_position} seconds")
        pygame.mixer.music.set_pos(self.new_position)   
        pygame.mixer.music.unpause()


    def play_audio(self, data):
        # Clear the stop event before starting playback
        self.stop_event.clear()  
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

        # Continue to play mp3 if LLM's reply are speak out  
        # without any interupts by more questions (no break in above for statement)
        # current_position is 'not None' means the mp3 is playing
        if not self.stop_event.is_set() and self.current_position is not None:
            self.continue_mp3()


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

        # Pause news playing for replying user questions
        self.pause_mp3()

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

#        pygame.mixer.music.pause()

        try:
            #print("Start recognizing user input by sensorvoice model")
            user_input = asr.asr_sensevoice(audio)
            #print("Start recognizing user input by whisper model")
            #user_input = recognizer.recognize_whisper(audio, model="small", language="english")
#            if user_input and user_input.strip() and len(user_input) > 1 and self.first_time:
            #if user_input and user_input.strip() and len(user_input) > 1:
            if user_input and user_input.strip() and len(user_input) > 1:
                #print(f"User said: {user_input}")
#                self.first_time = False
                # Stop the current playback(last LLM answer + transition) 
                # and also pause the news if it is in playing status

                # if "repeat" not in user_input and "main idea" not in user_input and "important" not in user_input:
                #     pygame.mixer.music.unpause()
                #     return

                self.stop_audio()

                # Generate TTS data based on `user_input` by calling Hunyuan for answer     
#                user_input = "The main points of the news?"    
                self.index = self.index + 1
                resp = llm_ca.answer(self.cred, user_input, self.current_position, index=self.index)
                #resp = llm_ca.answer(self.cred, user_input, self.current_position)
                #user_input = "The main points of the news?"
#                user_input = "Please repeat the previous sentence slowly, I have not heared the voice clearly"
                #resp = llm_zp.answer(self.cred, user_input, self.current_position)
                # JSON Format of reply from LLM is like following
                # {
                #     "Response": {
                #         "Action": "continue",
                #         "New_position": "27300",
                #         "Answer": "You're welcome! Let me know if you have any other questions.",
                #         "Transition": "If no other questions, I will continue playing the news."
                #     }
                # }  

                # Record new position suggested by LLM
                # Convert to seconds due to ms is returned
                resp_json = json.loads(resp)
                self.new_position = float(resp_json["Response"]["New_position"]) / 1000
                
                # Convert above json string to python dictionary object 
                audio_answer_transition = tts_rt.handle_tts( self.cred, resp_json["Response"]["Answer"]+
                                                            ' '+
                                                            resp_json["Response"]["Transition"] ) 

                # Play LLM answer + transition phrase,  
                # Resume the news at new_position if no more questions
                self.start_playback(audio_answer_transition)

                # no more questions from user, play the transition phrase
                # e.g. 'if there are no more questions, I will continue to play news'
                # audio_data = tts_rt.handle_tts( self.cred, resp[transition_phrase] ) 
                # self.play_audio(audio_data)

                # Continue to play news
                # new position depends on user's question
                # e.g. if user asked: 'Please repeat the last sentence slowly, I have not heared the voice clearly'
                # the new postion should be set as the last sentence start position
                # e.g. if user asked: 'What is the main points of the news?'
                # position no need to change after LLM answer is played
                # pygame.mixer.music.set_pos(float(resp_json["Response"]["Seek"]))
                # pygame.mixer.music.pause()

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Error with recognition service; {e}")

    # Listen for user input in the background
    # The recognizer will call back 'recognize_user_input' when it hears a user
    # The recognizer will listen for 3 seconds at a time
    # The recognizer will stop listening when the stop_listening function is called
    def listen_for_interrupt(self):
        self.stop_listening = self.recognizer.listen_in_background(self.microphone, self.recognize_user_input, phrase_time_limit=1)

    def start_playback(self, data):
        if self.playback_thread and self.playback_thread.is_alive():
            self.stop_audio()
            self.playback_thread.join()

        self.playback_thread = threading.Thread(target=self.play_audio, args=(data,))
        self.playback_thread.start()

    def greeting(self):
        # Start the chatbot by playing a greeting message        
        audio_data = tts_rt.handle_tts( self.cred, self.greetings )
        self.play_audio(audio_data)        

    def start_chataudio(self):

        # Start the chataudio by playing a greeting message
        #self.greeting()

        # Start listening for user input in the background
        # The recognizer will call back 'recognize_user_input' when it hears a user
        self.listen_for_interrupt()

        # Play audio of news/song/a meeting record...
        self.play_mp3()

        # user can press 'q' to exit the program
        while True:
            if input() == 'q':
                break        
        self.close()

    def close(self):
        if self.stop_listening:
            # Stop listening in background
            self.stop_listening(wait_for_stop=False)  
        # Stop any ongoing playback
        self.stop_audio()  
        # Terminate PyAudio when done with the chatbot
        self.p.terminate()

        # Stop audio of news/song/a meeting record...
        pygame.mixer.music.stop()

if __name__ == "__main__":
    chataudio = Chataudio("sap_news_jack.wav")
    chataudio.start_chataudio()