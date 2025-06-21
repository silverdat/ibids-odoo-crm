#!/usr/bin/env python3
"""
Script to manually add the govcon_crm module to Odoo database
"""
import psycopg2
import sys

# Database connection parameters
DB_HOST = 'db'  # Docker service name
DB_PORT = 5432
DB_NAME = 'ibidscrm'
DB_USER = 'odoo'
DB_PASSWORD = 'odoo'

def add_module_to_database():
    """Add govcon_crm module to the ir_module_module table"""
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
        
        # Check if module already exists
        cursor.execute("SELECT id FROM ir_module_module WHERE name = 'govcon_crm'")
        existing = cursor.fetchone()
        
        if existing:
            print("Module govcon_crm already exists in database")
            return
        
        # Insert the module with minimal required fields
        cursor.execute("""
            INSERT INTO ir_module_module (
                name, shortdesc, description, author, website, 
                category_id, state, create_date, write_date, create_uid, write_uid
            ) VALUES (
                'govcon_crm', 
                'Government Contracting CRM - Dominican Republic',
                'Comprehensive CRM for managing Dominican Republic government contracting processes',
                'Your Company',
                'https://www.yourcompany.com',
                (SELECT id FROM ir_module_category WHERE name = 'Sales/CRM' LIMIT 1),
                'uninstalled',
                NOW(),
                NOW(),
                1,
                1
            )
        """)
        
        conn.commit()
        print("Successfully added govcon_crm module to database")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_module_to_database() 