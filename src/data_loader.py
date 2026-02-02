"""
Excel 数据加载和处理模块
"""
import pandas as pd
from pathlib import Path
from typing import List, Optional
from .config import INPUT_DIR, OUTPUT_DIR


class DataLoader:
    """Excel 数据加载器"""
    
    def __init__(self):
        self.input_dir = INPUT_DIR
        self.output_dir = OUTPUT_DIR
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_sales_data(self, filename: str) -> pd.DataFrame:
        """
        加载销售数据 Excel 文件
        
        Args:
            filename: Excel 文件名（如 sales_jan.xlsx）
            
        Returns:
            包含销售数据的 DataFrame
        """
        file_path = self.input_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        df = pd.read_excel(file_path)
        return df
    
    def save_results(self, df: pd.DataFrame, filename: str) -> Path:
        """
        保存结果到 Excel
        
        Args:
            df: 包含结果的 DataFrame
            filename: 输出文件名（如 result_jan.xlsx）
            
        Returns:
            保存的文件路径
        """
        output_path = self.output_dir / filename
        df.to_excel(output_path, index=False)
        return output_path
    
    def detect_gift_name_column(self, df: pd.DataFrame) -> str:
        """
        自动检测"礼包名称"列
        
        Args:
            df: DataFrame
            
        Returns:
            列名
            
        Raises:
            ValueError: 如果无法找到合适的列
        """
        # 只允许精确匹配“礼包名称”，避免误判到“客户名称/CRM客户名称”等字段
        if "礼包名称" in df.columns:
            return "礼包名称"

        # 如果找不到，直接报错（由调用方用 -c/--column 手动指定）
        raise ValueError(
            f"无法自动检测'礼包名称'列。\n"
            f"可用列名: {', '.join(df.columns.tolist())}\n"
            f"请使用 -c/--column 参数指定列名。"
        )
    
    def add_product_type_column(
        self, 
        df: pd.DataFrame, 
        product_types: List[str]
    ) -> pd.DataFrame:
        """
        添加产品类型列到 DataFrame
        
        Args:
            df: 原始 DataFrame
            product_types: 产品类型列表（与 DataFrame 行数相同）
            
        Returns:
            添加了产品类型列的 DataFrame
        """
        df = df.copy()
        
        if len(product_types) != len(df):
            raise ValueError(
                f"产品类型列表长度 ({len(product_types)}) 与 DataFrame 行数 ({len(df)}) 不匹配"
            )
        
        df["产品类型"] = product_types
        return df
