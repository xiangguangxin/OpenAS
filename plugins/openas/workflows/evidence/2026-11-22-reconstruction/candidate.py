"""基于已授权合成观测独立实现的数值列表求和。"""


def total(items):
    """累加 int/float 项；布尔值与非数值项抛出 ValueError。"""
    result = 0
    for item in items:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError("items must contain int or float values")
        result += item
    return result
