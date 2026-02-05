"""
产品类型分类模块 - 根据礼包名称自动识别产品类型
"""
from typing import List, Dict, Optional
from .config import CLASSIFICATION_KEYWORDS, CUSTOM_BOOK_PATTERN, CLASSIFICATION_CONFIG, SALESPERSON_NAMES
from .llm_client import LLMClient


class ProductClassifier:
    """产品类型分类器"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.cache = {} if CLASSIFICATION_CONFIG.get("enable_cache", True) else None
    
    def _rule_based_classify(self, name: str, sales_order_type: Optional[str] = None) -> Optional[str]:
        """
        基于规则的产品类型分类
        
        Args:
            name: 礼包名称
            sales_order_type: 销售单类型
            
        Returns:
            产品类型（如果规则匹配），否则返回 None
        """
        if not name or not isinstance(name, str):
            return None
        
        # 0. 检查销售单类型 (优先级最高)
        if sales_order_type and sales_order_type == "实物集采":
            return "实物集采"
            
        name_lower = name.lower()
        
        # 1. 检查定制册 (优先级: 销售员名字 > 正则)
        # 检查销售员名字
        for person in SALESPERSON_NAMES:
            if person in name:
                return "定制册"
        
        # 2. 检查常规册关键词
        for keyword in CLASSIFICATION_KEYWORDS["常规册"]:
            if keyword in name:
                return "常规册"
        
        # 3. 检查生鲜专卡关键词
        for keyword in CLASSIFICATION_KEYWORDS["生鲜专卡"]:
            if keyword in name:
                return "生鲜专卡"
        
        # 4. 检查不核算关键词
        for keyword in CLASSIFICATION_KEYWORDS["不核算"]:
            if keyword in name:
                return "不核算"
        
        # 5. 检查定制册格式（人名+礼包名）- 辅助匹配
        if CUSTOM_BOOK_PATTERN.search(name):
            return "定制册"
        
        # 规则无法确定
        return None
    
    def _llm_classify(self, name: str) -> str:
        """
        使用 LLM 判断是否为生鲜专卡
        
        Args:
            name: 礼包名称
            
        Returns:
            产品类型（生鲜专卡 或 待确认）
        """
        if self.llm_client is None or getattr(self.llm_client, "available", False) is False:
            s = (name or "").lower()
            heuristics = ["牛肉", "羊肉", "猪肉", "鸡", "鸭", "鱼", "虾", "蟹", "贝", "海鲜", "生鲜", "水果", "和牛"]
            for kw in heuristics:
                if kw in name:
                    return "生鲜专卡"
            return "待确认"
        
        prompt = f"""请判断以下礼包名称是否属于“生鲜专卡”类别。
        
判定标准：
如果名称中包含肉类（如牛肉、羊肉、猪肉、鸡肉、鸭肉等）、海鲜类（如鱼、虾、蟹、贝等）、水果类等生鲜食品，则属于“生鲜专卡”。
注意：
1. 不要把具体的电器、家居用品判定为生鲜。
2. 实物集采已经由其他规则处理，这里只关注生鲜食品。

名称：{name}

请以 JSON 格式输出：
{{
    "产品类型": "生鲜专卡" 或 "待确认",
    "置信度": 0-1之间的小数,
    "原因": "简要说明判定原因"
}}"""
        
        system_message = "你是一个产品分类专家，擅长识别生鲜食品类礼包。请始终以 JSON 格式输出结果。"
        
        try:
            response = self.llm_client.call_api(prompt, system_message=system_message)
            result = self.llm_client.parse_json_response(response)
            
            product_type = result.get("产品类型", "待确认")
            # 确保返回的是有效的产品类型
            if product_type not in ["生鲜专卡", "待确认"]:
                product_type = "待确认"
            
            return product_type
        except Exception as e:
            # LLM 调用失败，返回待确认
            return "待确认"
    
    def classify_product_type(self, name: str, sales_order_type: Optional[str] = None) -> str:
        """
        分类单个产品类型
        
        Args:
            name: 礼包名称
            sales_order_type: 销售单类型
            
        Returns:
            产品类型：常规册、生鲜专卡、不核算、定制册、实物集采、待确认
        """
        # 注意：如果引入了 sales_order_type，缓存 key 应该包含它，或者只在 sales_order_type 为空时使用简单缓存
        # 为简单起见，如果提供了 sales_order_type 且为实物集采，直接处理不查缓存
        if sales_order_type == "实物集采":
            return "实物集采"

        # 检查缓存 (仅当没有特殊销售单类型或类型不影响规则时)
        # 这里的简化处理：如果 sales_order_type 存在，可能会影响结果，所以暂时跳过缓存或组合 key
        # 为了安全，如果有 sales_order_type，先跳过缓存，或者 key = f"{name}|{sales_order_type}"
        cache_key = f"{name}|{sales_order_type}" if sales_order_type else name
        
        if self.cache is not None and cache_key in self.cache:
            return self.cache[cache_key]
        
        # 先尝试规则匹配
        rule_result = self._rule_based_classify(name, sales_order_type)
        if rule_result:
            result = rule_result
        else:
            # 规则无法确定，使用 LLM 判断是否为生鲜专卡
            result = self._llm_classify(name)
        
        # 缓存结果
        if self.cache is not None:
            self.cache[cache_key] = result
        
        return result
    
    def classify_batch(self, names: List[str], sales_order_types: Optional[List[str]] = None) -> List[str]:
        """
        批量分类产品类型
        
        Args:
            names: 礼包名称列表
            sales_order_types: 销售单类型列表 (与 names 对应)
            
        Returns:
            产品类型列表
        """
        results = []
        total = len(names)
        
        if sales_order_types and len(sales_order_types) != total:
            print(f"警告: 销售单类型列表长度 ({len(sales_order_types)}) 与礼包名称列表长度 ({total}) 不匹配，将忽略销售单类型")
            sales_order_types = None
        
        print(f"开始批量分类，共 {total} 条记录...")
        
        for i, name in enumerate(names, 1):
            if i % 100 == 0 or i == total:
                print(f"  处理进度: {i}/{total}")
            
            s_type = sales_order_types[i-1] if sales_order_types else None
            product_type = self.classify_product_type(name, s_type)
            results.append(product_type)
        
        print(f"批量分类完成，共处理 {len(results)} 条记录")
        
        # 统计分类结果
        from collections import Counter
        stats = Counter(results)
        print("\n分类统计:")
        for product_type, count in stats.items():
            print(f"  {product_type}: {count} 条")
        
        return results
