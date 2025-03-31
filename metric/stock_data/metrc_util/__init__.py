from util.log import logger


def parse_money_unit(money_str) -> str:
    if "万" in money_str:
        return "万人民币"
    if "亿" in money_str:
        return "亿人民币"
    return "None"


def parse_money_num_with_unit(num_str: str) -> float:
    if not isinstance(num_str, str):
        logger.warning(f"invalid num_str: {num_str}")
        return 0
    if "万亿" in num_str:
        return float(num_str.replace("万亿", "")) * 10000 * 10000 * 10000
    if "万" in num_str:
        return float(num_str.replace("万", "")) * 10000
    if "亿" in num_str:
        return float(num_str.replace("亿", "")) * 10000 * 10000
    return float(num_str)


# 装饰器，用于将df统一根据日期排序
def sort_by_date(func):
    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)
        df = df.sort_values(by=["date"], ascending=False)
        return df

    return wrapper

# 缓存适配器，将ak包的同名且参数相同的函数调用结果缓存下来
def cache_adapter(func):
    def wrapper(*args, **kwargs):
        key = f"{func.__name__}_{args}_{kwargs}"
        if key in wrapper.cache:
            return wrapper.cache[key]
        result = func(*args, **kwargs)
        wrapper.cache[key] = result
        return result
    wrapper.cache = {}
    return wrapper