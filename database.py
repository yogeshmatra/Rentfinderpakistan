"""
Rent Finder Pakistan - Database Management & Models
SQLite-based persistent database with complete schemas and helper methods.
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rent_finder.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT,
        whatsapp TEXT,
        city TEXT DEFAULT 'Karachi',
        role TEXT DEFAULT 'user', -- 'user', 'landlord', 'agent', 'admin'
        avatar TEXT,
        bio TEXT,
        is_verified INTEGER DEFAULT 0, -- Trust & Safety verified landlord/agent badge
        verification_docs TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Properties table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        property_type TEXT NOT NULL, -- 'House', 'Flat', 'Room', 'Upper Portion', 'Lower Portion', 'Complete Portion', 'Shop', 'Office', 'Penthouse'
        city TEXT NOT NULL,
        area TEXT NOT NULL,
        address TEXT,
        monthly_rent INTEGER NOT NULL,
        advance_payment TEXT DEFAULT '2 Months Advance',
        security_deposit INTEGER DEFAULT 0,
        extra_charges TEXT DEFAULT 'Utilities not included',
        bedrooms INTEGER DEFAULT 0,
        bathrooms INTEGER DEFAULT 0,
        size REAL DEFAULT 0,
        size_unit TEXT DEFAULT 'Marla', -- 'Marla', 'Kanal', 'Sq Ft', 'Sq Yards'
        furnished TEXT DEFAULT 'Unfurnished', -- 'Furnished', 'Semi-Furnished', 'Unfurnished'
        floor_level TEXT DEFAULT 'Ground',
        parking_spaces INTEGER DEFAULT 0,
        facilities TEXT DEFAULT '[]', -- JSON string of amenities list
        images TEXT DEFAULT '[]', -- JSON string of image paths / URLs
        latitude REAL,
        longitude REAL,
        contact_name TEXT,
        contact_phone TEXT,
        contact_whatsapp TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
        rejection_reason TEXT,
        is_featured INTEGER DEFAULT 0,
        is_sponsored INTEGER DEFAULT 0,
        views_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Saved Favorites table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        property_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, property_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
    )
    ''')

    # Enquiries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER NOT NULL,
        sender_id INTEGER,
        sender_name TEXT NOT NULL,
        sender_email TEXT NOT NULL,
        sender_phone TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')

    # Viewing Appointments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS viewing_appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER NOT NULL,
        user_id INTEGER,
        visitor_name TEXT NOT NULL,
        visitor_phone TEXT NOT NULL,
        visitor_email TEXT,
        preferred_date TEXT NOT NULL,
        time_slot TEXT NOT NULL, -- 'Morning (9 AM - 12 PM)', 'Afternoon (12 PM - 4 PM)', 'Evening (4 PM - 7 PM)'
        notes TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'confirmed', 'cancelled', 'completed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')

    # Property Reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS property_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER NOT NULL,
        reporter_id INTEGER,
        reporter_email TEXT,
        reason TEXT NOT NULL,
        details TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'investigating', 'resolved', 'dismissed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
        FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')

    # Monetization: Subscriptions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL, -- 'Silver Landlord', 'Gold Landlord', 'Platinum Agency'
        amount INTEGER NOT NULL,
        payment_method TEXT NOT NULL, -- 'JazzCash', 'Easypaisa', 'Bank Transfer', 'Debit / Credit Card'
        transaction_ref TEXT,
        status TEXT DEFAULT 'active', -- 'pending', 'active', 'expired'
        listing_limit INTEGER DEFAULT 10,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Monetization: Payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        property_id INTEGER,
        payment_type TEXT NOT NULL, -- 'featured_listing', 'subscription', 'advertisement'
        amount INTEGER NOT NULL,
        payment_method TEXT NOT NULL, -- 'Easypaisa', 'JazzCash', 'Bank Transfer', 'Debit / Credit Card'
        account_number TEXT,
        transaction_id TEXT NOT NULL,
        status TEXT DEFAULT 'approved', -- 'pending', 'approved', 'rejected'
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
    )
    ''')

    # Advertisements table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS advertisements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        client_name TEXT NOT NULL,
        banner_image TEXT NOT NULL,
        target_url TEXT NOT NULL,
        placement TEXT DEFAULT 'sidebar', -- 'home_featured', 'sidebar', 'footer'
        impressions INTEGER DEFAULT 0,
        clicks INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # AI Chatbot History table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        user_id INTEGER,
        role TEXT NOT NULL, -- 'user', 'assistant'
        content TEXT NOT NULL,
        properties_json TEXT, -- Optional JSON string of matching property cards
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Website Settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS website_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    conn.commit()
    conn.close()

def get_setting(key, default=''):
    conn = get_db()
    row = conn.execute("SELECT value FROM website_settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else default

def set_setting(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO website_settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def get_all_settings():
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM website_settings").fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}

def find_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()
    conn.close()
    return user

def find_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def create_user(name, email, password, phone='', whatsapp='', city='Karachi', role='user', bio=''):
    conn = get_db()
    password_hash = generate_password_hash(password)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, phone, whatsapp, city, role, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name.strip(), email.strip().lower(), password_hash, phone, whatsapp, city, role, bio))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def check_duplicate_property(user_id, title, city, area, monthly_rent):
    conn = get_db()
    row = conn.execute('''
        SELECT id FROM properties
        WHERE user_id = ? AND LOWER(title) = LOWER(?) AND LOWER(city) = LOWER(?) AND LOWER(area) = LOWER(?) AND monthly_rent = ?
    ''', (user_id, title.strip(), city.strip(), area.strip(), monthly_rent)).fetchone()
    conn.close()
    return bool(row)

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at", DB_PATH)
