import psycopg2
conn = psycopg2.connect("postgresql://postgres.axxctjmyrjbprqquvqks:GHCSDmFVYsB05MFw@aws-1-ap-south-1.pooler.supabase.com:5432/postgres", connect_timeout=10)
print("Connected!")
conn.close()