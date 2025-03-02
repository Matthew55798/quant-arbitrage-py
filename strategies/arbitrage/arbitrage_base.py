from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from decimal import Decimal

class ArbitrageStrategy(ABC):
    """
    套利策略的基类
    
    属性:
        min_profit (float): 最小利润率阈值
    """
    
    def __init__(self, min_profit: float):
        """
        初始化套利策略
        
        Args:
            min_profit: 执行套利的最小利润率阈值
        """
        self.min_profit = min_profit
    
    @abstractmethod
    async def find_opportunities(self) -> Dict:
        """寻找套利机会"""
        pass
    
    @abstractmethod
    async def execute_arbitrage(self, opportunity: Dict) -> bool:
        """执行套利交易"""
        pass
    
    def calculate_profit(self, prices: Dict[str, Decimal], path: List[str], fee: Decimal) -> Tuple[Decimal, List[str]]:
        """
        计算给定交易路径的套利利润
        
        Args:
            prices: 币对价格字典，如 {'BTC/USDT': 50000, 'ETH/BTC': 0.07, ...}
            path: 交易路径，如 ['USDT', 'BTC', 'ETH', 'USDT']
            fee: 每笔交易的手续费率
            
        Returns:
            (profit, steps): 利润率和具体交易步骤
        """
        value = Decimal('1')
        steps = []
        
        for i in range(len(path) - 1):
            start_coin = path[i]
            end_coin = path[i + 1]
            
            # 构建交易对
            direct_pair = f"{end_coin}/{start_coin}"
            reverse_pair = f"{start_coin}/{end_coin}"
            
            if direct_pair in prices:
                # 买入 end_coin
                value = value / prices[direct_pair] * (Decimal('1') - fee)
                steps.append(f"买入 {direct_pair}")
            elif reverse_pair in prices:
                # 卖出 start_coin
                value = value * prices[reverse_pair] * (Decimal('1') - fee)
                steps.append(f"卖出 {reverse_pair}")
            else:
                raise ValueError(f"找不到交易对: {start_coin}-{end_coin}")
        
        profit = value - Decimal('1')
        return profit, steps 