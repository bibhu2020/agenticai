from typing import List
from langchain.tools import tool
from logger.decorators import log_entry
from utils.expense_calculator import Calculator

class CalculatorTool:
    """
    A wrapper class for trip-related financial calculations using a custom Calculator utility.

    This class exposes several LangChain-compatible tools for estimating hotel costs,
    calculating total expenses, and determining daily budgets.
    """

    def __init__(self):
        """
        Initialize the CalculatorTool by creating an instance of Calculator and setting up tools.
        """
        self.calculator = Calculator()
        self.calculator_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """
        Define and register calculator tools related to trip planning.

        Returns:
            List: A list of LangChain tool functions for financial calculations.
        """

        @tool
        @log_entry
        def estimate_total_hotel_cost(price_per_night: str, total_days: float) -> float:
            """
            Estimate the total hotel cost for a trip.

            Args:
                price_per_night (str): Cost per night for the hotel stay (may include currency symbol).
                total_days (float): Number of nights staying at the hotel.

            Returns:
                float: Total cost for the hotel stay.
            """
            print('Entered into estimate_total_hotel_cost().')
            return self.calculator.multiply(price_per_night, total_days)

        @tool
        @log_entry
        def calculate_total_expense(*costs: float) -> float:
            """
            Calculate the total trip expense by summing up individual cost items.

            Args:
                *costs (float): A variable number of expense values (e.g., hotel, food, transport).

            Returns:
                float: The total combined expense.
            """
            print('Entered into calculate_total_expense().')
            return self.calculator.calculate_total(*costs)

        @tool
        @log_entry
        def calculate_daily_expense_budget(total_cost: float, days: int) -> float:
            """
            Calculate the average daily budget for the trip.

            Args:
                total_cost (float): Total trip cost.
                days (int): Number of days in the trip.

            Returns:
                float: Estimated daily budget.
            """
            print('Entered into calculate_daily_expense_budget().')
            return self.calculator.calculate_daily_budget(total_cost, days)

        return [estimate_total_hotel_cost, calculate_total_expense, calculate_daily_expense_budget]
