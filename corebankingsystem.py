# migrate_simple.py
import psycopg2
import subprocess
import os

# Your Neon connection string
NEON_CONNECTION = "postgresql://neondb_owner:npg_XCO6HPNfw7El@ep-frosty-dawn-ad0cnbjn-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def run_command(command, env=None):
    """Run a command and return success"""
    try:
        subprocess.run(command, shell=True, check=True, env=env)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        return False

print("🚀 Starting migration...")

# Step 1: Backup both databases
print("1. Backing up local databases...")

# Backup dummydb
os.environ['PGPASSWORD'] = 'Test123'
if run_command('pg_dump -h localhost -p 5433 -U dummydata -d dummydb -f dummydb_backup.sql'):
    print("✅ dummydb backed up")

# Backup core_banking_system  
if run_command('pg_dump -h localhost -p 5433 -U bankuser -d core_banking_system -f core_banking_backup.sql'):
    print("✅ core_banking_system backed up")

# Step 2: Restore to Neon
print("2. Migrating to Neon...")

if run_command(f'psql "{NEON_CONNECTION}" -f dummydb_backup.sql'):
    print("✅ dummydb migrated to Neon")

if run_command(f'psql "{NEON_CONNECTION}" -f core_banking_backup.sql'):
    print("✅ core_banking_system migrated to Neon")

print("🎉 Migration completed! Both databases are now in Neon.")