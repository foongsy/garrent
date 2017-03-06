import math
import re
import decimal


def is_NaN(value):
    """
    check value is nan or not
    :param value:
    :return: bool
    """
    if isinstance(value, float):
        return math.isnan(value)
    else:
        return value != value


def convert_currency(value):
    """
    convert number likes  HKD 4.40
    :param value:
    :return:
    """
    if value:
        try:
            result = decimal.Decimal(re.sub(r'[^\d.]', '', value))
        except decimal.InvalidOperation as e:
            raise e
        else:
            return result
    else:
        return None

def convert_float(value):
    """
    :param value:
    :return:
    """
    try:
        result = float(value)
    except ValueError:
        pass
    else:
        return result

def parse_int(value):
    """
    convert number value like 796,529,786(L) to int
    :param value:
    :return:
    """
    value = value.replace(",", "")
    return re.search(r'\d+', value).group()

def convert_code(code):
    """
    try to convert stock code
    :param code:
    :return:
    """
    if len(code) < 5:
        new_code = "0" * (5 - len(code)) + code
    else:
        new_code = code

    return new_code
