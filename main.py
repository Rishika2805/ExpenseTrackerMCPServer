from fastmcp import FastMCP
from db import execute_query

mcp = FastMCP("ExpenseTracker")


def init_db():

    execute_query("""
        CREATE TABLE IF NOT EXISTS expenses(
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            amount NUMERIC(10,2) NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
        );
    """)

    execute_query("""
        CREATE TABLE IF NOT EXISTS budgets(
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            amount NUMERIC(10,2) NOT NULL,
            month TEXT NOT NULL,
            UNIQUE(category, month)
        );
    """)



@mcp.tool()
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """
    Add a new expense.
    """

    expense = execute_query(
        """
        INSERT INTO expenses
        (date, amount, category, subcategory, note)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (date, amount, category, subcategory, note),
        fetchone=True
    )

    return {
        "success": True,
        "message": "Expense added successfully.",
        "data": expense
    }




@mcp.tool()
def list_expenses():
    """
    Return all expenses.
    """

    expenses = execute_query(
        """
        SELECT
            id,
            date,
            amount,
            category,
            subcategory,
            note
        FROM expenses
        ORDER BY id;
        """,
        fetch=True
    )

    return expenses



@mcp.tool()
def delete_expense(expense_id: int):
    """
    Delete an expense by its ID.
    """

    expense = execute_query(
        """
        DELETE FROM expenses
        WHERE id = %s
        RETURNING id;
        """,
        (expense_id,),
        fetchone=True
    )

    if expense is None:
        return {
            "success": False,
            "message": f"No expense found with ID {expense_id}."
        }

    return {
        "success": True,
        "message": f"Expense {expense_id} deleted successfully."
    }

@mcp.tool()
def update_expense(
    expense_id: int,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """
    Update an existing expense.
    """

    expense = execute_query(
        """
        UPDATE expenses
        SET
            date = %s,
            amount = %s,
            category = %s,
            subcategory = %s,
            note = %s
        WHERE id = %s
        RETURNING id;
        """,
        (
            date,
            amount,
            category,
            subcategory,
            note,
            expense_id
        ),
        fetchone=True
    )

    if expense is None:
        return {
            "success": False,
            "message": f"Expense with ID {expense_id} not found."
        }

    return {
        "success": True,
        "message": "Expense updated successfully.",
        "data": expense
    }


@mcp.tool()
def total_expenses():
    """
    Get total spending.
    """

    result = execute_query(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses;
        """,
        fetchone=True
    )

    return {
        "total_spent": float(result["total"])
    }


@mcp.tool()
def category_summary():
    """
    Show spending grouped by category.
    """

    result = execute_query(
        """
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC;
        """,
        fetch=True
    )

    return result


@mcp.tool()
def expenses_by_category(category: str):
    """
    Get all expenses for a category.
    """

    result = execute_query(
        """
        SELECT
            id,
            date,
            amount,
            category,
            subcategory,
            note
        FROM expenses
        WHERE category = %s
        ORDER BY date DESC;
        """,
        (category,),
        fetch=True
    )

    return result


@mcp.tool()
def expenses_between(start_date: str, end_date: str):
    """
    List expenses between two dates.

    Example:
        start_date = "2026-07-01"
        end_date = "2026-07-31"
    """

    expenses = execute_query(
        """
        SELECT
            id,
            date,
            amount,
            category,
            subcategory,
            note
        FROM expenses
        WHERE date BETWEEN %s AND %s
        ORDER BY date ASC;
        """,
        (start_date, end_date),
        fetch=True
    )

    return expenses

@mcp.tool()
def recent_expenses(limit: int = 5):
    """
    Return the most recent expenses.
    """

    expenses = execute_query(
        """
        SELECT
            id,
            date,
            amount,
            category,
            subcategory,
            note
        FROM expenses
        ORDER BY date DESC
        LIMIT %s;
        """,
        (limit,),
        fetch=True
    )

    return expenses


