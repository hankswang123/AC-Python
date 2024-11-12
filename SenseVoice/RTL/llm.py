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

# for debug purpose
if __name__ == "__main__":

    resp = answer( credential.Credential(
                    os.environ.get("TENCENTCLOUD_SECRET_ID"),
                    os.environ.get("TENCENTCLOUD_SECRET_KEY")),
                    'the main content of the audio+0.234'
                    )

    resp_json = json.loads(resp)    
    print(resp_json["Response"]["Answer"])