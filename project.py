import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    # Optional pretty table; CLI will degrade gracefully if missing
    from tabulate import tabulate  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    tabulate = None  # type: ignore


def _ensure_data_shape(obj: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Return a valid data dict regardless of input shape/errors."""
    if not isinstance(obj, dict):
        return {"transactions": []}
    txs = obj.get("transactions")
    if not isinstance(txs, list):
        return {"transactions": []}
    return {"transactions": txs}


def load_data(filename: str = "data.json") -> Dict[str, List[Dict[str, Any]]]:
    """Load data from JSON; on missing/corrupt file return empty structure.

    Returns: {"transactions": [ ... ]}
    """
    try:
        if not os.path.exists(filename):
            return {"transactions": []}
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _ensure_data_shape(data)
    except Exception:
        return {"transactions": []}


def save_data(data: Dict[str, List[Dict[str, Any]]], filename: str = "data.json") -> None:
    """Persist data dict to JSON file."""
    safe = _ensure_data_shape(data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def _next_id(transactions: List[Dict[str, Any]]) -> int:
    if not transactions:
        return 1
    return max(int(t.get("id", 0)) for t in transactions) + 1


def _validate_tx_inputs(amount: Any, category: Any, tx_type: Any) -> None:
    if not (isinstance(amount, (int, float)) or (isinstance(amount, str) and amount.strip() != "")):
        raise ValueError("amount must be a number > 0")
    try:
        amt = float(amount)
    except Exception as exc:
        raise ValueError("amount must be numeric") from exc
    if amt <= 0:
        raise ValueError("amount must be > 0")
    if not isinstance(category, str) or not category.strip():
        raise ValueError("category must be a non-empty string")
    if tx_type not in ("income", "expense"):
        raise ValueError("tx_type must be 'income' or 'expense')")


def add_transaction(
    amount: Any,
    category: str,
    tx_type: str,
    note: str = "",
    filename: str = "data.json",
) -> Dict[str, Any]:
    """Validate and append a transaction; return created transaction dict."""
    _validate_tx_inputs(amount, category, tx_type)
    amount_f = float(amount)

    data = load_data(filename)
    transactions = data.get("transactions", [])
    new_tx = {
        "id": _next_id(transactions),
        "timestamp": datetime.now().replace(microsecond=0).isoformat(),
        "amount": amount_f,
        "category": category.strip(),
        "type": tx_type,
        "note": note or "",
    }
    transactions.append(new_tx)
    save_data({"transactions": transactions}, filename)
    return new_tx


def get_balance(filename: str = "data.json") -> float:
    data = load_data(filename)
    balance = 0.0
    for t in data.get("transactions", []):
        amt = float(t.get("amount", 0) or 0)
        if t.get("type") == "income":
            balance += amt
        elif t.get("type") == "expense":
            balance -= amt
    return round(balance, 2)


def get_summary_by_category(filename: str = "data.json", tx_type: str = "expense") -> Dict[str, Any]:
    data = load_data(filename)
    txs = data.get("transactions", [])

    def summarize(kind: str) -> Dict[str, float]:
        summary: Dict[str, float] = {}
        for t in txs:
            if t.get("type") != kind:
                continue
            cat = str(t.get("category", "Uncategorized") or "Uncategorized")
            summary[cat] = round(summary.get(cat, 0.0) + float(t.get("amount", 0) or 0), 2)
        return summary

    if tx_type == "both":
        return {"income": summarize("income"), "expense": summarize("expense")}
    if tx_type not in ("income", "expense"):
        raise ValueError("tx_type must be 'income', 'expense', or 'both'")
    return summarize(tx_type)


def list_transactions(limit: Optional[int] = None, filename: str = "data.json") -> List[Dict[str, Any]]:
    data = load_data(filename)
    txs = list(data.get("transactions", []))
    if limit is not None:
        try:
            n = int(limit)
        except Exception as exc:
            raise ValueError("limit must be an integer or None") from exc
        if n < 0:
            raise ValueError("limit must be >= 0")
        txs = txs[-n:] if n > 0 else []
    return txs


def format_currency(amount: float) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(float(amount)):.2f}"


def _print_table(rows: List[List[Any]], headers: List[str]) -> None:
    if tabulate:
        print(tabulate(rows, headers=headers, tablefmt="github"))
    else:  # fallback plain table
        widths = [len(h) for h in headers]
        for row in rows:
            for i, col in enumerate(row):
                widths[i] = max(widths[i], len(str(col)))
        line = "+".join("-" * (w + 2) for w in widths)
        print(" ".join(h.ljust(w) for h, w in zip(headers, widths)))
        print(line)
        for row in rows:
            print(" ".join(str(c).ljust(w) for c, w in zip(row, widths)))


def _print_transactions_detailed(txs: List[Dict[str, Any]]) -> None:
    rows = [
        [
            t.get("id"),
            t.get("timestamp"),
            format_currency(float(t.get("amount", 0) or 0)),
            t.get("category"),
            t.get("type"),
            t.get("note", ""),
        ]
        for t in txs
    ]
    _print_table(rows, ["ID", "Timestamp", "Amount", "Category", "Type", "Note"]) if rows else print("(none)")


def main() -> None:
    filename = "data.json"
    while True:
        print("\nPersonal Expense Tracker")
        print("1) Add income")
        print("2) Add expense")
        print("3) List transactions")
        print("4) Balance")
        print("5) Summary by category")
        print("6) Quit")
        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                amt = input("Amount: ").strip()
                cat = input("Category: ").strip()
                note = input("Note (optional): ").strip()
                tx = add_transaction(amt, cat, "income", note, filename)
                print(f"Added income #{tx['id']} {format_currency(tx['amount'])} in {tx['category']}")
            elif choice == "2":
                amt = input("Amount: ").strip()
                cat = input("Category: ").strip()
                note = input("Note (optional): ").strip()
                tx = add_transaction(amt, cat, "expense", note, filename)
                print(f"Added expense #{tx['id']} {format_currency(tx['amount'])} in {tx['category']}")
            elif choice == "3":
                lim_raw = input("Limit (blank for all): ").strip()
                limit = int(lim_raw) if lim_raw else None
                txs = list_transactions(limit, filename)
                rows = [
                    [t["id"], t["timestamp"], format_currency(t["amount"]), t["category"], t["type"], t.get("note", "")]
                    for t in txs
                ]
                _print_table(rows, ["ID", "Timestamp", "Amount", "Category", "Type", "Note"])
            elif choice == "4":
                bal = get_balance(filename)
                print(f"Balance: {format_currency(bal)}")
            elif choice == "5":
                which = input("Type (income/expense/both): ").strip().lower() or "expense"
                summary = get_summary_by_category(filename, which)
                if which == "both":
                    print("Income by category:")
                    rows_i = [[k, format_currency(v)] for k, v in summary.get("income", {}).items()]
                    _print_table(rows_i, ["Category", "Total"]) if rows_i else print("(none)")
                    print("\nExpense by category:")
                    rows_e = [[k, format_currency(v)] for k, v in summary.get("expense", {}).items()]
                    _print_table(rows_e, ["Category", "Total"]) if rows_e else print("(none)")
                    data_all = list_transactions(filename=filename)
                    inc_txs = [t for t in data_all if t.get("type") == "income"]
                    exp_txs = [t for t in data_all if t.get("type") == "expense"]
                    print("\nIncome transactions:")
                    _print_transactions_detailed(inc_txs)
                    print("\nExpense transactions:")
                    _print_transactions_detailed(exp_txs)
                else:
                    rows = [[k, format_currency(v)] for k, v in summary.items()]
                    _print_table(rows, ["Category", "Total"]) if rows else print("(none)")
                    data_all = list_transactions(filename=filename)
                    kind_txs = [t for t in data_all if t.get("type") == which]
                    print("\nDetailed transactions:")
                    _print_transactions_detailed(kind_txs)
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()


