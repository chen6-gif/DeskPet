import requests

class LLMService:
    """大语言模型服务"""

    def __init__(self):
        self.api_key = "sk-29S0hsJ3DEsJKQmVvHN7RyMA5bRChhhGXbmp93rl5lVxkViS"
        self.base_url = "https://api.hunyuan.cloud.tencent.com"
        self.model = "hunyuan-turbos-latest"
        self.history = []

    def set_config(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def chat(self, message: str) -> str:
        if not self.api_key:
            return "请先配置 API Key"

        if not self.base_url:
             return "请先在设置中配置 API URL"

        self.history.append({"role": "user", "content": message})

        try:
            url = f"{self.base_url}/v1/chat/completions"

            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": self.history
                },
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            return reply

        except Exception as e:
            error_msg = str(e)
            if "Bearer" in error_msg or "key" in error_msg.lower():
                return "API 请求失败，请检查配置"
            return f"请求失败，请检查网络或配置"

    def clear_history(self):
        self.history = []