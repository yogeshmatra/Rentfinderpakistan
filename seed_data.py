"""
Rent Finder Pakistan - Initial Setup Script
Creates admin user and core website settings only.
No dummy properties or sample data.
"""

from database import init_db, get_db
from werkzeug.security import generate_password_hash

def seed_all():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    print("Initializing Rent Finder Pakistan database...")

    # Core website settings (no personal phone/payment numbers)
    settings = {
        'site_name': 'Rent Finder Pakistan',
        'site_tagline': 'Find Your Perfect Rental Home.',
        'contact_email': 'admin@rentfinder.pk',
        'contact_phone': '',
        'whatsapp_number': '',
        'office_address': '',
        'announcement_bar': 'Welcome to Rent Finder Pakistan - Find Your Perfect Rental Home.',
        'currency_symbol': 'PKR',
        'total_cities_covered': '12+',
        'active_listings_count': '0',
        'gemini_api_key': '',
        'gemini_model': 'gemini-1.5-flash',
        'featured_listing_fee': '3500',
        'easypaisa_number': '',
        'easypaisa_title': '',
        'jazzcash_number': '',
        'jazzcash_title': '',
        'bank_name': '',
        'bank_account': '',
        'bank_iban': '',
        'bank_title': '',
    }
    for k, v in settings.items():
        cursor.execute(
            "INSERT OR IGNORE INTO website_settings (key, value) VALUES (?, ?)",
            (k, str(v))
        )
    conn.commit()
    print("  ✓ Website settings configured.")

    # Create admin user only (no dummy landlords or tenants)
    cursor.execute("SELECT id FROM users WHERE email = 'admin@rentfinder.pk'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, phone, whatsapp, city, role, is_verified, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Admin',
            'admin@rentfinder.pk',
            generate_password_hash('admin123'),
            '', '', 'Karachi', 'admin', 1,
            'System Administrator at Rent Finder Pakistan.'
        ))
        conn.commit()
        print("  ✓ Admin user created.")
    else:
        print("  ✓ Admin user already exists.")

    conn.close()

    print("\n" + "="*50)
    print("  SETUP COMPLETE - Database is ready!")
    print("="*50)
    print("  Admin Email    : admin@rentfinder.pk")
    print("  Admin Password : admin123")
    print("  Properties     : 0 (empty - add via admin panel)")
    print("="*50)

if __name__ == '__main__':
    seed_all()
