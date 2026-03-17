"""
API密钥加密存储与管理模块
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional

from cryptography.fernet import Fernet

from .settings import PROJECT_ROOT


class APIManager:
    """API密钥管理器 - 支持加密存储和多提供商切换"""

    def __init__(self):
        self.key_file = PROJECT_ROOT / ".api_keys.enc"
        self.config_file = PROJECT_ROOT / "api_config.json"
        self._fernet = self._init_fernet()
        self._load_config()

    def _init_fernet(self) -> Fernet:
        """初始化Fernet加密器"""
        key_path = PROJECT_ROOT / ".key"
        if key_path.exists():
            with open(key_path, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
        return Fernet(key)

    def _load_config(self):
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "minimax_group_id": "",
            }
            self._save_config()

    def _save_config(self):
        """保存配置"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_api_key(self, provider: str) -> Optional[str]:
        """获取API密钥(解密后)"""
        if not self.key_file.exists():
            return None

        with open(self.key_file, "rb") as f:
            encrypted_data = f.read()

        try:
            decrypted = self._fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted)
            return keys.get(provider)
        except Exception:
            return None

    def set_api_key(self, provider: str, api_key: str):
        """设置API密钥(加密存储)"""
        # 读取现有密钥
        keys = {}
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                encrypted_data = f.read()
            try:
                decrypted = self._fernet.decrypt(encrypted_data)
                keys = json.loads(decrypted)
            except Exception:
                keys = {}

        keys[provider] = api_key

        # 加密并保存
        encrypted = self._fernet.encrypt(json.dumps(keys).encode())
        with open(self.key_file, "wb") as f:
            f.write(encrypted)

    def get_provider(self) -> str:
        """获取当前提供商"""
        return self.config.get("provider", "openai")

    def set_provider(self, provider: str):
        """设置当前提供商"""
        self.config["provider"] = provider
        self._save_config()

    def get_model(self) -> str:
        """获取当前模型"""
        return self.config.get("model", "gpt-4o-mini")

    def set_model(self, model: str):
        """设置当前模型"""
        self.config["model"] = model
        self._save_config()

    def get_minimax_group_id(self) -> str:
        """获取MiniMax Group ID"""
        return self.config.get("minimax_group_id", "")

    def set_minimax_group_id(self, group_id: str):
        """设置MiniMax Group ID"""
        self.config["minimax_group_id"] = group_id
        self._save_config()

    def get_all_keys(self) -> Dict[str, str]:
        """获取所有已存储的API密钥(用于检查哪些已配置)"""
        if not self.key_file.exists():
            return {}

        with open(self.key_file, "rb") as f:
            encrypted_data = f.read()

        try:
            decrypted = self._fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted)
            # 返回掩码后的密钥
            return {
                k: f"{v[:8]}...{v[-4:]}" if v else None
                for k, v in keys.items()
            }
        except Exception:
            return {}


# 全局实例
api_manager = APIManager()
