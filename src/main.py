"""
主程序入口
"""
import argparse
from pathlib import Path
import pandas as pd
from .data_loader import DataLoader
from .product_classifier import ProductClassifier
from .llm_client import LLMClient


def classify_products(input_filename: str, output_filename: str = None, column_name: str = None):
    """
    产品类型分类主函数
    
    Args:
        input_filename: 输入 Excel 文件名
        output_filename: 输出 Excel 文件名（可选，默认自动生成）
        column_name: 礼包名称列名（可选，默认自动检测）
    """
    print("=" * 60)
    print("产品类型自动分类系统")
    print("=" * 60)
    
    # 初始化组件
    data_loader = DataLoader()
    llm_client = LLMClient()
    product_classifier = ProductClassifier(llm_client)
    
    # 1. 加载 Excel
    print(f"\n[1/4] 加载 Excel 文件: {input_filename}")
    try:
        df = data_loader.load_sales_data(input_filename)
        print(f"  成功加载 {len(df)} 条记录")
        print(f"  数据列: {', '.join(df.columns.tolist())}")
    except Exception as e:
        print(f"  错误: {e}")
        return
    
    # 2. 检测礼包名称列
    print(f"\n[2/4] 检测礼包名称列...")
    try:
        if column_name:
            if column_name not in df.columns:
                print(f"  错误: 指定的列名 '{column_name}' 不存在")
                print(f"  可用列名: {', '.join(df.columns.tolist())}")
                return
            gift_name_col = column_name
        else:
            gift_name_col = data_loader.detect_gift_name_column(df)
        print(f"  检测到列名: {gift_name_col}")
    except Exception as e:
        print(f"  错误: {e}")
        return
    
    # 3. 产品分类
    print(f"\n[3/4] 开始产品类型分类...")
    try:
        # 准备销售单类型数据 (必须存在)
        if "销售单类型" not in df.columns:
            raise ValueError("输入文件中缺少'销售单类型'列，该列是判断实物集采的必要条件。")
            
        print(f"  检测到'销售单类型'列，将用于判定实物集采")
        sales_order_types = df["销售单类型"].astype(str).tolist()
            
        product_types = product_classifier.classify_batch(
            df[gift_name_col].tolist(),
            sales_order_types=sales_order_types
        )
    except Exception as e:
        print(f"  错误: {e}")
        return
    
    # 4. 添加产品类型列并保存
    print(f"\n[4/4] 保存结果...")
    try:
        df = data_loader.add_product_type_column(df, product_types)
        
        if "价格类型" not in df.columns:
            raise ValueError("输入文件中缺少'价格类型'列，该列是结算规则处理的必要条件。")
        
        def normalize_price_type(val):
            if pd.isna(val):
                return val
            s = str(val)
            lower = s.lower()
            if "vp" in lower:
                return "按vp价结算"
            if "总监" in s:
                return "按总监价结算"
            if "核心" in s:
                return "按核心价结算"
            if "优惠" in s:
                return "按优惠价结算"
            if "常规" in s:
                return "按常规价结算"
            return s
        
        mask = df["产品类型"].isin(["常规册", "生鲜专卡"])
        df.loc[mask, "价格类型"] = df.loc[mask, "价格类型"].apply(normalize_price_type)
        
        # 生成输出文件名
        if output_filename is None:
            input_stem = Path(input_filename).stem
            output_filename = f"result_{input_stem}.xlsx"
        
        output_path = data_loader.save_results(df, output_filename)
        print(f"\n✓ 分类完成！结果已保存至: {output_path}")
    except Exception as e:
        print(f"  错误: {e}")
        return
    
    print("\n" + "=" * 60)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="产品类型自动分类系统 - 根据礼包名称自动识别产品类型"
    )
    
    parser.add_argument(
        "input_file",
        help="输入 Excel 文件名（位于 data/input/ 目录）"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出 Excel 文件名（可选，默认自动生成）"
    )
    parser.add_argument(
        "-c", "--column",
        dest="column_name",
        help="礼包名称列名（可选，默认自动检测）"
    )
    
    args = parser.parse_args()
    classify_products(args.input_file, args.output, args.column_name)


if __name__ == "__main__":
    main()
