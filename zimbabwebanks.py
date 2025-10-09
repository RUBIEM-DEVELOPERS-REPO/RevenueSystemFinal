import psycopg2

# Establish a connection to the PostgreSQL database
def create_connection():
    try:
        conn = psycopg2.connect(
            dbname="zimbabwe_banks",
            user="bankuser",
            password="Test123",
            host="localhost",
            port="5433"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Create tables
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banks (
            bank_id SERIAL PRIMARY KEY,
            bank_name VARCHAR(255) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_types (
            transaction_type_id SERIAL PRIMARY KEY,
            transaction_type_name VARCHAR(255) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS currencies (
            currency_id SERIAL PRIMARY KEY,
            currency_code VARCHAR(10) NOT NULL,
            currency_name VARCHAR(255) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS charges (
            charge_id SERIAL PRIMARY KEY,
            bank_id INTEGER NOT NULL,
            transaction_type_id INTEGER NOT NULL,
            currency_id INTEGER NOT NULL,
            charge_type VARCHAR(255) NOT NULL,
            charge_range_min NUMERIC(10, 2),
            charge_range_max NUMERIC(10, 2),
            charge_amount NUMERIC(10, 2),
            charge_percentage NUMERIC(5, 2),
            FOREIGN KEY (bank_id) REFERENCES banks (bank_id),
            FOREIGN KEY (transaction_type_id) REFERENCES transaction_types (transaction_type_id),
            FOREIGN KEY (currency_id) REFERENCES currencies (currency_id)
        )
    ''')
    conn.commit()
# Create tables

# Insert sample data
def insert_data(conn):
    cursor = conn.cursor()
    banks = [
        ('CBZ',),
        ('ZB',),
        ('FBC',),
        ('NMB',),
        ('Steward',),
        ('AFC',),
        ('Stanbic',)
    ]

    transaction_types = [
        ('Internal Transfers',),
        ('RTGS Transfers',),
        ('International Payments',),
        ('ATM Withdrawals',),
        ('Account Management',),
        ('Smile Cash',),
        ('Smile & Pay',),
        ('MyZB',),
        ('Local Payments',),
    ]

    currencies = [
        ('ZWL', 'Zimbabwean Dollar'),
        ('USD', 'United States Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'Pound Sterling'),
        ('ZAR', 'South African Rand'),
        ('ZiG', 'Zimbabwe Gold'),
    ]

    # Insert banks
    cursor.executemany('INSERT INTO banks (bank_name) VALUES (%s)', banks)

    # Get bank ids
    cursor.execute('SELECT bank_id FROM banks')
    bank_ids = [row[0] for row in cursor.fetchall()]

    # Insert transaction types
    cursor.executemany('INSERT INTO transaction_types (transaction_type_name) VALUES (%s)', transaction_types)

    # Get transaction type ids
    cursor.execute('SELECT transaction_type_id FROM transaction_types')
    transaction_type_ids = [row[0] for row in cursor.fetchall()]

    # Insert currencies
    cursor.executemany('INSERT INTO currencies (currency_code, currency_name) VALUES (%s, %s)', currencies)

    # Get currency ids
    cursor.execute('SELECT currency_id FROM currencies')
    currency_ids = [row[0] for row in cursor.fetchall()]

    # Insert charges for each bank
    charges = [
        # AFC
        (bank_ids[5], transaction_type_ids[3], currency_ids[1], 'ATM Withdrawal Fee', None, None, None, 2.5),
        (bank_ids[5], transaction_type_ids[2], currency_ids[1], 'International Visa Charges', None, None, None, 1.75),
        (bank_ids[5], transaction_type_ids[4], currency_ids[1], 'Account Maintenance Fee', None, None, 5.00, None),
        (bank_ids[5], transaction_type_ids[1], currency_ids[1], 'RTGS Transfer Charges', None, None, None, 2.00),

        # Stanbic
        (bank_ids[6], transaction_type_ids[3], currency_ids[1], 'ATM Withdrawal Fee', None, None, None, 2.00),
        (bank_ids[6], transaction_type_ids[2], currency_ids[1], 'International Visa Charges', None, None, None, 1.75),
        (bank_ids[6], transaction_type_ids[4], currency_ids[1], 'Account Maintenance Fee', None, None, 5.00, None),
        (bank_ids[6], transaction_type_ids[1], currency_ids[1], 'RTGS Transfer Charges', None, None, None, 2.00),
    ]

    cursor.executemany('''
        INSERT INTO charges (bank_id, transaction_type_id, currency_id, charge_type, charge_range_min, charge_range_max, charge_amount, charge_percentage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', charges)

    conn.commit()

# Main function
def main():
    conn = create_connection()
    if conn:
        create_tables(conn)
        insert_data(conn)
        conn.close()

if __name__ == "__main__":
    main()
    print("Data inserted successfully.")