import time
from zhipuai import ZhipuAI

import llm_transcript

#import RTL.llm_transcript as llm_transcript
import llm_transcript

def prepare_msg(user_question, current_position):

    return [
            {"role": "system", "content": "You are an assistant for an audio player."}, 
            {"role": "user", "content": llm_transcript.prepare_prompt(user_question, current_position)}            
            ]

def answer(cred, user_question, current_position):

    client = ZhipuAI(api_key="3d3d338f8054692163a5fca6fb168a73.XmitPSN4OFYN5mVs") 

    start_time = time.time()  # Record start time

    response = client.chat.completions.create(
            model="glm-4-flash",  # Fill in the model name to be called
            messages=prepare_msg(user_question=user_question, current_position=current_position),
            stream=False,
        )

    end_time = time.time()  # Record end time
    time_consumed = end_time - start_time  # Calculate time consumed
    print(f"Time consumed for __zhipuAI__ reply: {time_consumed:.2f} seconds\n")  

    print(response.choices[0].message.content)   

    return response.choices[0].message.content

# for chunk in response:
#     print(chunk.choices[0].delta)

# response = client.chat.completions.create(
#   model="glm-4",  # Fill in the model name to be called
#   messages=[
#       {"role": "user", "content": "As a marketing expert, please create an attractive slogan for my product"},
#       {"role": "assistant", "content": "Of course, to create an attractive slogan, please tell me some information about your product"},
#       {"role": "user", "content": "ZhipuAI Open Platform"},
#       {"role": "assistant", "content": "Empowering the future, mapping infinity - ZhipuAI, making innovation accessible!"},
#       {"role": "user", "content": "Create a more accurate and attractive slogan"}
#   ],
# )
# print(response.choices[0].message.content)

# tools = [
# {
#     "type": "function",
#     "function": {
#         "name": "query_train_info",
#         "description": "Query the train times according to the information provided by the user",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "departure": {
#                     "type": "string",
#                     "description": "Departure city or station",
#                 },
#                 "destination": {
#                     "type": "string",
#                     "description": "Destination city or station",
#                 },
#                 "date": {


#                     "type": "string",
#                     "description": "Date of the train to query",
#                 },
#             },
#             "required": ["departure", "destination", "date"],
#         },
#     }
# }
# ]

# messages = [
#     {
#         "role": "user",
#         "content": "Can you help me check the train tickets from Beijing South Station to Shanghai on January 1, 2024?"
#     }
# ]

# response = client.chat.completions.create(
#     model="glm-4", #Fill in the model code that needs to be called.
#     messages=messages,
#     tools=tools,
#     tool_choice="auto",
# )
# print(response.choices[0].message)

# start_time = time.time()  # Record start time
 
# response = client.chat.completions.create(
# model="glm-4",  # 填写需要调用的模型编码
# messages=[
#     {"role": "system", "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"},
#     {"role": "user", "content": "我对太阳系的行星非常感兴趣，特别是火星。请使用10句话提供关于它的基本信息，包括其大小、组成、环系统和任何独特的天文现象。"},
# ],
# stream=False,
# )

# end_time = time.time()  # Record end time
# time_consumed = end_time - start_time  # Calculate time consumed
# print(f"Time consumed for zhipu reply: {time_consumed:.2f} seconds\n")  

# print(response.choices[0].message.content)

# for chunk in response:
#     print(chunk.choices[0].delta)