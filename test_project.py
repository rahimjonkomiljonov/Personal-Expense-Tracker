import json
import os
import tempfile
import types

import pytest

import project as proj


def make_tmpfile() -> str:
    fd, path = tempfile.mkstemp(prefix="expense_tracker_", suffix=".json")
    os.close(fd)
    return path


def test_load_data_missing_file_returns_empty():
    tmp = make_tmpfile()
    os.remove(tmp)
    data = proj.load_data(tmp)
    assert isinstance(data, dict)
    assert data.get("transactions") == []


def test_save_and_load_roundtrip():
    tmp = make_tmpfile()
    data = {"transactions": [{"id": 1}]}
    proj.save_data(data, tmp)
    loaded = proj.load_data(tmp)
    assert loaded == data


def test_add_transaction_validations_and_creation():
    tmp = make_tmpfile()

    with pytest.raises(ValueError):
        proj.add_transaction(0, "Food", "expense", filename=tmp)
    with pytest.raises(ValueError):
        proj.add_transaction("abc", "Food", "expense", filename=tmp)
    with pytest.raises(ValueError):
        proj.add_transaction(10, "", "expense", filename=tmp)
    with pytest.raises(ValueError):
        proj.add_transaction(10, "Food", "invalid", filename=tmp)

    tx1 = proj.add_transaction(50, "Food", "expense", note="Lunch", filename=tmp)
    assert tx1["id"] == 1
    assert tx1["type"] == "expense"
    assert tx1["category"] == "Food"
    assert isinstance(tx1["timestamp"], str)

    tx2 = proj.add_transaction(100, "Salary", "income", filename=tmp)
    assert tx2["id"] == 2

    data = proj.load_data(tmp)
    assert len(data["transactions"]) == 2


def test_get_balance_and_list_and_summary():
    tmp = make_tmpfile()
    proj.add_transaction(100, "Salary", "income", filename=tmp)
    proj.add_transaction(40, "Groceries", "expense", filename=tmp)
    proj.add_transaction(10, "Coffee", "expense", filename=tmp)

    assert proj.get_balance(tmp) == 50.0

    # list all
    txs = proj.list_transactions(filename=tmp)
    assert len(txs) == 3
    # limit last 2
    txs2 = proj.list_transactions(2, filename=tmp)
    assert len(txs2) == 2
    assert txs2[0]["category"] == "Groceries"
    assert txs2[1]["category"] == "Coffee"

    # summary
    exp = proj.get_summary_by_category(tmp, "expense")
    assert exp == {"Groceries": 40.0, "Coffee": 10.0}
    inc = proj.get_summary_by_category(tmp, "income")
    assert inc == {"Salary": 100.0}
    both = proj.get_summary_by_category(tmp, "both")
    assert both == {"income": {"Salary": 100.0}, "expense": {"Groceries": 40.0, "Coffee": 10.0}}


def test_format_currency():
    assert proj.format_currency(0) == "$0.00"
    assert proj.format_currency(12.5) == "$12.50"
    assert proj.format_currency(-3.4) == "-$3.40"


