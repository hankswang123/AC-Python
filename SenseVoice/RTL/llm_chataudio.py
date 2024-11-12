# -*- coding: utf-8 -*-
import json
import time
import os

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models as hy_models

#import RTL.llm_transcript as llm_transcript
import llm_transcript

def prepare_msg(user_question, current_position):

    msg1 = hy_models.Message()
    msg1.Role = "system"
    msg1.Content = """
    You are an assistant for an audio player.
    """

    msg2 = hy_models.Message()
    msg2.Role = "user"
    msg2.Content = llm_transcript.prepare_prompt(user_question, current_position)

#    print(msg2.Content)

    return [msg1, msg2]

#Call LLM: Hunyuan to answer questions from user
#这里有如下问题要解决：
#1. 如何让大模型找到原音频新的seek位置，比如用户说“没听清楚，请重复上一句话”，那么大模型需要找到上一句话的位置
#2. 如何让大模型生成回答，比如用户问了一个知识性问题，大模型需要生成回答
def answer(cred, user_question, current_position, index = 1000):

    #demo code start
    # demo_answers = {
    #     "What is the main idea of this audio?": "The main idea of this audio is to discuss the importance of restoring trust in the business community.",
    #     "Could you summarize the main idea of this audio?": "The audio summarizes the significance of rebuilding trust within the business sector.",
    #     "Why is it important to restoring trust in business community based on the audio?": "Restoring trust in the business community is crucial for fostering a healthy economic environment and ensuring sustainable growth.",
    #     "What is Newton's laws?": "Newton's laws are three fundamental principles that describe the relationship between the motion of an object and the forces acting on it.",
    #     "I did not hear clearly, please repeat the last sentence": "Sure, the last sentence was about the importance of trust in business relationships.",
    #     "Yes, please": "Certainly! How can I assist you further?"
    # }

    demo_answers = [
                {
                        "Response": {
                            "Question": "Please repeat the last sentence",
                            "Current_position": f"{current_position}",
                            "Action": "",
                            "New_position": f"{current_position}",
                            "Answer": "Sure, the last sentence was about May 22-26, the World Economic Forum’s Annual Meeting will take place in Davos-Klosters, Switzerland, ",
                            "Transition": "If you have any further questions, feel free to ask."
                        }
                    },        
                {
                        "Response": {
                            "Question": "What is the main idea of this audio?",
                            "Current_position": f"{current_position}",
                            "Action": "",
                            "New_position": f"{current_position}",
                            "Answer": "The main idea of this audio is to discuss the importance of restoring trust in the business community.",
                            "Transition": "If no other questions, I will continue playing the news."
                        }
                    },
                {
                        "Response": {
                            "Question": "Why is it important to restoring trust in business community based on the audio?",
                            "Current_position": f"{current_position}",
                            "Action": "",
                            "New_position": f"{current_position}",
                            "Answer": "Restoring trust in the business community is crucial for fostering a healthy economic environment and ensuring sustainable growth.",
                            "Transition": "If you have any further questions, feel free to ask."
                        }
                    }

    ]

    if index < len(demo_answers) and index >= 0:
        return json.dumps(demo_answers[index])

    #demo code end
    
    try:
        cpf = ClientProfile()
        # 预先建立连接可以降低访问延迟
        cpf.httpProfile.pre_conn_pool_size = 3
        client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", cpf)
        #v20230901.
        req = hy_models.ChatCompletionsRequest()

        req.Messages = prepare_msg(user_question, current_position)

        # hunyuan ChatStd/ChatPro 同时支持 stream 和非 stream 的情况
        req.Stream = True
        req.Model = 'hunyuan-lite'
    #    req.Model = 'hunyuan-pro'

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

# for debug purpose
if __name__ == "__main__":

#    print(prompt_template)

    resp = answer( credential.Credential(
                    os.environ.get("TENCENTCLOUD_SECRET_ID"),
                    os.environ.get("TENCENTCLOUD_SECRET_KEY")),
                    #'What is the main idea of this audio?',
                    #'Could you summarize the main idea of this audio?',
                    'Why is it important to restoring trust in business community based on the audio?',
                    #'what is Newton laws?',
                    #'I did not hear clearly, please repeat the last sentence',
                    #'Yes, please',
                    27300
                    )

    resp_json = json.loads(resp)    
    print(resp_json["Response"]["Answer"])