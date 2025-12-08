# tests/test_memory_manager.py

import os
import pytest
from core.memory_manager import MemoryManager

@pytest.fixture
def memory_manager(tmp_path):
    # Use a temporary file for testing
    cache_file = tmp_path / "test_cache.json"
    manager = MemoryManager(cache_file=str(cache_file))
    return manager

def test_save_and_get_analysis(memory_manager):
    symbol = "AAPL"
    analysis = {"signal": "Buy", "latest_price": 150.0}
    
    # Save analysis
    memory_manager.save_analysis(symbol, analysis)
    
    # Retrieve analysis
    retrieved = memory_manager.get_analysis(symbol)
    assert retrieved == analysis

def test_get_analysis_nonexistent(memory_manager):
    assert memory_manager.get_analysis("MSFT") is None

def test_save_and_get_portfolio(memory_manager):
    portfolio_data = {"positions": {"AAPL": 10, "GOOGL": 5}, "total_value": 2000.0}
    
    memory_manager.save_portfolio(portfolio_data)
    
    retrieved = memory_manager.get_portfolio()
    assert retrieved == portfolio_data

def test_clear_cache(memory_manager):
    memory_manager.save_analysis("AAPL", {"signal": "Buy"})
    memory_manager.save_portfolio({"total_value": 1000})
    
    memory_manager.clear_cache()
    
    assert memory_manager.get_analysis("AAPL") is None
    assert memory_manager.get_portfolio() is None

def test_persistence(tmp_path):
    cache_file = tmp_path / "persistent_cache.json"
    
    # Save data
    manager1 = MemoryManager(str(cache_file))
    manager1.save_analysis("AAPL", {"signal": "Sell"})
    manager1.save_portfolio({"total_value": 5000})
    
    # Load again from the same file
    manager2 = MemoryManager(str(cache_file))
    assert manager2.get_analysis("AAPL") == {"signal": "Sell"}
    assert manager2.get_portfolio() == {"total_value": 5000}
