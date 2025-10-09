import psycopg2

try:
    conn = psycopg2.connect(
        "postgresql://neondb_owner:npg_7AlUWE8wkigH@ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM price_recommendations;")
    rows = cur.fetchall()
    for row in rows:
        print(row)
except psycopg2.Error as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()