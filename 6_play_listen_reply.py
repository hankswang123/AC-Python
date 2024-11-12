# -*- coding: utf-8 -*-
import json
import os

import pygame
import time
import threading
import speech_recognition as sr

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
#from tencentcloud.tts.v20190823 import tts_client, models
#https://github.com/TencentCloud/tencentcloud-sdk-python/blob/master/tencentcloud/tts/v20190823/tts_client.py

#此文件演示了如何使用腾讯云的混元对话接口，这个文件可以执行成功

def answer(prompt):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
        cred = credential.Credential(
            os.environ.get("TENCENTCLOUD_SECRET_ID"),
            os.environ.get("TENCENTCLOUD_SECRET_KEY"))

        cpf = ClientProfile()
        # 预先建立连接可以降低访问延迟
        cpf.httpProfile.pre_conn_pool_size = 3
        client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", cpf)

        req = models.ChatCompletionsRequest()

        msg1 = models.Message()
        msg1.Role = "system"
    #    msg1.Content = "你是一个智能助手，将回答用户的问题"
        msg1.Content = """
        你是一个音频智能助手，你将基于下面音频的json内容回答收听者在收听过程中的问题。
        {
            "Scripts": {
                "00:01": May 22-26, the World Economic Forum’s Annual Meeting will take place in Davos-Klosters, Switzerland, under the theme of Working Together, Restoring Trust. 
                "00:11": Business leaders, international political leaders, economists, celebrities and journalists come together to discuss global issues such as climate change and broader social challenges with regards to a sustainable future.
                "00:23": SAP announced that the jobs at SAP Landing Page for refugees from Ukraine is live. 
                "00:30": To support refugees from Ukraine, SAP is rolling out a dedicated onboarding process for refugees who have arrived in Bulgaria, Czech Republic, Germany, Hungary, Poland, Romania and Slovakia. 
                "00:42": This includes buddy support with an existing Ukrainian employee, mental health support and dedicated learning and language courses, childcare options (in selected countries) and advanced payment options for new hires. 
                "00:54": SAP is also working to extend this to other countries.            
            }
        }

        回答过程中，请注意一下规则：
        1. 用户的问题之后会有以+号开始音频的播放位置信息，比如客户原始问题是：“没听清楚，请重复上一句话”，
        那么你收到的问题将会是：“没听清楚，请重复上一句话+00：29”，这个表示用户在收听到第29秒的时候
        向你提到了这个问题。你要在回答中给出新的位置信息。如果客户的问题不需要重新对音频下次播放位置重
        定位，则把这个位置返回。返回的位置信息，写在{Seek}中

        2. 针对客户问题生成的回答，写在{Answer}中. 针对音频操作类的问题，{Answer}为空。比如，“暂停播放”等，
        应该写空{}

        3. 回答内容要简洁明了。

        使用下面的格式生成回答。
        {
            "Response": {
                "Seek": "{Seek}"
                "Answer": "{Answer}"
            }
        }
        """

        msg2 = models.Message()
        msg2.Role = "user"
        msg2.Content = prompt
        req.Messages = [msg1, msg2]

        # hunyuan ChatStd/ChatPro 同时支持 stream 和非 stream 的情况
        req.Stream = True
    #    req.Model = 'hunyuan-lite'
        req.Model = 'hunyuan-pro'
        resp = client.ChatCompletions(req)

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

        print(full_content)

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
                answer("你好，奥运会中国金牌数")

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

# Create threads for playing music and listening for questions
music_thread = threading.Thread(target=play_mp3, args=(mp3_file,))
listen_thread = threading.Thread(target=listen_for_questions)

# Start the threads
listen_thread.start()
music_thread.start()

# Wait for the threads to complete
listen_thread.join()
music_thread.join()


