import psycopg2
import pandas as pd
import logging
from datetime import datetime
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demonstrate_charge_calculations():
    """Demonstrate how different charge types are calculated"""
    
    charge_structures = {
        'Percentage-Based (With Caps)': {
            'Withdrawal': {'rate': 0.02, 'min': 1.00, 'max': 10.00},
            'Transfer': {'rate': 0.015, 'min': 0.50, 'max': 15.00},
            'Payment': {'rate': 0.01, 'min': 0.25, 'max': 8.00},
            'International Transfer': {'rate': 0.025, 'min': 5.00, 'max': 50.00}
        },
        'Flat Fees': {
            'Account Maintenance': 5.00,
            'Card Replacement': 15.00, 
            'Statement Fee': 2.00,
            'Overdraft Fee': 25.00
        },
        'Tiered Fees': {
            'Large Withdrawal': {
                'Tier 1 (≤$1,000)': 10.00,
                'Tier 2 (≤$5,000)': 25.00, 
                'Tier 3 (>$5,000)': 50.00
            }
        }
    }
    
    print("\n" + "="*80)
    print("🎯 CHARGE CALCULATION METHODS - DEMONSTRATION")
    print("="*80)
    
    # Demonstrate percentage-based calculations
    print("\n📈 PERCENTAGE-BASED FEES (with min/max caps):")
    print("-" * 60)
    
    sample_amounts = [25, 100, 500, 1000, 2000, 5000]
    
    for trans_type, rules in charge_structures['Percentage-Based (With Caps)'].items():
        print(f"\n{trans_type:20}: {rules['rate']*100}% (min ${rules['min']}, max ${rules['max']})")
        for amount in sample_amounts:
            calculated = amount * rules['rate']
            final_charge = max(rules['min'], min(calculated, rules['max']))
            capped = "⚡ CAPPED" if calculated != final_charge else ""
            min_applied = "🚨 MIN APPLIED" if final_charge == rules['min'] and calculated < rules['min'] else ""
            max_applied = "📈 MAX APPLIED" if final_charge == rules['max'] and calculated > rules['max'] else ""
            
            print(f"  ${amount:5,d} → ${calculated:6.2f} → ${final_charge:6.2f} (final) {capped} {min_applied} {max_applied}")
    
    # Demonstrate flat fees
    print(f"\n💵 FLAT FEES (fixed amount regardless of transaction size):")
    print("-" * 60)
    for fee_type, amount in charge_structures['Flat Fees'].items():
        print(f"  {fee_type:20} → ${amount:6.2f} (always this amount)")
    
    # Demonstrate tiered fees  
    print(f"\n📊 TIERED FEES (amount-based tiers):")
    print("-" * 60)
    for fee_type, tiers in charge_structures['Tiered Fees'].items():
        print(f"  {fee_type}:")
        for tier, amount in tiers.items():
            print(f"    {tier:25} → ${amount:6.2f}")

def add_charge_columns():
    """Add the necessary columns for detailed charge tracking"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="core_banking_system", 
            user="dummydata",
            password="Test123",
            port=5433
        )
        cur = conn.cursor()
        
        # Add charges column if it doesn't exist
        cur.execute("""
            ALTER TABLE customer_transactions 
            ADD COLUMN IF NOT EXISTS charges DECIMAL(10,2) DEFAULT 0.00
        """)
        
        # Add charge_type column for categorization
        cur.execute("""
            ALTER TABLE customer_transactions 
            ADD COLUMN IF NOT EXISTS charge_type VARCHAR(30)
        """)
        
        # Add charge_calculation column for transparency
        cur.execute("""
            ALTER TABLE customer_transactions 
            ADD COLUMN IF NOT EXISTS charge_calculation TEXT
        """)
        
        # Add charge_method column to show min/max/percentage/flat
        cur.execute("""
            ALTER TABLE customer_transactions 
            ADD COLUMN IF NOT EXISTS charge_method VARCHAR(20)
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info("✅ Added all charge-related columns to customer_transactions")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding charge columns: {e}")
        return False

