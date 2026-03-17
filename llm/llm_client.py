"""
通用LLM客户端 - 支持多个服务商的API封装
"""
import os
from typing import Dict, List, Optional

import requests

from config import api_manager


class LLMClient:
    """通用LLM客户端"""

    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or api_manager.get_provider()
        self.model = model or api_manager.get_model()
        self.api_key = api_manager.get_api_key(self.provider)
        self.temperature = 0.7
        self.max_tokens = 4000

    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            回复内容
        """
        if self.provider == "openai":
            return self._chat_openai(messages, **kwargs)
        elif self.provider == "anthropic":
            return self._chat_anthropic(messages, **kwargs)
        elif self.provider == "qwen":
            return self._chat_qwen(messages, **kwargs)
        elif self.provider == "minimax":
            return self._chat_minimax(messages, **kwargs)
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")

    def _chat_openai(self, messages: List[Dict], **kwargs) -> str:
        """OpenAI API调用"""
        import openai
        openai.api_key = self.api_key

        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        return response.choices[0].message.content

    def _chat_anthropic(self, messages: List[Dict], **kwargs) -> str:
        """Anthropic Claude API调用"""
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)

        # 转换消息格式
        system = ""
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                claude_messages.append(msg)

        response = client.messages.create(
            model=self.model,
            system=system,
            messages=claude_messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        return response.content[0].text

    def _chat_qwen(self, messages: List[Dict], **kwargs) -> str:
        """阿里Qwen API调用"""
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _chat_minimax(self, messages: List[Dict], **kwargs) -> str:
        """MiniMax API调用"""
        url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # MiniMax需要特殊的消息格式
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def create_client(provider: str = None, model: str = None) -> LLMClient:
    """创建LLM客户端的便捷函数"""
    return LLMClient(provider=provider, model=model)
