# -*- coding: utf-8 -*-
import json
import os
import base64
import wave
import pyaudio
from pyaudio import PyAudio, paInt16

import pygame
import time
import threading
import speech_recognition as sr

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models as hy_models
from tencentcloud.tts.v20190823 import tts_client, models as tts_models

import RTL.asr as svr

# 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
cred = credential.Credential(
       os.environ.get("TENCENTCLOUD_SECRET_ID"),
       os.environ.get("TENCENTCLOUD_SECRET_KEY"))

#Call Tencent TTS: Text To Speech service to speak out Hunyuan's reply
#这里最关键的是使用原音频的音色speak out回答，这样听起来更自然
#The key point here is to use the original audio's voice to speak out the reply, so it sounds more natural
#这里没有还没有使用原音频的音色，后续可以尝试使用复刻音色功能
def tts_play(audio_data):
    if audio_data:
        p = PyAudio()
        player = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
        player.write(audio_data)
        player.stop_stream()
        player.close()
        p.terminate()
        print("TTS调用成功：")
    else:
        print("Error: Decoded audio data is None")

#Call Tencent TTS: Text To Speech service to speak out Hunyuan's reply
#这里最关键的是使用原音频的音色speak out回答，这样听起来更自然
#播放TTS的音频时，需要在一个新的线程中运行，这样可以避免阻塞主线程，持续监听用户的问题
def handle_tts(cred, text):

    try:
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tts.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tts_client.TtsClient(cred, "ap-guangzhou", clientProfile)

        req = tts_models.TextToVoiceRequest()
        params = {
            "Text": text,
            "SessionId": "test_session_id",
            "Volume": 0,
            "Speed": 0,      
            "ProjectId": 0,
            "ModelType": 1,                   
            "VoiceType": 101002,            
            "PrimaryLanguage": 1,
            "SampleRate": 16000,
            "Codec": "wav",
            "SegmentRate": 0,
            "EmotionCategory": "neutral",
            "EmotionIntensity": 100
        }

        params_json = json.dumps(params)
        req.from_json_string(params_json)

        start_time = time.time()  # Record start time
        resp = client.TextToVoice(req)
        end_time = time.time()  # Record end time
        time_consumed = end_time - start_time  # Calculate time consumed
        print(f"Time consumed for tencent TTS: {time_consumed:.2f} seconds")        

        if resp.Audio:
            try:
                audio_data = base64.b64decode(resp.Audio)
            except Exception as e:
                print(f"Error decoding audio data: {e}")
                audio_data = None

            if audio_data:
                # Run the audio playback in a separate thread
                audio_thread = threading.Thread(target=tts_play, args=(audio_data,))
                audio_thread.start()
            else:
                print("Error: Decoded audio data is None")
        else:
            print("TTS调用失败")

    except Exception as e:
        print(e)     