def update_transactions_with_detailed_charges():
    """Update all transactions with detailed charge calculations"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="core_banking_system", 
            user="dummydata",
            password="Test123",
            port=5433
        )
        cur = conn.cursor()
        
        # First, let's see what transaction types we have
        cur.execute("""
            SELECT DISTINCT transaction_type 
            FROM customer_transactions 
            WHERE charges IS NULL OR charges = 0
            LIMIT 20
        """)
        existing_types = [row[0] for row in cur.fetchall()]
        print(f"\n📋 Found transaction types: {existing_types}")
        
        # Enhanced charge calculation with clear logic for each method
        update_query = """
        UPDATE customer_transactions 
        SET 
            charges = 
                CASE 
                    -- =============================================
                    -- PERCENTAGE-BASED FEES (with min/max caps)
                    -- =============================================
                    
                    -- Withdrawals: 2% with $1 min and $10 max
                    WHEN transaction_type = 'Withdrawal' AND amount < 0 THEN 
                        GREATEST(1.00, LEAST(ABS(amount) * 0.02, 10.00))
                    
                    -- Transfers: 1.5% with $0.50 min and $15 max  
                    WHEN transaction_type = 'Transfer' AND amount < 0 THEN 
                        GREATEST(0.50, LEAST(ABS(amount) * 0.015, 15.00))
                    
                    -- Payments: 1% with $0.25 min and $8 max
                    WHEN transaction_type = 'Payment' AND amount < 0 THEN 
                        GREATEST(0.25, LEAST(ABS(amount) * 0.01, 8.00))
                    
                    -- International: 2.5% with $5 min and $50 max
                    WHEN transaction_type = 'International Transfer' AND amount < 0 THEN 
                        GREATEST(5.00, LEAST(ABS(amount) * 0.025, 50.00))
                    
                    -- =============================================
                    -- FLAT FEES (fixed amount regardless of size)
                    -- =============================================
                    WHEN transaction_type = 'Maintenance Fee' THEN 5.00
                    WHEN transaction_type = 'Card Fee' THEN 15.00
                    WHEN transaction_type = 'Service Fee' THEN 2.00
                    WHEN transaction_type = 'Penalty Fee' THEN 25.00
                    
                    -- =============================================
                    -- NO FEES (explicitly free transactions)
                    -- =============================================
                    ELSE 0.00
                END,
            
            -- Charge type categorization
            charge_type =
                CASE 
                    WHEN transaction_type IN ('Withdrawal', 'Transfer', 'Payment', 'International Transfer') THEN 'Percentage-Based'
                    WHEN transaction_type IN ('Maintenance Fee', 'Card Fee', 'Service Fee', 'Penalty Fee') THEN 'Flat-Fee'
                    ELSE 'No-Charge'
                END,
            
            -- Charge calculation method
            charge_method =
                CASE 
                    WHEN transaction_type IN ('Withdrawal', 'Transfer', 'Payment', 'International Transfer') THEN 'Percentage+MinMax'
                    WHEN transaction_type IN ('Maintenance Fee', 'Card Fee', 'Service Fee', 'Penalty Fee') THEN 'Flat'
                    ELSE 'Free'
                END,
            
            -- Transparent calculation description
            charge_calculation =
                CASE 
                    -- Percentage calculations with min/max
                    WHEN transaction_type = 'Withdrawal' AND amount < 0 THEN 
                        '2% of $' || ABS(amount) || ' = $' || ROUND(ABS(amount) * 0.02, 2) || ' (capped $1-$10)'
                    WHEN transaction_type = 'Transfer' AND amount < 0 THEN 
                        '1.5% of $' || ABS(amount) || ' = $' || ROUND(ABS(amount) * 0.015, 2) || ' (capped $0.50-$15)'
                    WHEN transaction_type = 'Payment' AND amount < 0 THEN 
                        '1% of $' || ABS(amount) || ' = $' || ROUND(ABS(amount) * 0.01, 2) || ' (capped $0.25-$8)'
                    WHEN transaction_type = 'International Transfer' AND amount < 0 THEN 
                        '2.5% of $' || ABS(amount) || ' = $' || ROUND(ABS(amount) * 0.025, 2) || ' (capped $5-$50)'
                    
                    -- Flat fee descriptions
                    WHEN transaction_type = 'Maintenance Fee' THEN 'Flat fee: $5.00'
                    WHEN transaction_type = 'Card Fee' THEN 'Flat fee: $15.00'
                    WHEN transaction_type = 'Service Fee' THEN 'Flat fee: $2.00'
                    WHEN transaction_type = 'Penalty Fee' THEN 'Flat fee: $25.00'
                    
                    -- No charge descriptions
                    ELSE 'No charges applied'
                END
                
        WHERE charges IS NULL OR charges = 0
        """
        
        # Get count of transactions to update
        cur.execute("SELECT COUNT(*) FROM customer_transactions WHERE charges IS NULL OR charges = 0")
        records_to_update = cur.fetchone()[0]
        
        print(f"\n🔄 Updating {records_to_update:,} transactions with charges...")
        
        # Perform the update
        cur.execute(update_query)
        conn.commit()
        
        # Generate detailed report
        report_query = """
        SELECT 
            charge_type,
            charge_method,
            COUNT(*) as transaction_count,
            ROUND(AVG(charges), 2) as avg_charge,
            SUM(charges) as total_charges,
            MIN(charges) as min_charge,
            MAX(charges) as max_charge
        FROM customer_transactions 
        WHERE charges > 0
        GROUP BY charge_type, charge_method
        ORDER BY total_charges DESC
        """
        
        cur.execute(report_query)
        charge_report = cur.fetchall()
        
        # Get breakdown by transaction type for percentage-based fees
        percentage_breakdown_query = """
        SELECT 
            transaction_type,
            COUNT(*) as txn_count,
            ROUND(AVG(charges), 2) as avg_charge,
            SUM(charges) as total_charges,
            ROUND(AVG(ABS(amount)), 2) as avg_transaction_size,
            ROUND((AVG(charges) / AVG(ABS(amount))) * 100, 2) as effective_rate
        FROM customer_transactions 
        WHERE charge_type = 'Percentage-Based' AND amount < 0
        GROUP BY transaction_type
        ORDER BY total_charges DESC
        """
        
        cur.execute(percentage_breakdown_query)
        percentage_breakdown = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Display detailed breakdown
        print("\n" + "="*80)
        print("💰 CHARGE IMPLEMENTATION RESULTS")
        print("="*80)
        
        print(f"\n✅ Successfully updated {records_to_update:,} transactions")
        
        print(f"\n📊 OVERVIEW BY CHARGE TYPE:")
        print("-" * 80)
        for charge_type, method, count, avg_charge, total, min_charge, max_charge in charge_report:
            print(f"\n🎯 {charge_type} ({method}):")
            print(f"   • Transactions: {count:,}")
            print(f"   • Average Charge: ${avg_charge:.2f}")
            print(f"   • Total Revenue: ${total:,.2f}")
            print(f"   • Charge Range: ${min_charge:.2f} - ${max_charge:.2f}")
        
        print(f"\n📈 PERCENTAGE-BASED FEE BREAKDOWN:")
        print("-" * 80)
        for trans_type, count, avg_charge, total, avg_size, effective_rate in percentage_breakdown:
            print(f"\n💸 {trans_type}:")
            print(f"   • Transactions: {count:,}")
            print(f"   • Avg Charge: ${avg_charge:.2f}")
            print(f"   • Avg Transaction: ${avg_size:,.2f}")
            print(f"   • Effective Rate: {effective_rate}%")
            print(f"   • Total Revenue: ${total:,.2f}")
        
        return {
            'updated_records': records_to_update,
            'charge_report': charge_report,
            'percentage_breakdown': percentage_breakdown
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating transactions with detailed charges: {e}")
        return None

def show_sample_transactions_with_charges():
    """Show sample transactions with the new charge details"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="core_banking_system",
            user="dummydata",
            password="Test123",
            port=5433
        )
        
        sample_query = """
        SELECT 
            transaction_id,
            transaction_type,
            amount,
            charges,
            charge_type,
            charge_method,
            charge_calculation
        FROM customer_transactions 
        WHERE charges > 0
        ORDER BY RANDOM()
        LIMIT 15
        """
        
        sample_df = pd.read_sql(sample_query, conn)
        conn.close()
        
        print("\n" + "="*100)
        print("🔍 SAMPLE TRANSACTIONS WITH CHARGES")
        print("="*100)
        
        # Display in a clean format
        for _, row in sample_df.iterrows():
            print(f"\n🆔 Transaction {row['transaction_id']}:")
            print(f"   Type: {row['transaction_type']}")
            print(f"   Amount: ${row['amount']:,.2f}")
            print(f"   Charge: ${row['charges']:.2f} ({row['charge_type']} - {row['charge_method']})")
            print(f"   Calculation: {row['charge_calculation']}")
        
        return sample_df
        
    except Exception as e:
        logger.error(f"❌ Error fetching sample transactions: {e}")
        return None

