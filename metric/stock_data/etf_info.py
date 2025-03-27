import akshare as ak


class ETFInfoMgr(object):
    def __init__(self) -> None:
        self.raw = ak.fund_etf_category_sina(symbol='ETF基金')
        self.symbol_name_map = {}
        self.name_symbol_map = {}
        for i, row in self.raw.iterrows():
            symbol = row['代码']
            name = row['名称']
            self.symbol_name_map[symbol] = name
            self.name_symbol_map[name] = symbol

    def query_name(self, symbol):
        return self.symbol_name_map.get(symbol, None)

    def query_symbol(self, name):
        return self.name_symbol_map.get(name, None)


_mgr = ETFInfoMgr()


def query_etf_name(symbol: str):
    return _mgr.query_name(symbol=symbol)


def query_etf_symbol(name: str):
    return _mgr.query_symbol(name=name)
