from decimal import Decimal
import logging
from typing import Dict, Tuple

from binance.client import AsyncClient
from binance.exceptions import BinanceAPIException

from .arbitrage_base import ArbitrageStrategy
from data.data_fetcher import DataFetcher
from config.config import BinanceConfig, ArbitrageConfig

class ContractArbitrage(ArbitrageStrategy):
    def __init__(self, min_profit: float, data_fetcher: DataFetcher):
        super().__init__(min_profit)
        self.data_fetcher = data_fetcher
        self.client = None
        self._load_config()

    def _load_config(self):
        """加载配置参数"""
        self.symbols = ArbitrageConfig.SYMBOLS
        self.fee = ArbitrageConfig.FEE
        self.max_trade_amount = ArbitrageConfig.MAX_TRADE_AMOUNT
        self.slippage_tolerance = ArbitrageConfig.SLIPPAGE_TOLERANCE

    async def initialize(self):
        """初始化 Binance 客户端"""
        api_key, api_secret = BinanceConfig.get_credentials()
        self.client = await AsyncClient.create(
            api_key=api_key,
            api_secret=api_secret,
            testnet=BinanceConfig.USE_TEST_NET
        )

    async def find_opportunities(self) -> Dict:
        """
        实现父类的抽象方法，寻找套利机会
        """
        # TODO: 实现具体的套利机会查找逻辑
        pass

    async def execute_arbitrage(self, opportunity: Dict) -> bool:
        """执行三角套利交易"""
        if not self._is_profitable_opportunity(opportunity):
            return False

        try:
            if not await self._check_sufficient_balance():
                return False

            trade_amounts = self._calculate_trade_amounts(opportunity)
            return await self._execute_trades(trade_amounts, opportunity)

        except Exception as e:
            logging.error(f"执行套利失败: {str(e)}")
            return False

    def _is_profitable_opportunity(self, opportunity: Dict) -> bool:
        """检查套利机会是否满足最小利润要求"""
        return opportunity and opportunity.get('profit', 0) > self.min_profit

    async def _check_sufficient_balance(self) -> bool:
        """检查USDT余额是否充足"""
        has_balance, usdt_balance = await self._get_balance('USDT')
        if not has_balance or usdt_balance < self.max_trade_amount:
            logging.warning(f"USDT余额不足: {usdt_balance}")
            return False
        return True

    def _calculate_trade_amounts(self, opportunity: Dict) -> Dict[str, Decimal]:
        """计算每步交易的数量"""
        has_balance, usdt_balance =  self._get_balance('USDT')
        trade_amount = min(self.max_trade_amount, usdt_balance)
        eth_amount = trade_amount / Decimal(str(opportunity['ETH/USDT']))
        btc_amount = eth_amount * Decimal(str(opportunity['ETH/BTC']))

        return {
            'eth_amount': eth_amount,
            'btc_amount': btc_amount
        }

    async def _execute_trades(self, amounts: Dict[str, Decimal], opportunity: Dict) -> bool:
        """执行三步套利交易"""
        trades = [
            ('ETH/USDT', 'BUY', amounts['eth_amount']),
            ('ETH/BTC', 'SELL', amounts['eth_amount']),
            ('BTC/USDT', 'SELL', amounts['btc_amount'])
        ]

        for symbol, side, quantity in trades:
            if not await self._place_order(symbol, side, quantity):
                # TODO: 实现交易回滚机制
                return False

        logging.info(f"三角套利执行成功! 预期收益: {opportunity['profit']:.4%}")
        return True

    async def _get_balance(self, symbol: str) -> Tuple[bool, Decimal]:
        """获取指定币种的可用余额"""
        try:
            account = await self.client.get_account()
            for balance in account['balances']:
                if balance['asset'] == symbol:
                    return True, Decimal(balance['free'])
            return False, Decimal('0')
        except BinanceAPIException as e:
            logging.error(f"检查余额失败: {str(e)}")
            return False, Decimal('0')

    async def _place_order(self, symbol: str, side: str, quantity: Decimal) -> bool:
        """执行订单"""
        try:
            formatted_symbol = symbol.replace('/', '')
            quantity = self._format_quantity(formatted_symbol, quantity)
            
            order = await self.client.create_order(
                symbol=formatted_symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            logging.info(f"订单执行成功: {order}")
            return True

        except BinanceAPIException as e:
            logging.error(f"下单失败: {str(e)}")
            return False

    async def _format_quantity(self, symbol: str, quantity: Decimal) -> float:
        """根据交易对精度格式化交易数量"""
        exchange_info = await self.client.get_exchange_info()
        symbol_info = next(
            (item for item in exchange_info['symbols'] if item['symbol'] == symbol),
            None
        )
        
        if not symbol_info:
            raise ValueError(f"未找到交易对信息: {symbol}")

        precision = symbol_info['baseAssetPrecision']
        return float(quantity.quantize(Decimal(f'0.{"0" * precision}')))

    async def close(self):
        """关闭连接"""
        if self.client:
            await self.client.close_connection() 