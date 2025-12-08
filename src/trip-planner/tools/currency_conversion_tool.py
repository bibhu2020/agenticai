import os
from typing import List
from dotenv import load_dotenv
from langchain.tools import tool
from logger.decorators import log_entry
from utils.currency_converter import CurrencyConverter

class CurrencyConverterTool:
    """
    A wrapper class that defines a LangChain-compatible tool for converting currencies
    using a custom CurrencyConverter service.

    Attributes:
        api_key (str): API key for the currency conversion service.
        currency_service (CurrencyConverter): Instance of the currency conversion service.
        currency_converter_tool_list (List): List of registered LangChain tools.
    """

    def __init__(self):
        """
        Initialize the CurrencyConverterTool with API credentials and tool setup.
        """
        load_dotenv()
        self.api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
        self.currency_service = CurrencyConverter(self.api_key)
        self.currency_converter_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """
        Define and register the currency conversion tool.

        Returns:
            List: A list containing the currency conversion tool function.
        """

        @tool
        @log_entry
        def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
            """
            Convert an amount from one currency to another using real-time exchange rates.

            Args:
                amount (float): The amount of money to convert.
                from_currency (str): The currency code to convert from (e.g., "USD").
                to_currency (str): The currency code to convert to (e.g., "EUR").

            Returns:
                float: The equivalent amount in the target currency.
            """
            print('Entered into convert_currency().')
            return self.currency_service.convert(amount, from_currency, to_currency)

        return [convert_currency]