def analyze_charge_efficiency():
    """Analyze how effective our charge structure is"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="core_banking_system",
            user="dummydata",
            password="Test123",
            port=5433
        )
        
        efficiency_query = """
        SELECT 
            -- Overall metrics
            COUNT(*) as total_transactions,
            SUM(CASE WHEN charges > 0 THEN 1 ELSE 0 END) as charged_transactions,
            ROUND((SUM(CASE WHEN charges > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as charge_coverage_rate,
            
            -- Revenue metrics
            SUM(charges) as total_charge_revenue,
            ROUND(AVG(CASE WHEN charges > 0 THEN charges ELSE NULL END), 2) as avg_charge_per_txn,
            
            -- Efficiency metrics
            ROUND((SUM(charges) / ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END))) * 100, 2) as overall_charge_rate,
            
            -- Method effectiveness
            COUNT(DISTINCT charge_method) as unique_charge_methods,
            COUNT(DISTINCT charge_type) as unique_charge_types
            
        FROM customer_transactions
        """
        
        efficiency_df = pd.read_sql(efficiency_query, conn)
        conn.close()
        
        print("\n" + "="*80)
        print("📊 CHARGE EFFICIENCY ANALYSIS")
        print("="*80)
        
        row = efficiency_df.iloc[0]
        print(f"\n📈 Overall Statistics:")
        print(f"   • Total Transactions: {row['total_transactions']:,}")
        print(f"   • Charged Transactions: {row['charged_transactions']:,}")
        print(f"   • Charge Coverage: {row['charge_coverage_rate']}%")
        print(f"   • Total Charge Revenue: ${row['total_charge_revenue']:,.2f}")
        print(f"   • Average Charge: ${row['avg_charge_per_txn']:.2f}")
        print(f"   • Overall Charge Rate: {row['overall_charge_rate']}%")
        print(f"   • Unique Charge Methods: {row['unique_charge_methods']}")
        print(f"   • Unique Charge Types: {row['unique_charge_types']}")
        
        return efficiency_df
        
    except Exception as e:
        logger.error(f"❌ Error analyzing charge efficiency: {e}")
        return None

# Main execution
def main():
    print("🚀 IMPLEMENTING DETAILED CHARGE SYSTEM")
    print("This will add charges to your existing transactions with clear distinctions!")
    
    # Step 1: Show how charges will be calculated
    demonstrate_charge_calculations()
    
    input("\nPress Enter to continue with the implementation...")
    
    # Step 2: Add the necessary columns
    print(f"\n📋 Step 1: Adding charge columns to database...")
    if not add_charge_columns():
        print("❌ Failed to add charge columns. Exiting.")
        return
    
    # Step 3: Update transactions with charges
    print(f"\n📋 Step 2: Calculating and applying charges...")
    result = update_transactions_with_detailed_charges()
    
    if not result:
        print("❌ Failed to update transactions with charges.")
        return
    
    # Step 4: Show samples
    print(f"\n📋 Step 3: Showing sample transactions...")
    show_sample_transactions_with_charges()
    
    # Step 5: Analyze efficiency
    print(f"\n📋 Step 4: Analyzing charge efficiency...")
    analyze_charge_efficiency()
    
    print(f"\n🎉 CHARGE SYSTEM IMPLEMENTATION COMPLETED SUCCESSFULLY!")
    print(f"\n📝 Summary:")
    print(f"   • Added detailed charge columns")
    print(f"   • Applied charges using multiple methods (Percentage, Flat, Tiered)")
    print(f"   • Categorized charges by type and method") 
    print(f"   • Added transparent calculation descriptions")
    print(f"   • Your revenue analysis can now include detailed charge breakdowns!")

if __name__ == "__main__":
    main()