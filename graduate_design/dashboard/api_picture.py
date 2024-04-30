import base64
import requests
import json
from dashboard.variables.variable import Var

url = Var.API_url
api = Var.API_key


# vision-preview
def picture_api_analy(prompt_12, model_use="gpt-4-turbo", path="fixed_snapshot.jpg"):
    # OpenAI API Key
    api_key = api

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Path to your image
    image_path = (path)

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model_use,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_12
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100
    }

    response = requests.post(url + "/chat/completions", headers=headers, json=payload)

    print(response.text)
    response_zi = json.loads(response.text)
    total_tokens = response_zi['usage']['total_tokens']
    content = response_zi['choices'][0]['message']['content']
    return content, total_tokens

# prompt_11 = "图片中有什么物体，是否有火焰，是否有不安全的物品，是否有生物活动，使用中文并简短回答"
# content, total_tokens = picture_api_analy(prompt_11,path="unlabeled_image.jpg")
# print(content, total_tokens)
