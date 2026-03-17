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
        """MiniMax API调用 - 使用Anthropic兼容格式"""
        import streamlit as st

        # 从widget获取密钥
        api_key = st.session_state.get("minimax_api_key_input", "")

        if not api_key:
            raise ValueError("请在侧边栏配置MiniMax的API密钥")

        # MiniMax Anthropic兼容API
        url = "https://api.minimaxi.com/anthropic/v1/messages"

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # 分离system消息
        system_content = ""
        minimax_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                # 转换为Anthropic格式
                minimax_messages.append({
                    "role": msg["role"],
                    "content": [{"type": "text", "text": msg["content"]}]
                })

        data = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "system": system_content,
            "messages": minimax_messages,
        }

        print(f"MiniMax request - URL: {url}")
        print(f"MiniMax request - Model: {self.model}")
        print(f"MiniMax request - Key prefix: {api_key[:10]}...")

        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"MiniMax response status: {response.status_code}")
        print(f"MiniMax response: {response.text[:1000]}")

        if response.status_code != 200:
            raise ValueError(f"MiniMax API错误: {response.text}")

        result = response.json()

        if "content" in result:
            # 返回text类型的内容
            for block in result["content"]:
                if block.get("type") == "text":
                    return block.get("text", "")
            raise ValueError(f"MiniMax响应中没有text内容: {result}")
        else:
            raise ValueError(f"MiniMax响应格式异常: {result}")

        # 尝试不同的API端点
        endpoints = [
            f"https://api.minimax.chat/v1/text/chatcompletion?GroupId={group_id}",
            f"https://api.minimax.chat/v1/text/chatcompletion_v2?GroupId={group_id}",
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 分离system消息
        system_content = ""
        minimax_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                minimax_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        data = {
            "model": self.model,
            "messages": minimax_messages,
            "system": system_content,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        last_error = None
        for url in endpoints:
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)

                if response.status_code == 200:
                    result = response.json()

                    # 处理不同的响应格式
                    if "choices" in result:
                        return result["choices"][0]["message"]["content"]
                    elif "completion_message" in result:
                        return result["completion_message"]["content"]
                    elif "base_resp" in result and result["base_resp"].get("status_code") != 0:
                        last_error = result["base_resp"]
                        continue
                    else:
                        print(f"MiniMax响应: {result}")
                        raise ValueError(f"未知的MiniMax响应格式: {result}")
                else:
                    last_error = response.text
            except Exception as e:
                last_error = str(e)

        # 所有端点都失败
        print(f"MiniMax API错误: {last_error}")
        raise ValueError(f"MiniMax API调用失败: {last_error}")


def create_client(provider: str = None, model: str = None) -> LLMClient:
    """创建LLM客户端的便捷函数"""
    return LLMClient(provider=provider, model=model)