#Call LLM: Hunyuan to answer questions from user
#这里有如下问题要解决：
#1. 如何让大模型找到原音频新的seek位置，比如用户说“没听清楚，请重复上一句话”，那么大模型需要找到上一句话的位置
#2. 如何让大模型生成回答，比如用户问了一个知识性问题，大模型需要生成回答
def answer(cred, prompt):
    try:
        cpf = ClientProfile()
        # 预先建立连接可以降低访问延迟
        cpf.httpProfile.pre_conn_pool_size = 3
        client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", cpf)
        #v20230901.
        req = hy_models.ChatCompletionsRequest()

        msg1 = hy_models.Message()
        msg1.Role = "system"
        msg1.Content = """
        你是一个音频智能助手，你将基于下面音频的json内容回答收听者在收听过程中的问题。"1.0"表示第一秒的位置开始播放的句子
        {
            "Scripts": {
                "1.0": May 22-26, the World Economic Forum’s Annual Meeting will take place in Davos-Klosters, Switzerland, under the theme of Working Together, Restoring Trust. 
                "11.0": Business leaders, international political leaders, economists, celebrities and journalists come together to discuss global issues such as climate change and broader social challenges with regards to a sustainable future.
                "23.0": SAP announced that the jobs at SAP Landing Page for refugees from Ukraine is live. 
                "30.0": To support refugees from Ukraine, SAP is rolling out a dedicated onboarding process for refugees who have arrived in Bulgaria, Czech Republic, Germany, Hungary, Poland, Romania and Slovakia. 
                "42.0": This includes buddy support with an existing Ukrainian employee, mental health support and dedicated learning and language courses, childcare options (in selected countries) and advanced payment options for new hires. 
                "54.0": SAP is also working to extend this to other countries.            
            }
        }

        回答过程中，请注意一下规则：
        1. 用户的问题之后会有以+号开始音频的播放位置信息，比如客户在第29秒问了问题：“没听清楚，请重复上一句话”，
        那么你收到的问题将会是：“没听清楚，请重复上一句话+29.0”。你要在回答中给出新的位置信息。如果客户的问题不需要
        对音频下次播放位置重定位，则把接收到的seek信息原路返回。返回的位置信息写在{Seek}中。

        2. 针对客户问题生成的回答，写在{Answer}中. 针对音频操作类的问题，{Answer}为空。比如，“暂停播放”
        "重复播放上一句"等音频操作类的命令，你不需要生成内容，只要返回seek信息即可。

        3. 如果客户的问题总结或是知识性问答，seek信息只需要原路返回即可，不需要生成新的seek信息，即为{}。
        你生成的回答内容写在{Answer}中。

        4. 回答内容要简洁明了。

        使用下面的格式生成回答。
        {
            "Response": {
                "Seek": "{Seek}"
                "Answer": "{Answer}"
            }
        }
        """

        msg2 = hy_models.Message()
        msg2.Role = "user"
        msg2.Content = prompt
        req.Messages = [msg1, msg2]

        # hunyuan ChatStd/ChatPro 同时支持 stream 和非 stream 的情况
        req.Stream = True
    #    req.Model = 'hunyuan-lite'
        req.Model = 'hunyuan-pro'

        start_time = time.time()  # Record start time
        resp = client.ChatCompletions(req)
        end_time = time.time()  # Record end time
        time_consumed = end_time - start_time  # Calculate time consumed
        print(f"Time consumed for hunyuan reply: {time_consumed:.2f} seconds")        

        full_content = ""
        if req.Stream:  # stream 示例
            for event in resp:
    #            print(event["data"])
                data = json.loads(event['data'])
                for choice in data['Choices']:
                    full_content += choice['Delta']['Content']
        else:  # 非 stream 示例
            # 通过 Stream=False 参数来指定非 stream 协议, 一次性拿到结果
            full_content = resp.Choices[0].Message.Content

#        print(full_content)

        return full_content

    except TencentCloudSDKException as err:
        print(err)

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

# ASR: Automatic Speech Recognition
# Here we use the Whisper model from OpenAI to recognize the speech
def asr_whisper(recognizer, audio):
    
    start_time = time.time()  # Record start time
    
    speech_text = recognizer.recognize_whisper(audio, model="base", language="chinese")
    print(f"User said: {speech_text}")

    end_time = time.time()  # Record end time
    time_consumed = end_time - start_time  # Calculate time consumed

    print(f"Time consumed for whisper ASR: {time_consumed:.2f} seconds")    
    return speech_text

# Main loop for listening for questions
# The loop listens for questions and pauses the music when a question is detected
# The loop resumes the music when the question is answered
def audio_callback(recognizer, audio):

    print("Listening for questions...")

    try:
        speech_text = svr.asr_sensevoice(audio)
        if speech_text:

            #Question detected! Pause the music
            pygame.mixer.music.pause()
            position = pygame.mixer.music.get_pos() / 1000
            print(f"Playback paused at position: {position} seconds due to voice detected")

            #for debug purpose
            speech_text = "the main content of the audio file" 

            #Call Hunyuan to answer the question
            resp = answer(cred, 
                            prompt=speech_text+"+"+str(position))

            #Speak out the answer
            resp_json = json.loads(resp)
            tts_play(cred, text=resp_json["Response"]["Answer"])

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

recognizer = sr.Recognizer()
microphone = sr.Microphone()
with microphone as source:
    recognizer.adjust_for_ambient_noise(source)

# Start the background listening thread
stop_listening = recognizer.listen_in_background(microphone, audio_callback, phrase_time_limit=8)

# Main loop for playing the music
play_mp3("sap_news.mp3")

while True:
    if input() == 'q':
        break

stop_listening(wait_for_stop=False)