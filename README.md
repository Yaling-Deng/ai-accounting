# 产品类型自动分类系统

## 项目简介

这是一个基于 Python 和 LLM API 的产品类型自动分类系统。系统通过读取 Excel 文件中的"礼包名称"字段，使用混合方案（规则匹配 + LLM 辅助）自动识别产品类型，并输出带分类结果的 Excel 文件。

## 核心特性

- ✅ **Excel In -> Python + LLM -> Excel Out** 的完整流程
- ✅ **混合分类策略**：规则匹配优先，LLM 兜底判断
- ✅ **无数据库设计**：使用纯文件操作（Excel）
- ✅ **批量处理**：支持大批量数据的自动分类
- ✅ **自动列检测**：自动识别"礼包名称"列
- ✅ **五类产品识别**：常规册、生鲜专卡、不核算、定制册、实物集采

## 项目结构

```
project_root/
│
├── data/
│   ├── input/                # 存放待分类的 Excel 文件
│   └── output/               # 存放分类结果 Excel 文件
│
├── src/
│   ├── __init__.py
│   ├── config.py             # API Key 和配置项（包含分类关键词）
│   ├── data_loader.py        # Excel 读写逻辑
│   ├── llm_client.py         # 轻量级 LLM API 调用工具
│   ├── product_classifier.py # 产品分类核心模块
│   └── main.py               # 主程序入口
│
├── requirements.txt
├── .env                      # 存放 OPENAI_API_KEY / DEEPSEEK_API_KEY
└── README.md
```

## 安装和配置

### 1. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### 2. 安装依赖

```bash
# 确保虚拟环境已激活，然后安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置 API Key

编辑 `.env` 文件，填入你的 API Key（至少配置一个）：

```env
# OpenAI API Key (可选)
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek API Key (可选，推荐)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 4. 准备数据文件

将待分类的 Excel 文件放入 `data/input/` 目录。

Excel 文件需要包含"礼包名称"相关的列（系统会自动检测，或使用 `-c` 参数指定列名）。

## 使用方法

**注意**：使用前请确保虚拟环境已激活（`source venv/bin/activate`）

### 基本用法

```bash
# 自动检测列名
python -m src.main sales_jan.xlsx

# 指定输出文件名
python -m src.main sales_jan.xlsx -o result_jan.xlsx

# 手动指定礼包名称列名
python -m src.main sales_jan.xlsx -c "产品名称"
```

## 产品类型分类规则

系统支持以下五类产品类型的自动识别：

### 1. 常规册
包含以下关键词：明月、骄阳、满月、繁星、山海礼系列、朝霞、潮汐、银河、苍穹、流光、吉时至、吉时福、吉时禄、吉时礼系列、吉时禧、吉时运、吉时样、吉时泰、吉时盈、六选一月饼提领券

### 2. 生鲜专卡
包含以下关键词：大闸蟹、海鲜、滩羊、牛肉、水果、吉时鲜等

### 3. 不核算
包含以下关键词：定制费、运费、印刷费、补差价、提错折扣、员工福利、宴请费用、账务调整

### 4. 定制册
格式为"人名+礼包名"，例如：`白虹+2025盐池滩羊889`、`廖旭+2025奥飞中秋山海礼繁星`

### 5. 实物集采
规则无法确定时，使用 LLM 判断是否为具体商品名称（如"宜盾普空气炸锅4L"、"康宁 晶耀系列玻璃餐具8件套"等）

## 工作流程

1. **数据加载**：从 `data/input/` 读取 Excel 文件
2. **列名检测**：自动检测或手动指定"礼包名称"列
3. **规则匹配**：使用关键词和正则表达式进行快速分类
4. **LLM 判断**：规则无法确定时，调用 LLM 判断是否为"实物集采"
5. **结果输出**：将分类结果保存到 `data/output/` 目录

## 输出格式

分类结果 Excel 文件包含：

- 原始数据的所有列
- **产品类型**：分类结果（常规册、生鲜专卡、不核算、定制册、实物集采、待确认）

## 分类策略

系统采用混合分类策略：

1. **规则优先**：前4类（常规册、生鲜专卡、不核算、定制册）使用规则匹配，速度快、成本低
2. **LLM 兜底**：规则无法确定时，调用 LLM 判断是否为"实物集采"
3. **性能优化**：批量处理，减少 LLM 调用次数

## 配置说明

分类关键词和配置在 `src/config.py` 中定义，可以根据实际需求修改：

- `CLASSIFICATION_KEYWORDS`：各类产品的关键词列表
- `CUSTOM_BOOK_PATTERN`：定制册的正则表达式
- `CLASSIFICATION_CONFIG`：LLM 调用参数等配置

## 注意事项

- 确保 Excel 文件格式正确，包含"礼包名称"相关的列
- API Key 需要有效且有足够的额度（仅用于"实物集采"的判断）
- 大部分分类通过规则匹配完成，LLM 调用次数较少
- 建议先在小批量数据上测试

## 许可证

MIT License
