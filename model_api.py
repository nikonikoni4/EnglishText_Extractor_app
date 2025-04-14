import configparser
import requests
import json


def call_deepseek_api(prompt, api_key,max_tokens=300, model="deepseek-chat", temperature=0.5):
    """
    调用DeepSeek API接口
    :param prompt: 输入的提示文本
    :param api_key: API密钥
    :param model: 使用的模型，默认为deepseek-v3
    :param temperature: 生成文本的随机性，默认为0.7
    :return: API返回的响应内容
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens  # 新增：设置更大的token限制
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API请求失败，状态码：{response.status_code}，错误信息：{response.text}")

def get_prompt(word, sentence="", config=None):
    if config is None:
        config = {}
  
    # 从配置中获取prompt模板，如果不存在则使用默认值
    prompt_template = config["prompt"]["default"]
    # 使用format方法替换占位符
   
    return prompt_template.format(word=word, sentence=sentence)

def ask_model(api_key, word, sentence="", config=None):
    # 从配置中获取prompt
    
    prompt = get_prompt(word,sentence,config)  # 替换为你的提示文本
   
    try:
        response = call_deepseek_api(prompt, api_key)
       
        content = response["choices"][0]["message"]["content"]
        
        # 去除Markdown代码块
        if content.startswith('```json'):
            content = content[content.find('{'):content.rfind('}')+1]
        
        # 解析JSON
        data = json.loads(content)
        print("API返回内容：")
        print(data)
        return data
    except Exception as e:
        print(f"调用API失败: {str(e)}")
        return None   
def load_config(config_path='config.ini'):
        """读取配置文件并返回配置对象"""
        config = configparser.ConfigParser()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config.read_file(f)
            return config
        except Exception as e:
            print(f"读取配置文件失败: {str(e)}")
            return configparser.ConfigParser()  # 返回空配置对象

if __name__ == "__main__":
    # 从环境变量获取API密钥更安全
    api_key = ""  # 替换为你的API密钥
    
    config = load_config()
    ask_model(api_key, "apple", config=config)
