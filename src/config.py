"""
配置管理模块
"""
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
# 明确指定 .env 文件路径（相对于项目根目录）
PROJECT_ROOT = Path(__file__).parent.parent
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

# 项目根目录（已在上面定义）

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 默认使用 DeepSeek（如果没有配置 OpenAI）
DEFAULT_API_PROVIDER = "deepseek" if DEEPSEEK_API_KEY else "openai"
DEFAULT_API_KEY = DEEPSEEK_API_KEY if DEEPSEEK_API_KEY else OPENAI_API_KEY

# LLM API 配置
API_CONFIG = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "api_key": OPENAI_API_KEY,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "api_key": DEEPSEEK_API_KEY,
    }
}

# 产品分类配置
CLASSIFICATION_KEYWORDS = {
    "常规册": [
        "明月", "骄阳", "满月", "繁星", "山海礼系列", "朝霞", "潮汐", 
        "银河", "苍穹", "流光", "吉时至", "吉时福", "吉时禄", "吉时礼系列",
        "吉时禧", "吉时运", "吉时祥", "吉时泰", "吉时盈", "六选一月饼提领券",
        "中华月饼自选册"
    ],
    "生鲜专卡": [
        "大闸蟹", "海鲜", "滩羊", "牛肉", "水果", "吉时鲜"
    ],
    "不核算": [
        "定制费", "运费", "印刷费", "补差价", "提错折扣", 
        "员工福利", "宴请费用", "账务调整"
    ]
}

# 销售员名单（用于识别定制册）
SALESPERSON_NAMES = [
    "陈叶", "韩振华", "戴甜", "张一明", "赵艳伟", "任莎莎", "张鑫", "陈若寒", 
    "王婉婉", "马恩博", "刘敏", "郑洁", "廖旭", "曹梦瑶", "闫羽芹", "汪玲", 
    "夏爽", "王洋", "丁双平", "付昊", "杨江水", "刘彦彬", "白虹", "潘可盈", 
    "朱玉立", "王雨歌", "李宗隆", "陈敏", "王克承", "李加葵", "华栋", "余潞瑶", 
    "谭敏", "尹俊博", "杨凯", "韩啸", "杨凯迪", "李绘艳", "郭巧", "徐圆圆", 
    "杨小桐", "刘小芬", "何亚梅", "乔善丰", "何阳", "周宇", "姚卓凡", "谢毅", 
    "陈绪凯", "张园园", "张晓曼", "赵婷", "李嵩茜", "崔浩", "胡庆镇", "杨慧", 
    "陈丹妮", "杨广山", "李美彤", "全潇月", "戴茂元", "韩金龙", "吴圆圆", "易辰", 
    "夏佳月", "鲁红卫", "邓林玲", "李帆", "张子龙", "祁文文", "西南李帆", "范亮丁", 
    "肖迪文", "吴果霖", "陈铭", "王杭", "沈思华", "吴若凤", "杨帆", "李娜", 
    "刘炎壩", "张筱蕾", "黄宇", "张宏玮", "蔡梓华", "李炳材", "于福濛", "吕瑷伻", 
    "彭振祥", "刘苗苗", "王羽", "郭美霖", "王路", "崔化祥", "董洛语", "郇昌朋", 
    "张菁", "邓若晴", "刘天威", "黄敏", "杨清玥", "郗星泽", "刘雪莹", "陈琳", 
    "张李娜", "童卓文", "孙凯丽", "杨萌", "刘海明", "于丛洋", "胡松林", "张梦真"
]

# 定制册正则表达式（匹配"人名+礼包名"格式）
# 注意：现在优先使用 SALESPERSON_NAMES 进行匹配，此正则作为辅助或保留
CUSTOM_BOOK_PATTERN = re.compile(r'\w+\+.*')

# 分类配置
CLASSIFICATION_CONFIG = {
    "llm_temperature": 0.1,  # LLM 温度参数
    "llm_max_tokens": 500,  # LLM 最大输出 token 数
    "enable_cache": True,  # 是否启用分类结果缓存
}
