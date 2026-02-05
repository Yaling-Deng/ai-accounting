import io
from pathlib import Path
import pandas as pd
import streamlit as st
from src.data_loader import DataLoader
from src.product_classifier import ProductClassifier
from src.llm_client import LLMClient
from src.config import INPUT_DIR, OUTPUT_DIR, DEFAULT_API_PROVIDER, DEFAULT_API_KEY

st.set_page_config(page_title="产品&价格类型自动分类系统", layout="wide")
st.title("产品&价格类型自动分类系统")

data_loader = DataLoader()

uploaded = st.file_uploader("上传 Excel 文件", type=["xlsx"])
use_llm = st.checkbox("启用 LLM 生鲜判断", value=True)
run_btn = st.button("开始分类")

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

pass

if run_btn:
    if uploaded is None:
        st.error("请先上传 Excel 文件")
        st.stop()
    input_path = INPUT_DIR / uploaded.name
    input_path.parent.mkdir(parents=True, exist_ok=True)
    with open(input_path, "wb") as f:
        f.write(uploaded.getbuffer())
    df = data_loader.load_sales_data(uploaded.name)
    if "礼包名称" not in df.columns:
        st.error("缺少“礼包名称”列")
        st.stop()
    if "销售单类型" not in df.columns:
        st.error("缺少“销售单类型”列")
        st.stop()
    gift_col = "礼包名称"
    sales_types = df["销售单类型"].astype(str).tolist()
    llm_client = LLMClient() if use_llm else None
    classifier = ProductClassifier(llm_client)
    names = df[gift_col].tolist()
    total = len(names)
    product_types = []
    import math
    with st.spinner("执行中"):
        prog = st.progress(0)
        for i, name in enumerate(names, 1):
            s_type = sales_types[i-1] if sales_types else None
            product_types.append(classifier.classify_product_type(name, s_type))
            ratio = int(i * 100 / total)
            prog.progress(min(100, max(0, ratio)))
    df = data_loader.add_product_type_column(df, product_types)
    if "价格类型" not in df.columns:
        st.error("缺少“价格类型”列")
        st.stop()
    mask = df["产品类型"].isin(["常规册", "生鲜专卡"])
    df.loc[mask, "价格类型"] = df.loc[mask, "价格类型"].apply(normalize_price_type)
    from collections import Counter
    stats = Counter(df["产品类型"].tolist())
    st.subheader("分类统计")
    st.write({k: int(v) for k, v in stats.items()})
    st.subheader("结果预览（前10行）")
    st.dataframe(df.head(10), use_container_width=True)
    st.subheader("价格类型分布（仅常规册/生鲜专卡）")
    vc = df.loc[mask, "价格类型"].value_counts(dropna=False)
    st.write(vc)
    output_name = f"result_{Path(uploaded.name).stem}.xlsx"
    output_path = OUTPUT_DIR / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data_loader.save_results(df, output_name)
    st.success(f"已保存至: {output_path}")
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        label="下载结果 Excel",
        data=bio.getvalue(),
        file_name=output_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
