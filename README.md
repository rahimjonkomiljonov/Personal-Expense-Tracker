## Personal Expense Tracker (CLI)

Command-line program to record income and expenses, categorize them, track a running balance, and view summaries by category. Data is persisted to a local JSON file so transactions are remembered between runs.

### Project structure

```
expense-tracker/
├─ project.py        # main program + functions
├─ test_project.py   # pytest tests
├─ requirements.txt  # dependencies (tabulate, pytest)
└─ data.json         # created at runtime (default)
```

### Requirements

- Python 3.8+
- `pip install -r requirements.txt`
  - `tabulate` is used to render pretty tables in the CLI (falls back to plain text if missing)
  - `pytest` is used for tests

### Quick start

```bash
pip install -r requirements.txt
python project.py
```

### Usage

When you run `python project.py` you will see a menu:

- 1) Add income
- 2) Add expense
- 3) List transactions
- 4) Balance
- 5) Summary by category
- 6) Quit

Details:

- Add income/expense: prompts for amount, category, and optional note. Validates input and saves to `data.json`.
- List transactions: shows ID, timestamp, amount, category, type, and note. Optional limit shows the last N transactions.
- Balance: shows total income minus total expenses.
- Summary by category: choose `income`, `expense`, or `both`. Totals are shown first, then detailed transactions are printed automatically.

### Data format (JSON)

File: `data.json` (created automatically)

```json
{
  "transactions": [
    {
      "id": 1,
      "timestamp": "2025-10-05T20:15:30",
      "amount": 100.0,
      "category": "Salary",
      "type": "income",
      "note": ""
    }
  ]
}
```

- `id` is auto-incremented.
- `type` is `income` or `expense`.
- `amount` stored as number (float).

### Running tests

```bash
pytest -q
```

### Advanced: alternate data file

All top-level functions accept an optional `filename` parameter. The CLI uses the default `data.json`. For scripts or tests you can pass a different path, e.g.:

```python
import project as proj
proj.add_transaction(25, "Snacks", "expense", filename="/tmp/mydata.json")
```

### Notes

- Timestamps are saved to second precision using local time (`datetime.now().isoformat()`).
- If `data.json` is missing or corrupted, the app safely starts with an empty dataset.


