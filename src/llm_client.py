"""
LLM 客户端模块 - 轻量级 LLM API 调用工具
"""
import json
import requests
import re
from typing import Dict, Any, Optional
from .config import API_CONFIG, DEFAULT_API_PROVIDER, DEFAULT_API_KEY, CLASSIFICATION_CONFIG


class LLMClient:
    """轻量级 LLM 客户端"""
    
    def __init__(self):
        self.api_provider = DEFAULT_API_PROVIDER
        self.api_config = API_CONFIG[self.api_provider]
        self.api_key = DEFAULT_API_KEY
        
        if not self.api_key:
            raise ValueError("未配置 API Key，请在 .env 文件中设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY")
    
    def call_api(self, prompt: str, system_message: str = None, temperature: float = None, max_tokens: int = None) -> str:
        """
        调用 LLM API
        
        Args:
            prompt: 用户 Prompt
            system_message: 系统消息（可选）
            temperature: 温度参数（可选，默认使用配置值）
            max_tokens: 最大 token 数（可选，默认使用配置值）
            
        Returns:
            LLM 的响应文本
        """
        url = f"{self.api_config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.api_config["model"],
            "messages": messages,
            "temperature": temperature if temperature is not None else CLASSIFICATION_CONFIG["llm_temperature"],
            "max_tokens": max_tokens if max_tokens is not None else CLASSIFICATION_CONFIG["llm_max_tokens"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # 提取回复内容
            content = result["choices"][0]["message"]["content"]
            return content
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 调用失败: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"API 响应格式错误: {e}")
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析 LLM 响应为 JSON 格式
        
        Args:
            response: LLM 的响应文本
            
        Returns:
            解析后的 JSON 字典
        """
        # 尝试提取 JSON（可能包含在代码块中）
        response = response.strip()
        
        # 移除可能的 markdown 代码块标记
        if response.startswith("```"):
            lines = response.split("\n")
            # 移除第一行和最后一行（代码块标记）
            if len(lines) > 2:
                response = "\n".join(lines[1:-1])
        
        # 尝试解析 JSON
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # 如果解析失败，尝试提取 JSON 部分
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except json.JSONDecodeError:
                    pass
            
            # 如果还是失败，返回空字典
            return {}
