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
    Add a new expense record to the expense tracker.

    Use this tool ONLY when the user wants to:
    - Add a new expense
    - Record a purchase
    - Log spending
    - Save an expense
    - Track money spent

    Examples:
    - "I spent ₹500 on food."
    - "Add ₹250 for coffee."
    - "Log an expense of ₹1200 for groceries."
    - "Record ₹800 spent on petrol."

    Required:
    - date
    - amount
    - category

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
    Return every expense stored in the database.

    Use this tool when the user asks:
    - Show all expenses
    - List my expenses
    - Display all transactions
    - View expense history
    - Show everything I have spent

    Do NOT use for recent expenses, category summaries, budgets, or analytics.
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
    Delete an expense using its expense ID.

    Use this tool ONLY when the user explicitly wants to remove an expense.

    Examples:
    - Delete expense 4
    - Remove expense ID 7
    - Delete transaction 12

    Requires:
    - expense_id

    Never use this tool for updates or analytics.
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

    Use this tool when the user wants to modify:
    - amount
    - date
    - category
    - subcategory
    - note

    Examples:
    - Change expense 5 to ₹600
    - Update expense 3
    - Edit my grocery expense

    Requires:
    - expense_id
    - updated values

    Never use this tool to add or delete expenses.
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
    Calculate the total amount spent across all recorded expenses.

    Use this tool when the user asks:
    - Total expenses
    - Total spending
    - How much have I spent?
    - Total money spent

    Do NOT use for category summaries or highest/lowest expenses.
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
    Calculate total spending grouped by category.

    Use ONLY when the user wants spending grouped by categories.

    Examples:
    - Show spending by category
    - Category-wise summary
    - Where did I spend my money?
    - Show category breakdown
    - Spending distribution

    Returns:
    Each category and its total spending.

    Do NOT use for:
    - Highest expense
    - Lowest expense
    - Monthly totals
    - Total spending
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
    Return every expense belonging to one specific category.

    Use when the user asks:
    - Show food expenses
    - List grocery expenses
    - Show travel expenses
    - Expenses for coffee

    Requires:
    - category

    Returns individual expense records.

    Do NOT use for grouped summaries.
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
    Return every expense recorded between two dates.

    Use when the user asks:
    - Expenses this week
    - Expenses last month
    - Expenses between two dates
    - Transactions from July

    Requires:
    - start_date
    - end_date

    Returns every matching expense.
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

    Use when the user asks:
    - Recent expenses
    - Latest transactions
    - Last few expenses
    - Most recent spending

    Optional:
    - limit

    Do NOT use for complete history.
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
    Return spending grouped by category for one month.

    Use ONLY when the user asks:
    - Monthly summary
    - Spending this month
    - July summary
    - Monthly spending breakdown

    Requires:
    - month

    Returns category totals for that month.

    Do NOT use for highest or lowest expense.
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
    Return the single expense with the smallest amount.

    Use ONLY when the user asks:
    - Lowest expense
    - Cheapest purchase
    - Smallest expense
    - Least expensive transaction
    - What did I spend the least on?

    Returns one expense record.

    Never use for category summaries.
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
    Return the single expense with the largest amount.

    Use ONLY when the user asks:
    - Highest expense
    - Biggest purchase
    - Largest expense
    - Most expensive transaction
    - What did I spend the most on?

    Returns one expense record.

    Never use for category summaries.
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
    Create or update a monthly budget for one category.

    Use when the user wants to:
    - Set a budget
    - Create a budget
    - Update a budget
    - Change budget amount

    Examples:
    - Set food budget to ₹5000
    - Set travel budget to ₹3000

    Requires:
    - category
    - amount
    - month

    Never use for retrieving budgets.
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
    Return every budget for a specific month.

    Use when the user asks:
    - Show my budgets
    - List budgets
    - View monthly budgets
    - Budget for this month

    Requires:
    - month

    Returns all categories and their budgets.

    Do NOT calculate remaining budget.
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
    Calculate remaining budget for one category.

    Use when the user asks:
    - Budget left
    - Remaining budget
    - How much budget is left?
    - Remaining money in food budget

    Requires:
    - category

    Optional:
    - month

    Returns:
    - Budget
    - Spent
    - Remaining
    - Usage percentage

    Do NOT use for listing all budgets.
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
    Return budget usage for every category.

    Use when the user asks:
    - Budget status
    - Budget report
    - Budget overview
    - Show budget utilization
    - Compare spending against budgets

    Requires:
    - month

    Returns:
    - Budget
    - Spent
    - Remaining
    - Percentage used

    Do NOT use for one specific category.
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

@mcp.tool()
def test_db():
    try:
        result = execute_query(
            "SELECT NOW() as current_time;",
            fetchone=True
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "error": repr(e),
            "args": e.args,
            "type": type(e).__name__
        }

if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001
    )