@mcp.tool()
def monthly_summary(month: str):
    """
    Return spending grouped by category for a month.

    Example:
        month = "2026-07"
    """

    summary = execute_query(
        """
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        WHERE TO_CHAR(date, 'YYYY-MM') = %s
        GROUP BY category
        ORDER BY total DESC;
        """,
        (month,),
        fetch=True
    )

    return summary


@mcp.tool()
def lowest_expense():
    """
    Return the lowest expense.
    """

    expense = execute_query(
        """
        SELECT
            id,
            date,
            amount,
            category,
            subcategory,
            note
        FROM expenses
        ORDER BY amount ASC
        LIMIT 1;
        """,
        fetchone=True
    )

    if expense is None:
        return {
            "success": False,
            "message": "No expenses found."
        }

    return expense


@mcp.tool()
def highest_expense():
    """
    Return the highest expense.
    """

    expense = execute_query(
        """
        SELECT
            id,
            date,
            amount,
            category,
            subcategory,
            note
        FROM expenses
        ORDER BY amount DESC
        LIMIT 1;
        """,
        fetchone=True
    )

    if expense is None:
        return {
            "success": False,
            "message": "No expenses found."
        }

    return expense

@mcp.tool()
def set_budget(
    category: str,
    amount: float,
    month: str
):
    """
    Set or update a monthly budget.

    Example:
        category="Food"
        amount=5000
        month="2026-07"
    """

    execute_query(
        """
        INSERT INTO budgets(category, amount, month)
        VALUES (%s, %s, %s)
        ON CONFLICT(category, month)
        DO UPDATE SET amount = EXCLUDED.amount;
        """,
        (category, amount, month)
    )

    return {
        "success": True,
        "message": f"Budget for '{category}' set to ₹{amount} for {month}."
    }

@mcp.tool()
def get_budget(month: str):
    """
    Return all budgets for a month.
    """

    budgets = execute_query(
        """
        SELECT
            category,
            amount
        FROM budgets
        WHERE month = %s
        ORDER BY category;
        """,
        (month,),
        fetch=True
    )

    return budgets



from datetime import datetime

@mcp.tool()
def remaining_budget(category: str, month: str | None = None):
    """
    Calculate remaining budget for a category.
    """

    if month is None:
        month = datetime.now().strftime("%Y-%m")

    budget = execute_query(
        """
        SELECT amount
        FROM budgets
        WHERE category = %s
        AND month = %s;
        """,
        (category, month),
        fetchone=True
    )

    if budget is None:
        return {
            "success": False,
            "message": "No budget found."
        }

    spent = execute_query(
        """
        SELECT COALESCE(SUM(amount),0) AS spent
        FROM expenses
        WHERE category = %s
        AND TO_CHAR(date, 'YYYY-MM') = %s;
        """,
        (category, month),
        fetchone=True
    )

    spent_amount = float(spent["spent"])
    budget_amount = float(budget["amount"])
    remaining = budget_amount - spent_amount

    return {
        "category": category,
        "month": month,
        "budget": budget_amount,
        "spent": spent_amount,
        "remaining": remaining,
        "used_percent": round((spent_amount / budget_amount) * 100, 2) if budget_amount else 0
    }

@mcp.tool()
def budget_status(month: str):
    """
    Return budget usage for all categories.
    """

    budgets = execute_query(
        """
        SELECT
            category,
            amount
        FROM budgets
        WHERE month = %s
        ORDER BY category;
        """,
        (month,),
        fetch=True
    )

    result = []

    for budget in budgets:

        spent = execute_query(
            """
            SELECT COALESCE(SUM(amount),0) AS spent
            FROM expenses
            WHERE category = %s
            AND TO_CHAR(date, 'YYYY-MM') = %s;
            """,
            (budget["category"], month),
            fetchone=True
        )

        spent_amount = float(spent["spent"])
        budget_amount = float(budget["amount"])
        remaining = budget_amount - spent_amount

        result.append({
            "category": budget["category"],
            "budget": budget_amount,
            "spent": spent_amount,
            "remaining": remaining,
            "used_percent": round((spent_amount / budget_amount) * 100, 2) if budget_amount else 0
        })

    return result


if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001
    )