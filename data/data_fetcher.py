from typing import Dict
import ccxt
from decimal import Decimal


class DataFetcher:
    def __init__(self, exchange_id: str, api_key: str = None, secret: str = None):
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True
        })
    
    async def get_price(self, symbol: str, market_type: str = 'spot') -> Decimal:
        """获取价格信息"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return Decimal(str(ticker['last']))
        except Exception as e:
            raise Exception(f"获取{market_type}价格失败: {str(e)}")
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """获取订单簿数据"""
        try:
            return await self.exchange.fetch_order_book(symbol, limit)
        except Exception as e:
            raise Exception(f"获取订单簿失败: {str(e)}")

    async def close(self):
        """关闭连接"""
        await self.exchange.close()
