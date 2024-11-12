import pygame
import openai

def pause_audio():
    pygame.mixer.music.pause()
    return pygame.mixer.music.get_pos() / 1000.0

def send_to_llm(transcript, current_position, user_question):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant for an audio player."},
            {
                "role": "user",
                "content": f"Here is the transcript of the audio with timecodes: {transcript}. "
                           f"The audio is currently paused at {current_position} seconds. "
                           f"The user asked: '{user_question}'. "
                           f"Please provide a response to the user, and also provide a transition sentence in your response, "
                           f"and suggest the next play position in seconds."
            },
        ]
    )
    return response.choices[0].message['content']

import pyttsx3

tts_engine = pyttsx3.init()

def play_tts(text):
    tts_engine.say(text)
    tts_engine.runAndWait()


import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_for_additional_questions(timeout=10):
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=timeout)
            user_input = recognizer.recognize_google(audio, language='zh-CN')
            return user_input
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

def handle_user_input(user_question):
    current_position = pause_audio()
    
    # 发送问题到LLM
    llm_response = send_to_llm(transcript, current_position, user_question)
    
    # 播放LLM的回答
    play_tts(llm_response['response'])
    
    # 实时监听用户是否有进一步提问
    while True:
        user_input = listen_for_additional_questions()
        if user_input:
            # 如果用户提出了新问题，重新处理该问题
            llm_response = send_to_llm(transcript, current_position, user_input)
            play_tts(llm_response['response'])
        else:
            # 用户没有进一步提问，播放过渡性句子并恢复音频
            play_tts(llm_response['transition_sentence'])
            next_position = llm_response['next_play_position']
            pygame.mixer.music.set_pos(next_position)
            pygame.mixer.music.unpause()
            break

