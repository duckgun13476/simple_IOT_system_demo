from openai import OpenAI
from dashboard.variables.variable import Var


def get_report(word, model_set="gpt-3.5-turbo-0125"):
    client = OpenAI(
        base_url=Var.API_url,
        api_key=Var.API_key
    )

    completion = client.chat.completions.create(
        model=model_set,
        messages=[
            {"role": "system", "content": "你是一个助理,善于对数据进行分析评估，使用中文和markdown"
                                          "进行回答，分析内容简短精炼，每次回答都遗忘上次对话内容，不要重"
                                          "复数据，只在数据存在问题时说出数据问题"},
            {"role": "user", "content": word}
        ]
    )
    return completion.choices[0].message.content, completion.usage.total_tokens

# word = "卧室温度24度，厨房温度58度，客厅温度35度，请对此进行评估"

# response_1 = get_report(word)
# print(response_1)
