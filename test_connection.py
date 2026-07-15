from db import execute_query

print(
    execute_query(
        "SELECT NOW() AS current_time;",
        fetchone=True
    )
)