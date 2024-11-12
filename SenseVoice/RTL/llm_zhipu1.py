import time
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="3d3d338f8054692163a5fca6fb168a73.XmitPSN4OFYN5mVs") # Please fill in your own APIKey
# response = client.chat.completions.create(
#   model="glm-4",  # Fill in the model name to be called
#     messages=[
#       {"role": "user", "content": "Hello! What is your name"},
#     ],
#     stream=False,
#     )
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

start_time = time.time()  # Record start time
 
response = client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型编码
            messages=[
                {"role": "system", "content": "你是一个天文学专家，将回答用户关于太阳系的问题，如果提问了其他问题，将不予回答。"},
                {"role": "user", "content": "上海的经济发展如何？"},
            ],
            stream=False, )

end_time = time.time()  # Record end time
time_consumed = end_time - start_time  # Calculate time consumed
print(f"Time consumed for zhipu reply: {time_consumed:.2f} seconds\n")  

print(response.choices[0].message.content)

# second call
print("Second API call, to get more information about Mars, will system prompt be repeated? \n")
response = client.chat.completions.create(
                model="glm-4",  # 填写需要调用的模型编码
                messages=[
                    {"role": "user", "content": "上海的经济发展如何？"},
                ],
                stream=False, )

print(response.choices[0].message)
# for chunk in response:
#     print(chunk.choices[0].delta)