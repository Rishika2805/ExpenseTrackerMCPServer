from fastmcp import FastMCP
import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), 'categories.json')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

mcp = FastMCP('ExpenseTracker')

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,   
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        ''')    
    
init_db()

@mcp.tool()
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""):
    """
      Add a new expense to the SQLite database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            '''INSERT INTO expenses (date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)''',
            (date, amount, category, subcategory, note)
        )
        return {'Status' : 'ok' , 'id' : cur.lastrowid}




@mcp.tool()
def list_expenses() -> list:
    """
    List all expense entries from the database
    """
    with get_connection() as conn:
        cur = conn.execute(
            '''SELECT id, date, amount, category, subcategory, note FROM expenses ORDER BY id ASC'''
        )
        return [dict(row) for row in cur.fetchall()]



@mcp.tool()
def delete_expense(id: int):
    """
    Delete an expense by its ID.
    """
    with get_connection() as conn:
        cur = conn.execute(
            '''DELETE FROM expenses WHERE id = ?''',
            (id,)
        )

        if cur.rowcount == 0:
            return {
                'Status' : 'error',
                'message' : f'No expense with that ID was found {id}.'
            }

        return {
            'Status' : 'success',
            'message' : f'Successfully deleted expense with ID {id}.'
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
    Update an expense
    """
    with get_connection() as conn:
        cur = conn.execute(
            '''UPDATE expenses 
            SET 
                date = ?,
                amount = ?,
                category = ?,
                subcategory = ?, 
                note = ?
            WHERE id = ?''',
            (
                date,
                amount,
                category,
                subcategory,
                note,
                expense_id
            )
        )

        if cur.rowcount == 0:
            return {
                'Status' : 'error',
                'message' : f'Expense not found.'
            }

        return {
            'Status' : 'success',
            'message' : f'Successfully updated Expense.'
        }


@mcp.tool()
def total_expenses():
    """
    Get total spending.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT SUM(amount) AS total 
            FROM expenses """
        )

        total = cur.fetchone()['total']
        return {
            'total_spent' : total if total else 0,
        }


@mcp.tool()
def category_summary():
    """
    Show Spending Grouped by category.
    """

    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT 
            category,
            SUM(amount) AS total
            FROM expenses 
            GROUP BY category
            ORDER BY total DESC
            """
        )

        return [dict(row) for row in cur.fetchall()]


@mcp.tool()
def expenses_by_category(category: str):
    """
    Get all expenses for a category.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM expenses
            WHERE category = ?
            ORDER BY date DESC
            """,
            (category,)
        )

        return [dict(row) for row in cur.fetchall()]


@mcp.tool()
def expenses_between(strat_date: str,end_date:str):
    """
    List Expenses between two dates.
    """

    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT * 
            FROM expenses 
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC""",
            (strat_date,end_date)
        )

        return [dict(row) for row in cur.fetchall()]

@mcp.tool()
def recent_expenses(limit : int = 5):
    """
    Get recent expenses.
    """

    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT * 
            FROM expenses 
            ORDER BY date DESC LIMIT ?""",
            (limit,)
        )

        return [dict(row) for row in cur.fetchall()]


@mcp.tool()
def monthly_summary(month: str):
    """
    Example:
    month = '2026-07'
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT
                category,
                SUM(amount) AS total
            FROM expenses
            WHERE substr(date,1,7)=?
            GROUP BY category
            ORDER BY total DESC
            """,
            (month,)
        )

        return [dict(row) for row in cur.fetchall()]


@mcp.tool()
def lowest_expense():
    """
    Return the lowest expense.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM expenses
            ORDER BY amount ASC
            LIMIT 1
            """
        )

        row = cur.fetchone()

        if row is None:
            return {
                "message": "No expenses found."
            }

        return dict(row)

@mcp.tool()
def highest_expense():
    """
    Return the highest expense.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM expenses
            ORDER BY amount DESC
            LIMIT 1
            """
        )

        row = cur.fetchone()

        if row is None:
            return {
                "message": "No expenses found."
            }

        return dict(row)

if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )