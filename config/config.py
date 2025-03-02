import os
from decimal import Decimal
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class BaseConfig:
    """基础配置"""
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'crypto_arbitrage.log'

    # 交易所配置
    EXCHANGE_ID = 'binance'  # 使用的交易所ID


class BinanceConfig:
    """币安交易所配置"""
    # 实盘API配置
    API_KEY = 'your_api_key'
    API_SECRET = 'your_api_secret'
    
    # 测试网配置
    TEST_API_KEY = 'lN0KEIpQOy3rboPv3EK8tZmNE9Z2PsYtcJZkyuZ1USHQ0FNdWMcQs8FsGnNPXdtO'
    TEST_API_SECRET = 'iRipiF1gQiyTlsfIgRx4Cmk6qE3aML839r6XLHyl5y0YqlZomRYBnjf5QUEL1Ldl'
    
    # 环境配置
    USE_TEST_NET = True
    
    @classmethod
    def get_credentials(cls):
        """获取当前环境的API凭证"""
        if cls.USE_TEST_NET:
            return cls.TEST_API_KEY, cls.TEST_API_SECRET
        return cls.API_KEY, cls.API_SECRET


class ArbitrageConfig:
    """套利策略配置"""
    # 交易对配置
    SYMBOLS = ["BTC/USDT", "ETH/BTC", "ETH/USDT"]
    
    # 交易参数
    FEE = Decimal('0.0003')  # 0.03% 交易手续费
    MIN_PROFIT = Decimal('0.001')  # 最小利润率
    MAX_TRADE_AMOUNT = Decimal('1000')  # 最大交易USDT金额
    SLIPPAGE_TOLERANCE = Decimal('0.001')  # 0.1%滑点容忍度

    # 风控参数
    MAX_RETRY_TIMES = 3  # 最大重试次数
    ORDER_TIMEOUT = 30  # 订单超时时间(秒) 