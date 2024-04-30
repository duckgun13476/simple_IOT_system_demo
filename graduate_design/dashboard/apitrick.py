from openai import OpenAI

client = OpenAI(
  base_url="https://api.gptsapi.net/v1",
  api_key="sk-kOw1abedb5be8075cee41d5ec006ec58561d7debd0dBctS5"
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
    {"role": "system", "content": "你是一个助理,善于编码和分析问题，使用中文和markdown进行回答"},
    {"role": "user", "content": "你好，请生成一段代码，使用python，打印liuxinlong来了"}
  ]
)

print(completion.choices[0].message)