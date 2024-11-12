import json
import os

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
#混元接口说明
#https://cloud.tencent.com/document/api/1729/105701?cps_key=1d358d18a7a17b4a6df8d67a62fd3d3d

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
        msg1.Content = "你是一个智能助手，将回答用户的问题"

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

answer("你好，奥运会中国金牌数")
