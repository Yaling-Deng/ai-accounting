# 快速开始指南

## 1. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

## 2. 配置 API Key

**注意**：确保虚拟环境已激活（命令行提示符前应显示 `(venv)`）

编辑 `.env` 文件，填入你的 API Key：

```env
DEEPSEEK_API_KEY=sk-...
```

## 3. 准备测试数据

**注意**：确保虚拟环境已激活

在 `data/input/` 目录下创建一个测试 Excel 文件 `test_sales.xlsx`，包含"礼包名称"列：

| 礼包名称 |
|---------|
| 2025奥飞中秋山海礼繁星 |
| 大闸蟹礼盒 |
| 白虹+2025盐池滩羊889 |
| 定制费 |
| 宜盾普空气炸锅4L |

## 4. 运行分类

**注意**：确保虚拟环境已激活

```bash
python -m src.main test_sales.xlsx
```

## 5. 查看结果

分类结果将保存在 `data/output/result_test_sales.xlsx`，包含：
- 原始数据的所有列
- **产品类型**：分类结果（常规册、生鲜专卡、不核算、定制册、实物集采、待确认）

## 常见问题

### Q: 如何修改分类关键词？
A: 直接编辑 `src/config.py` 文件中的 `CLASSIFICATION_KEYWORDS` 字典，添加或修改关键词。

### Q: 支持哪些 API？
A: 目前支持 OpenAI 和 DeepSeek API，优先使用 DeepSeek（如果配置了的话）。LLM 仅用于"实物集采"的判断，大部分分类通过规则匹配完成。

### Q: 如何处理大批量数据？
A: 系统会自动批量处理，规则匹配速度很快。只有规则无法确定的记录才会调用 LLM，因此 LLM 调用次数很少。

### Q: 分类结果不准确怎么办？
A: 可以修改 `src/config.py` 中的关键词列表，添加更多关键词以提高规则匹配的准确性。
