import os
from dotenv import load_dotenv
load_dotenv()
from langchain.tools import tool
from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper
from logger.decorators import log_entry

@tool
@log_entry
def multiply(a: int, b: int) -> int:
    """
    Multiply two integers.

    This tool takes two integer values and returns their product.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The product of `a` and `b`.
    """
    print('Entered into multiply().')
    return a * b

@tool
@log_entry
def add(a: int, b: int) -> int:
    """
    Add two integers.

    This tool takes two integer values and returns their sum.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The sum of `a` and `b`.
    """
    print('Entered into add().')
    return a + b

@tool
@log_entry
def currency_converter(from_curr: str, to_curr: str, value: float) -> float:
    """
    Convert a currency value from one currency to another using real-time exchange rates.

    This tool uses the AlphaVantage API to fetch real-time exchange rates and converts 
    the given value from `from_curr` to `to_curr`.

    Args:
        from_curr (str): The currency code to convert from (e.g., "USD").
        to_curr (str): The currency code to convert to (e.g., "EUR").
        value (float): The numeric amount in the `from_curr` currency.

    Returns:
        float: The equivalent amount in `to_curr` currency based on the current exchange rate.
    """
    print('Entered into currency_converter().')
    os.environ["ALPHAVANTAGE_API_KEY"] = os.getenv('ALPHAVANTAGE_API_KEY')
    alpha_vantage = AlphaVantageAPIWrapper()
    response = alpha_vantage._get_exchange_rate(from_curr, to_curr)
    exchange_rate = response['Realtime Currency Exchange Rate']['5. Exchange Rate']
    return value * float(exchange_rate)
