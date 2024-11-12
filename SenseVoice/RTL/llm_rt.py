# -*- coding: utf-8 -*-
import json
import time
import os

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models as hy_models

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
        你是一个智能对话助手，回答用户提出的问题。不知道的直接说不知道就可以了。
        """
        msg2 = hy_models.Message()
        msg2.Role = "user"
        msg2.Content = prompt
        req.Messages = [msg1, msg2]

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

    resp = answer( credential.Credential(
                    os.environ.get("TENCENTCLOUD_SECRET_ID"),
                    os.environ.get("TENCENTCLOUD_SECRET_KEY")),
                    'the main content of the audio+0.234'
#                    '我对太阳系的行星非常感兴趣，特别是火星。请使用10句话提供关于它的基本信息，包括其大小、组成、环系统和任何独特的天文现象。'
                    )

    resp_json = json.loads(resp)    
    print(resp_json["Response"]["Answer"])