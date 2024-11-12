# from gradio_client import Client

# client = Client("https://s5k.cn/api/v1/studio/iic/CosyVoice-300M/gradio/")
# result = client.predict(
# 		api_name="/random_seed"
# )
# print(result)

from gradio_client import Client

client = Client("https://s5k.cn/api/v1/studio/iic/CosyVoice-300M/gradio/")
result = client.predict(
		_sound_radio="中文女",
		_synthetic_input_textbox="SAP announced that the jobs at SAP",
		_seed=0,
		api_name="/generate_audio"
)
print(result)