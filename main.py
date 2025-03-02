import asyncio
import logging
from data.data_fetcher import DataFetcher
from strategies.arbitrage.contract_arbitrage import ContractArbitrage
from config.config import BaseConfig, ArbitrageConfig


async def main():
    # 配置日志
    logging.basicConfig(
        level=BaseConfig.LOG_LEVEL,
        format=BaseConfig.LOG_FORMAT,
        filename=BaseConfig.LOG_FILE
    )

    try:
        # 初始化数据获取器
        data_fetcher = DataFetcher(exchange_id=BaseConfig.EXCHANGE_ID)
        
        # 初始化套利策略
        arbitrage = ContractArbitrage(
            min_profit=ArbitrageConfig.MIN_PROFIT,
            data_fetcher=data_fetcher
        )
        
        # 初始化交易所连接
        await arbitrage.initialize()
        
        try:
            while True:
                # 寻找套利机会
                opportunity = await arbitrage.find_opportunities()
                
                # 如果发现套利机会，执行套利
                if opportunity and opportunity.get('profit', 0) > ArbitrageConfig.MIN_PROFIT:
                    success = await arbitrage.execute_arbitrage(opportunity)
                    if success:
                        logging.info("套利执行成功")
                    else:
                        logging.warning("套利执行失败")
                
                # 等待一段时间再次检查
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("程序正在停止...")
        finally:
            # 关闭连接
            await arbitrage.close()
            await data_fetcher.close()
            
    except Exception as e:
        logging.error(f"程序运行错误: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 