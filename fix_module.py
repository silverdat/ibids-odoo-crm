#!/usr/bin/env python3
"""
Script to fix the govcon_crm module state in Odoo database
"""
import psycopg2

# Database connection parameters
DB_HOST = 'db'
DB_PORT = 5432
DB_NAME = 'ibidscrm'
DB_USER = 'odoo'
DB_PASSWORD = 'odoo'

def fix_module_state():
    """Fix the module state in the database"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Update the module state to installed
        cursor.execute("""
            UPDATE ir_module_module 
            SET state = 'installed', 
                write_date = NOW()
            WHERE name = 'govcon_crm'
        """)
        
        # Also clear any pending installation states
        cursor.execute("""
            UPDATE ir_module_module 
            SET state = 'installed'
            WHERE state IN ('to install', 'to upgrade', 'to uninstall')
            AND name = 'govcon_crm'
        """)
        
        conn.commit()
        print("Successfully fixed govcon_crm module state to 'installed'")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_module_state() 