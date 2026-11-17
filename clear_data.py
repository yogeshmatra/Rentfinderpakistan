"""
Clear all dummy/sample data from Rent Finder Pakistan database.
Keeps: admin user, database schema, website settings (without personal numbers).
Removes: all properties, non-admin users, phone numbers, JazzCash, EasyPaisa, bank details.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rent_finder.db')

def clear_all_dummy_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Step 1: Removing all property-related data...")
    cursor.execute("DELETE FROM property_reports")
    cursor.execute("DELETE FROM viewing_appointments")
    cursor.execute("DELETE FROM enquiries")
    cursor.execute("DELETE FROM favorites")
    cursor.execute("DELETE FROM properties")
    print("  ✓ All properties, enquiries, appointments, favorites removed.")

    print("Step 2: Removing dummy users (keeping admin only)...")
    cursor.execute("DELETE FROM payments")
    cursor.execute("DELETE FROM subscriptions")
    cursor.execute("DELETE FROM advertisements")
    cursor.execute("DELETE FROM chat_messages")
    cursor.execute("DELETE FROM users WHERE role != 'admin'")
    print("  ✓ All non-admin users removed.")

    print("Step 3: Resetting admin user (clean credentials)...")
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    admin = cursor.fetchone()
    if not admin:
        # Create fresh admin if none exists
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, phone, whatsapp, city, role, is_verified, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Admin',
            'admin@rentfinder.pk',
            generate_password_hash('admin123'),
            '', '', 'Karachi', 'admin', 1, 'System Administrator'
        ))
        print("  ✓ Fresh admin user created.")
    else:
        # Clear personal contact info from admin
        cursor.execute('''
            UPDATE users SET phone = '', whatsapp = ''
            WHERE role = 'admin'
        ''')
        print("  ✓ Admin contact info cleared.")

    print("Step 4: Clearing personal numbers from website settings...")
    # Clear all personal/payment numbers
    settings_to_clear = {
        'contact_phone': '',
        'whatsapp_number': '',
        'office_address': '',
        'easypaisa_number': '',
        'easypaisa_title': '',
        'jazzcash_number': '',
        'jazzcash_title': '',
        'bank_name': '',
        'bank_account': '',
        'bank_iban': '',
        'bank_title': '',
        'active_listings_count': '0',
        'announcement_bar': 'Welcome to Rent Finder Pakistan - Find Your Perfect Rental Home.',
    }
    for key, value in settings_to_clear.items():
        cursor.execute(
            "UPDATE website_settings SET value = ? WHERE key = ?",
            (value, key)
        )
        # Insert if not exists
        cursor.execute(
            "INSERT OR IGNORE INTO website_settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    print("  ✓ Phone numbers, EasyPaisa, JazzCash, bank details cleared.")

    # Keep essential settings untouched
    print("Step 5: Keeping core site settings...")
    core_settings = {
        'site_name': 'Rent Finder Pakistan',
        'site_tagline': 'Find Your Perfect Rental Home.',
        'contact_email': 'admin@rentfinder.pk',
        'currency_symbol': 'PKR',
        'total_cities_covered': '12+',
        'gemini_model': 'gemini-1.5-flash',
        'featured_listing_fee': '3500',
    }
    for key, value in core_settings.items():
        cursor.execute(
            "INSERT OR IGNORE INTO website_settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    print("  ✓ Core settings preserved.")

    conn.commit()
    conn.close()

    print("\n" + "="*55)
    print("  DATABASE CLEANUP COMPLETE!")
    print("="*55)
    print("  Properties        : 0 (empty - ready for real data)")
    print("  Dummy Users       : Removed")
    print("  Admin Account     : KEPT (admin@rentfinder.pk)")
    print("  Admin Password    : admin123")
    print("  Phone Numbers     : CLEARED")
    print("  EasyPaisa Numbers : CLEARED")
    print("  JazzCash Numbers  : CLEARED")
    print("  Bank Details      : CLEARED")
    print("  Design & Features : UNCHANGED")
    print("  Admin Panel       : INTACT")
    print("="*55)

if __name__ == '__main__':
    clear_all_dummy_data()
