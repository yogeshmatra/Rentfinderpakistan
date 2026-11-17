"""
Seed Data Generator for Rent Finder Pakistan
Creates admin, demo landlords/agents, realistic Pakistani properties, viewing appointments, inquiries, monetization data, advertisements, and settings.
"""

import json
from datetime import datetime, timedelta
from database import init_db, get_db, create_user, set_setting, DB_PATH
from werkzeug.security import generate_password_hash

def seed_all():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # Clear old data to prevent stale duplicates on re-seeding
    cursor.execute("DELETE FROM property_reports")
    cursor.execute("DELETE FROM viewing_appointments")
    cursor.execute("DELETE FROM enquiries")
    cursor.execute("DELETE FROM favorites")
    cursor.execute("DELETE FROM payments")
    cursor.execute("DELETE FROM subscriptions")
    cursor.execute("DELETE FROM advertisements")
    cursor.execute("DELETE FROM chat_messages")
    cursor.execute("DELETE FROM properties")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM website_settings")
    conn.commit()

    print("Configuring Website Settings...")
    settings = {
        'site_name': 'Rent Finder Pakistan',
        'site_tagline': 'Find Your Perfect Rental Home.',
        'contact_email': 'support@rentfinder.pk',
        'contact_phone': '+92 300 8291034',
        'whatsapp_number': '+92 300 8291034',
        'office_address': 'Suite 504, FTC Building, Shahrah-e-Faisal, Karachi, Pakistan',
        'announcement_bar': 'Verified houses, flats, portions, shops & offices for rent across all major cities of Pakistan.',
        'currency_symbol': 'PKR',
        'total_cities_covered': '12+',
        'active_listings_count': '150+',
        'gemini_api_key': '',
        'gemini_model': 'gemini-1.5-flash',
        'featured_listing_fee': '3500',
        'easypaisa_number': '03008291034',
        'easypaisa_title': 'Rent Finder Pakistan Pvt Ltd',
        'jazzcash_number': '03019988776',
        'jazzcash_title': 'Rent Finder Pakistan',
        'bank_name': 'Meezan Bank Ltd',
        'bank_account': '01020304050607',
        'bank_iban': 'PK45MEZN0001020304050607',
        'bank_title': 'Rent Finder Pakistan (Pvt) Limited'
    }
    for k, v in settings.items():
        cursor.execute("INSERT OR REPLACE INTO website_settings (key, value) VALUES (?, ?)", (k, str(v)))
    conn.commit()

    print("Creating System Users...")
    users = [
        {
            'name': 'Muhammad Tariq (Admin)',
            'email': 'admin@rentfinder.pk',
            'password': 'admin123',
            'phone': '+92 300 8291034',
            'whatsapp': '+92 300 8291034',
            'city': 'Karachi',
            'role': 'admin',
            'is_verified': 1,
            'bio': 'System Administrator & Portal Moderator at Rent Finder Pakistan.'
        },
        {
            'name': 'Malik Usman Real Estate',
            'email': 'usman.realtors@gmail.com',
            'password': 'password123',
            'phone': '+92 321 4455667',
            'whatsapp': '+92 321 4455667',
            'city': 'Lahore',
            'role': 'agent',
            'is_verified': 1,
            'bio': 'Specializing in luxury rental properties across DHA Lahore, Gulberg and Johar Town.'
        },
        {
            'name': 'Syed Farhan Bukhari',
            'email': 'farhan.bukhari@yahoo.com',
            'password': 'password123',
            'phone': '+92 333 5511223',
            'whatsapp': '+92 333 5511223',
            'city': 'Islamabad',
            'role': 'landlord',
            'is_verified': 1,
            'bio': 'Private property owner offering premium residences in CDA Sectors F-7, F-10 and E-11.'
        },
        {
            'name': 'Karachi Prime Estates',
            'email': 'contact@karachiprime.pk',
            'password': 'password123',
            'phone': '+92 301 9988776',
            'whatsapp': '+92 301 9988776',
            'city': 'Karachi',
            'role': 'agent',
            'is_verified': 1,
            'bio': 'Leading rental brokerage in Clifton, DHA Karachi and Gulshan-e-Iqbal.'
        },
        {
            'name': 'Hamza Rafique',
            'email': 'hamza.tenant@gmail.com',
            'password': 'password123',
            'phone': '+92 345 1122334',
            'whatsapp': '+92 345 1122334',
            'city': 'Karachi',
            'role': 'user',
            'is_verified': 0,
            'bio': 'Software engineer looking for modern rental apartment in Karachi.'
        }
    ]

    user_ids = {}
    for u in users:
        pwd_hash = generate_password_hash(u['password'])
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, phone, whatsapp, city, role, is_verified, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (u['name'], u['email'], pwd_hash, u['phone'], u['whatsapp'], u['city'], u['role'], u['is_verified'], u['bio']))
        user_ids[u['email']] = cursor.lastrowid
    conn.commit()

    admin_id = user_ids['admin@rentfinder.pk']
    usman_id = user_ids['usman.realtors@gmail.com']
    bukhari_id = user_ids['farhan.bukhari@yahoo.com']
    karachi_agent_id = user_ids['contact@karachiprime.pk']
    tenant_id = user_ids['hamza.tenant@gmail.com']

    print("Populating Realistic Pakistani Rental Properties...")

    properties_data = [
        # 1. Karachi - Clifton Flat
        {
            'user_id': karachi_agent_id,
            'title': 'Luxury 3-Bed Apartment with Arabian Sea Breeze & Balcony',
            'description': '''Prime executive residence situated in the high-demand Clifton Block 4 near Bilawal House and Beach Avenue. 
Featuring 3 spacious bedrooms with attached imported European-tiled bathrooms, an airy drawing-dining lounge, contemporary Italian-style open kitchen with quartz countertops, servant room with bath, and a panoramic wide balcony.
Building offers 2 dedicated high-speed Japanese lifts, standby Caterpillar generator (zero loadshedding), 24/7 CCTV surveillance with armed guard, covered basement parking, and continuous sweet water supply line.''',
            'property_type': 'Flat',
            'city': 'Karachi',
            'area': 'Clifton Block 4',
            'address': 'Marine Drive Heights, Block 4, Clifton, Karachi',
            'monthly_rent': 185000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 370000,
            'extra_charges': 'Building Maintenance: PKR 12,000 / month',
            'bedrooms': 3,
            'bathrooms': 3,
            'size': 2400,
            'size_unit': 'Sq Ft',
            'furnished': 'Semi-Furnished',
            'floor_level': '7th Floor',
            'parking_spaces': 2,
            'facilities': ['Standby Generator', 'High-Speed Elevators', 'Sweet Water Supply', 'Sui Gas Active', '24/7 Security CCTV', 'Covered Basement Parking', 'Balcony', 'Servant Quarter', 'Intercom System'],
            'images': [
                'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 24.8188,
            'longitude': 67.0322,
            'contact_name': 'Karachi Prime Estates',
            'contact_phone': '+92 301 9988776',
            'contact_whatsapp': '+92 301 9988776',
            'status': 'approved',
            'is_featured': 1,
            'is_sponsored': 1,
            'views_count': 342
        },

        # 2. Karachi - DHA Phase 6 Bungalow
        {
            'user_id': karachi_agent_id,
            'title': 'Brand New 500 Sq Yards 5-Bed Designer Bungalow with Basement',
            'description': '''Exquisite modern masterpiece in DHA Phase 6 on a quiet 50-foot wide road. Architect-designed with double-height ceiling lobby, Spanish porcelain flooring, and imported fixtures.
Includes 5 master bedrooms with walk-in closets, designer wet and show kitchens with cooking range, home theatre basement room, lush front lawn with water feature, separate 2-room servant quarter, and automatic remote-controlled car gate.
Direct connection to Cantonment sweet line water plus functional underground tank with sweet boring backup. Solid Sui gas pressure.''',
            'property_type': 'House',
            'city': 'Karachi',
            'area': 'DHA Phase 6',
            'address': 'Street 18, Khayaban-e-Hafiz, Phase 6, DHA Karachi',
            'monthly_rent': 380000,
            'advance_payment': '3 Months Advance',
            'security_deposit': 760000,
            'extra_charges': 'CBC Municipal Taxes and Security patrol fee PKR 8,000 / month',
            'bedrooms': 5,
            'bathrooms': 6,
            'size': 500,
            'size_unit': 'Sq Yards',
            'furnished': 'Unfurnished',
            'floor_level': 'Ground + 1 + Basement',
            'parking_spaces': 4,
            'facilities': ['Lawn / Garden', 'Home Theatre Room', 'Sui Gas Active', 'Sweet Water Line', 'Solar System 15kW Installed', 'Servant Quarters', 'Basement', 'Automated Gate', 'CCTV Security'],
            'images': [
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 24.7891,
            'longitude': 67.0624,
            'contact_name': 'Tariq Mehmood (Senior Consultant)',
            'contact_phone': '+92 301 9988776',
            'contact_whatsapp': '+92 301 9988776',
            'status': 'approved',
            'is_featured': 1,
            'is_sponsored': 1,
            'views_count': 512
        },

        # 3. Karachi - Gulshan-e-Iqbal Upper Portion
        {
            'user_id': karachi_agent_id,
            'title': 'Spacious 3-Bed Upper Portion with Separate Entrance & Roof Access',
            'description': '''Convenient and secure 1st floor upper portion in Block 13-D Gulshan-e-Iqbal. Ideal for small to mid-sized decent families.
Features a completely independent staircase entrance, separate K-Electric digital meter, separate Sui Gas line, 3 well-lit bedrooms with attached baths, spacious TV lounge, and full private access to the terrace.
Located within walking distance of Sir Syed University, mosques, departmental stores, and main University Road transport links.''',
            'property_type': 'Upper Portion',
            'city': 'Karachi',
            'area': 'Gulshan-e-Iqbal Block 13-D',
            'address': 'Near Hasan Square & Al-Mustafa Trust, Block 13-D, Gulshan-e-Iqbal, Karachi',
            'monthly_rent': 58000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 116000,
            'extra_charges': 'Separate Sub-meter for utilities',
            'bedrooms': 3,
            'bathrooms': 3,
            'size': 240,
            'size_unit': 'Sq Yards',
            'furnished': 'Unfurnished',
            'floor_level': '1st Floor',
            'parking_spaces': 1,
            'facilities': ['Independent Entrance', 'Separate Gas Meter', 'Separate Electric Meter', 'Roof Access / Terrace', 'Sweet Water Line', 'Near Mosque', 'Near Public Transport'],
            'images': [
                'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 24.9123,
            'longitude': 67.0815,
            'contact_name': 'Rashid Property Advisor',
            'contact_phone': '+92 300 2345678',
            'contact_whatsapp': '+92 300 2345678',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 228
        },

        # 4. Lahore - DHA Phase 5 1 Kanal House
        {
            'user_id': usman_id,
            'title': '1 Kanal Ultra-Modern 5-Bed House with Basement & Lawn in DHA Phase 5',
            'description': '''Magnificent corner 1 Kanal home situated in Sector C, DHA Phase 5 Lahore. Built according to top engineering specifications with Ashwood doors, Grohe bathroom fittings, and Spanish tiles.
Offers 5 executive en-suite bedrooms, dual designer kitchens equipped with hood & microwave ovens, huge drawing/dining, spacious family lounge, landscaped lawn with pergola, and covered car porch for 3 full-size SUVs.
Near Ring Road interchange, DHA Sports Club, and international schools.''',
            'property_type': 'House',
            'city': 'Lahore',
            'area': 'DHA Phase 5',
            'address': 'Sector C, Main Boulevard, Phase 5, DHA Lahore',
            'monthly_rent': 320000,
            'advance_payment': '3 Months Advance',
            'security_deposit': 640000,
            'extra_charges': 'DHA Maintenance & Security: PKR 6,500 / month',
            'bedrooms': 5,
            'bathrooms': 6,
            'size': 1,
            'size_unit': 'Kanal',
            'furnished': 'Unfurnished',
            'floor_level': 'Ground + 1 + Basement',
            'parking_spaces': 3,
            'facilities': ['Lawn / Garden', 'Corner Plot', 'Standby Generator Wiring', 'Sui Gas Active', 'LESCO 3-Phase Meter', 'Servant Quarters', 'Basement', 'Near Commercial Market', 'Near Ring Road'],
            'images': [
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600573472591-ee6b68d14c68?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 31.4697,
            'longitude': 74.3986,
            'contact_name': 'Malik Usman',
            'contact_phone': '+92 321 4455667',
            'contact_whatsapp': '+92 321 4455667',
            'status': 'approved',
            'is_featured': 1,
            'is_sponsored': 1,
            'views_count': 640
        },

        # 5. Lahore - Gulberg III Serviced Apartment
        {
            'user_id': usman_id,
            'title': 'Fully Furnished 2-Bed Luxury Serviced Apartment off MM Alam Road',
            'description': '''Boutique luxury living right next to Lahore's culinary and shopping strip on MM Alam Road Gulberg.
Tastefully decorated with plush sofa set, 65-inch 4K LED TV, king-size beds with orthopedic mattresses, inverter ACs in all rooms, and a fully functional kitchen with refrigerator, microwave and crockery.
Includes dedicated underground parking slot, high-speed fiber internet, housekeeping option, gym access, and 100% generator backup.''',
            'property_type': 'Flat',
            'city': 'Lahore',
            'area': 'Gulberg III',
            'address': 'Grand Residency Tower, off MM Alam Road, Gulberg III, Lahore',
            'monthly_rent': 115000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 230000,
            'extra_charges': 'Service & Maintenance: PKR 10,000 / month',
            'bedrooms': 2,
            'bathrooms': 2,
            'size': 1350,
            'size_unit': 'Sq Ft',
            'furnished': 'Furnished',
            'floor_level': '5th Floor',
            'parking_spaces': 1,
            'facilities': ['Furnished with Appliances', 'Inverter ACs', 'Gymnasium Access', 'High-Speed Elevators', 'Standby Generator', '24/7 Security CCTV', 'Covered Basement Parking', 'Balcony'],
            'images': [
                'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 31.5134,
            'longitude': 74.3541,
            'contact_name': 'Malik Usman Real Estate',
            'contact_phone': '+92 321 4455667',
            'contact_whatsapp': '+92 321 4455667',
            'status': 'approved',
            'is_featured': 1,
            'is_sponsored': 1,
            'views_count': 418
        },

        # 6. Lahore - Johar Town Lower Portion
        {
            'user_id': usman_id,
            'title': '10 Marla Ground Floor Lower Portion with Car Porch near Expo Center',
            'description': '''Comfortable ground floor portion in a solid 10 Marla house in Johar Town Block J2.
Features 3 bedrooms with tiled attached washrooms, large drawing room, separate dining area, TV lounge, and practical kitchen with fitted wooden cabinets.
Dedicated covered car porch for 2 cars, separate Wapda meter, Sui gas connection, and peaceful family environment.''',
            'property_type': 'Lower Portion',
            'city': 'Lahore',
            'area': 'Johar Town Block J2',
            'address': 'Block J2, Near Expo Center & Doctors Hospital, Johar Town, Lahore',
            'monthly_rent': 65000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 130000,
            'extra_charges': 'Separate meter bill sharing on actual consumption',
            'bedrooms': 3,
            'bathrooms': 3,
            'size': 10,
            'size_unit': 'Marla',
            'furnished': 'Unfurnished',
            'floor_level': 'Ground Floor',
            'parking_spaces': 2,
            'facilities': ['Car Porch Parking', 'Independent Gas Connection', 'Independent Electric Meter', 'Near Doctors Hospital', 'Near Emporium Mall', 'Wide Street (40 ft)'],
            'images': [
                'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600585152220-90363fe7e115?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 31.4704,
            'longitude': 74.2721,
            'contact_name': 'Haji Iftikhar Property Dealer',
            'contact_phone': '+92 321 9876543',
            'contact_whatsapp': '+92 321 9876543',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 195
        },

        # 7. Islamabad - F-7/2 Double Storey House
        {
            'user_id': bukhari_id,
            'title': 'Prestigious 10 Marla 4-Bed House in F-7/2 with Margalla View',
            'description': '''Prestigious CDA approved residential sector F-7/2 Islamabad. Close to Jinnah Super Market and Safa Gold Mall.
4 bedrooms with Italian bath ceramics, large double lounge with fireplace, formal drawing room, fully fitted teak wood kitchen with pantry, servant quarter with bathroom, and rooftop terrace facing the picturesque Margalla Hills.
IESCO 3-phase electricity, Sui gas, continuous CDA water supply plus underground water reservoir.''',
            'property_type': 'House',
            'city': 'Islamabad',
            'area': 'Sector F-7/2',
            'address': 'Street 34, Sector F-7/2, Islamabad',
            'monthly_rent': 260000,
            'advance_payment': '3 Months Advance',
            'security_deposit': 520000,
            'extra_charges': 'Security & CDA conservancy fee: PKR 5,000 / month',
            'bedrooms': 4,
            'bathrooms': 5,
            'size': 10,
            'size_unit': 'Marla',
            'furnished': 'Semi-Furnished',
            'floor_level': 'Ground + 1',
            'parking_spaces': 3,
            'facilities': ['Margalla Hills View', 'Lawn / Garden', 'Sui Gas Active', 'CDA Water Connection', 'Servant Quarters', 'Fireplace', 'Near Jinnah Super Market', 'Secure Diplomatic Zone Vicinity'],
            'images': [
                'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600573472591-ee6b68d14c68?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 33.7215,
            'longitude': 73.0556,
            'contact_name': 'Syed Farhan Bukhari',
            'contact_phone': '+92 333 5511223',
            'contact_whatsapp': '+92 333 5511223',
            'status': 'approved',
            'is_featured': 1,
            'is_sponsored': 1,
            'views_count': 720
        },

        # 8. Islamabad - E-11/2 Luxury Apartment
        {
            'user_id': bukhari_id,
            'title': 'Modern 2-Bed Furnished Apartment with Scenic Hills View in E-11',
            'description': '''Elegantly furnished apartment in a family-oriented tower in Sector E-11/2 Islamabad.
Includes 2 spacious bedrooms with attached bathrooms, drawing room, fully equipped American open kitchen with stainless steel appliances, and a private balcony overlooking the lush Margalla range.
Building provides 24-hour backup generator, dual high-speed elevators, CCTV cameras, dedicated maintenance team, and covered car parking.''',
            'property_type': 'Flat',
            'city': 'Islamabad',
            'area': 'Sector E-11/2',
            'address': 'Silver Oaks Heights, Sector E-11/2, Islamabad',
            'monthly_rent': 80000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 160000,
            'extra_charges': 'Building Maintenance: PKR 6,000 / month',
            'bedrooms': 2,
            'bathrooms': 2,
            'size': 1250,
            'size_unit': 'Sq Ft',
            'furnished': 'Furnished',
            'floor_level': '6th Floor',
            'parking_spaces': 1,
            'facilities': ['Furnished with Appliances', 'Margalla View Balcony', 'High-Speed Elevators', 'Standby Generator', '24/7 Security CCTV', 'Covered Parking', 'Sui Gas Active'],
            'images': [
                'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 33.6989,
            'longitude': 72.9817,
            'contact_name': 'Syed Farhan Bukhari',
            'contact_phone': '+92 333 5511223',
            'contact_whatsapp': '+92 333 5511223',
            'status': 'approved',
            'is_featured': 1,
            'is_sponsored': 1,
            'views_count': 380
        },

        # 9. Islamabad - Blue Area Corporate Office
        {
            'user_id': bukhari_id,
            'title': 'Prime Commercial Corporate Office Floor (2,500 Sq Ft) in Blue Area',
            'description': '''Class-A commercial office space located in the business epicenter of Islamabad: Jinnah Avenue, Blue Area.
Fitted with glass partitions, executive conference room, 4 director manager rooms, open hall for 30+ workstations, dedicated server room with fire suppression, reception lobby, and separate male/female washrooms.
Equipped with dual power backup generators, centralized chiller HVAC, 4 OTIS elevators, and 5 reserved underground car parking slots.''',
            'property_type': 'Office',
            'city': 'Islamabad',
            'area': 'Blue Area (Jinnah Avenue)',
            'address': 'State Life Tower / Beverly Centre vicinity, Blue Area, Islamabad',
            'monthly_rent': 250000,
            'advance_payment': '3 Months Advance',
            'security_deposit': 500000,
            'extra_charges': 'Plaza Central Maintenance: PKR 25,000 / month',
            'bedrooms': 0,
            'bathrooms': 4,
            'size': 2500,
            'size_unit': 'Sq Ft',
            'furnished': 'Semi-Furnished',
            'floor_level': '4th Floor',
            'parking_spaces': 5,
            'facilities': ['Centralized Air Conditioning', 'Glass Partitions & Cabins', 'Conference Room', 'Standby Industrial Generators', '4 High-Speed Lifts', '24/7 Armed Security & CCTV', 'Fire Safety Sprinklers', 'Dedicated Server Room'],
            'images': [
                'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 33.7121,
            'longitude': 73.0645,
            'contact_name': 'Syed Farhan Bukhari',
            'contact_phone': '+92 333 5511223',
            'contact_whatsapp': '+92 333 5511223',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 310
        },

        # 10. Rawalpindi - Bahria Town Phase 7 Luxury House
        {
            'user_id': usman_id,
            'title': '10 Marla 4-Bed Luxury House in Bahria Town Phase 7 near River View',
            'description': '''Solid constructed 10 Marla designer house in Phase 7 Bahria Town Rawalpindi.
Features 4 air-conditioned bedrooms with luxury en-suite baths, 2 imported kitchens with Corian worktops, spacious double-height lobby, servant room, and tiled car porch.
Bahria Town guarantees zero loadshedding with uninterrupted 24/7 underground power supply, round-the-clock security patrol, and proximity to grocery stores, green parks, and international dining chains.''',
            'property_type': 'House',
            'city': 'Rawalpindi',
            'area': 'Bahria Town Phase 7',
            'address': 'Sector B, River View Commercial Lane, Phase 7, Bahria Town Rawalpindi',
            'monthly_rent': 115000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 230000,
            'extra_charges': 'Bahria Maintenance Charges: PKR 4,500 / month',
            'bedrooms': 4,
            'bathrooms': 5,
            'size': 10,
            'size_unit': 'Marla',
            'furnished': 'Unfurnished',
            'floor_level': 'Ground + 1',
            'parking_spaces': 2,
            'facilities': ['Bahria 24/7 Electricity (No Loadshedding)', 'Sui Gas Available', 'Servant Quarters', 'Gated Community Security', 'Car Porch', 'Near Commercial Hub'],
            'images': [
                'https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 33.5358,
            'longitude': 73.1198,
            'contact_name': 'Malik Usman Real Estate',
            'contact_phone': '+92 321 4455667',
            'contact_whatsapp': '+92 321 4455667',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 280
        },

        # 11. Karachi - I.I. Chundrigar Road Commercial Office
        {
            'user_id': karachi_agent_id,
            'title': 'Fully Renovated Commercial Office Space (1,200 Sq Ft) on I.I. Chundrigar Road',
            'description': '''Strategic financial district office suite on Pakistan's Wall Street (I.I. Chundrigar Road).
Walking distance from State Bank of Pakistan and City Railway Station.
Accommodates 2 executive suites, open floor plan for 16 associates, kitchen pantry, private washrooms, and IT server enclosure.
High building security with turnstile badge entrance, standby generator, and passenger elevators.''',
            'property_type': 'Office',
            'city': 'Karachi',
            'area': 'I.I. Chundrigar Road',
            'address': 'Uni Center / Muhammadi House, I.I. Chundrigar Road, Karachi',
            'monthly_rent': 120000,
            'advance_payment': '3 Months Advance',
            'security_deposit': 240000,
            'extra_charges': 'Maintenance: PKR 14,000 / month',
            'bedrooms': 0,
            'bathrooms': 2,
            'size': 1200,
            'size_unit': 'Sq Ft',
            'furnished': 'Semi-Furnished',
            'floor_level': '3rd Floor',
            'parking_spaces': 2,
            'facilities': ['Standby Generator', 'High-Speed Elevators', 'Turnstile Access Control', '24/7 Security CCTV', 'Fire Extinguishers', 'Kitchenette / Pantry'],
            'images': [
                'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 24.8532,
            'longitude': 67.0069,
            'contact_name': 'Karachi Prime Estates',
            'contact_phone': '+92 301 9988776',
            'contact_whatsapp': '+92 301 9988776',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 165
        },

        # 12. Lahore - Anarkali / Mall Road Corner Shop
        {
            'user_id': usman_id,
            'title': 'Prime Corner Retail Commercial Shop (450 Sq Ft) near Mall Road',
            'description': '''Exceptional high-footfall corner retail showroom located right off the historic Mall Road & Anarkali Bazaar intersection.
Double glass display frontage, ceramic flooring, false ceiling with spotlights, mezzanine storage space, and separate washroom.
Suitable for clothing boutique, pharmacy, cosmetics store, telecom franchise or electronics retail.''',
            'property_type': 'Shop',
            'city': 'Lahore',
            'area': 'Mall Road / Anarkali',
            'address': 'Corner Plaza, Commercial Square, Mall Road, Lahore',
            'monthly_rent': 85000,
            'advance_payment': '6 Months Advance',
            'security_deposit': 170000,
            'extra_charges': 'Commercial Plaza fee PKR 5,000 / month',
            'bedrooms': 0,
            'bathrooms': 1,
            'size': 450,
            'size_unit': 'Sq Ft',
            'furnished': 'Unfurnished',
            'floor_level': 'Ground Floor (Corner)',
            'parking_spaces': 1,
            'facilities': ['Corner Location', 'Double Glass Display', 'Mezzanine Storage Floor', 'High Footfall Area', 'Commercial 3-Phase Meter', 'Security Shutter'],
            'images': [
                'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 31.5621,
            'longitude': 74.3167,
            'contact_name': 'Malik Usman Real Estate',
            'contact_phone': '+92 321 4455667',
            'contact_whatsapp': '+92 321 4455667',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 230
        },

        # 13. Hyderabad - Qasimabad Ground Portion
        {
            'user_id': karachi_agent_id,
            'title': '3-Bed Family Ground Portion with Sweet Water in Qasimabad Hyderabad',
            'description': '''Comfortable ground floor portion in a reputable residential colony of Qasimabad Hyderabad.
Consists of 3 airy bedrooms, attached washrooms, front veranda, open courtyard, drawing room, kitchen, and dedicated covered car parking.
Has uninterrupted WASA sweet water supply, Sui gas, and near reputable schools and hospitals.''',
            'property_type': 'Lower Portion',
            'city': 'Hyderabad',
            'area': 'Qasimabad Phase 1',
            'address': 'Street 6, Citizen Colony, Qasimabad, Hyderabad, Sindh',
            'monthly_rent': 38000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 76000,
            'extra_charges': 'Electricity & Gas bills separate',
            'bedrooms': 3,
            'bathrooms': 3,
            'size': 200,
            'size_unit': 'Sq Yards',
            'furnished': 'Unfurnished',
            'floor_level': 'Ground Floor',
            'parking_spaces': 1,
            'facilities': ['Sweet Water Connection', 'Sui Gas Active', 'Car Parking Porch', 'Open Courtyard', 'Near Schools & Clinics'],
            'images': [
                'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 25.4052,
            'longitude': 68.3414,
            'contact_name': 'Ahmed Ali Broker',
            'contact_phone': '+92 300 3012345',
            'contact_whatsapp': '+92 300 3012345',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 142
        },

        # 14. Multan - Cantt 1 Kanal Executive House
        {
            'user_id': usman_id,
            'title': '1 Kanal 5-Bed Executive Residence with Green Lawn in Multan Cantt',
            'description': '''Prestigious and tranquil 1 Kanal residence located in the secure Cantt enclave of Multan near Bosan Road.
Features 5 spacious bedrooms, 2 kitchens, large drawing and formal dining room, wide terrace, expansive front lawn with fruit trees, and servant quarters.
High boundary walls, secure cantonment environment with strict security checkpoints.''',
            'property_type': 'House',
            'city': 'Multan',
            'area': 'Multan Cantt (Near Bosan Road)',
            'address': 'Officers Lane, Multan Cantt, Multan, Punjab',
            'monthly_rent': 95000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 190000,
            'extra_charges': 'Cantt Board charges PKR 3,000 / month',
            'bedrooms': 5,
            'bathrooms': 5,
            'size': 1,
            'size_unit': 'Kanal',
            'furnished': 'Unfurnished',
            'floor_level': 'Ground + 1',
            'parking_spaces': 3,
            'facilities': ['Lawn / Garden', 'Secure Cantt Location', 'Sui Gas Active', 'MEPCO 3-Phase Connection', 'Servant Quarters', 'Car Porch'],
            'images': [
                'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 30.1984,
            'longitude': 71.4687,
            'contact_name': 'Chaudhry Nadeem (Multan Real Estate)',
            'contact_phone': '+92 302 7711223',
            'contact_whatsapp': '+92 302 7711223',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 175
        },

        # 15. Faisalabad - Kohinoor City 2-Bed Flat
        {
            'user_id': usman_id,
            'title': '2-Bed Modern Apartment in Kohinoor City near D Ground',
            'description': '''Comfortable 2-bedroom apartment in Kohinoor City Faisalabad, adjacent to D Ground commercial center.
Featuring ceramic tile flooring, drawing room, kitchen with granite counter, balcony, and elevator access.
Safe family environment with 24/7 security guard and generator backup for lifts and stairs.''',
            'property_type': 'Flat',
            'city': 'Faisalabad',
            'area': 'Kohinoor City / D Ground',
            'address': 'Kohinoor Heights, Jaranwala Road, Faisalabad',
            'monthly_rent': 42000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 84000,
            'extra_charges': 'Maintenance: PKR 4,000 / month',
            'bedrooms': 2,
            'bathrooms': 2,
            'size': 950,
            'size_unit': 'Sq Ft',
            'furnished': 'Semi-Furnished',
            'floor_level': '2nd Floor',
            'parking_spaces': 1,
            'facilities': ['Elevator / Lift', 'Standby Generator for Lifts', 'Sui Gas Active', 'FESCO Electricity', 'Near D Ground Market', 'Security Guard'],
            'images': [
                'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 31.4187,
            'longitude': 73.0791,
            'contact_name': 'Mian Shahid Property Advisor',
            'contact_phone': '+92 300 6655443',
            'contact_whatsapp': '+92 300 6655443',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 130
        },

        # 16. Islamabad - I-8/4 Studio Room for Professional
        {
            'user_id': bukhari_id,
            'title': 'Independent Furnished Studio Room with Bath & Kitchenette in I-8/4',
            'description': '''Well-maintained independent studio accommodation in Sector I-8/4 Islamabad, ideal for working executive, doctor or university scholar.
Fully furnished with bed, study table, wardrobe, mini fridge, inverter split AC, and attached modern bath with geyser.
Walking distance to I-8 Markaz, metro bus station, and lush green family park.''',
            'property_type': 'Room',
            'city': 'Islamabad',
            'area': 'Sector I-8/4',
            'address': 'Street 12, Sector I-8/4, Islamabad',
            'monthly_rent': 28000,
            'advance_payment': '1 Month Advance',
            'security_deposit': 50000,
            'extra_charges': 'All bills inclusive (Electricity, Gas, Fast Wi-Fi)',
            'bedrooms': 1,
            'bathrooms': 1,
            'size': 350,
            'size_unit': 'Sq Ft',
            'furnished': 'Furnished',
            'floor_level': 'Ground Floor (Independent Entrance)',
            'parking_spaces': 1,
            'facilities': ['Furnished with Bed & Wardrobe', 'Inverter Split AC', 'High-Speed Wi-Fi', 'Attached Bathroom with Geyser', 'Walking Distance to Metro Bus', 'All Utility Bills Included'],
            'images': [
                'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 33.6681,
            'longitude': 73.0754,
            'contact_name': 'Syed Farhan Bukhari',
            'contact_phone': '+92 333 5511223',
            'contact_whatsapp': '+92 333 5511223',
            'status': 'approved',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 260
        },

        # 17. Pending Property (Demonstrates Admin Approval Workflow)
        {
            'user_id': bukhari_id,
            'title': 'Brand New 4-Bed Flat in G-11/3 Waiting for Admin Review',
            'description': '''Recently completed luxury apartment in Sector G-11/3 Islamabad. 4 bedrooms, 4 bathrooms, spacious drawing dining, standby generator and reserved parking slot. Undergoing landlord review.''',
            'property_type': 'Flat',
            'city': 'Islamabad',
            'area': 'Sector G-11/3',
            'address': 'Margalla Heights, Sector G-11/3, Islamabad',
            'monthly_rent': 90000,
            'advance_payment': '2 Months Advance',
            'security_deposit': 180000,
            'extra_charges': 'Maintenance: PKR 5,000 / month',
            'bedrooms': 4,
            'bathrooms': 4,
            'size': 1800,
            'size_unit': 'Sq Ft',
            'furnished': 'Unfurnished',
            'floor_level': '3rd Floor',
            'parking_spaces': 1,
            'facilities': ['Elevator / Lift', 'Standby Generator', 'Sui Gas Active', 'IESCO Electricity', 'Balcony'],
            'images': [
                'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80'
            ],
            'latitude': 33.6689,
            'longitude': 73.0034,
            'contact_name': 'Syed Farhan Bukhari',
            'contact_phone': '+92 333 5511223',
            'contact_whatsapp': '+92 333 5511223',
            'status': 'pending',
            'is_featured': 0,
            'is_sponsored': 0,
            'views_count': 12
        }
    ]

    for p in properties_data:
        cursor.execute('''
            INSERT INTO properties (
                user_id, title, description, property_type, city, area, address,
                monthly_rent, advance_payment, security_deposit, extra_charges,
                bedrooms, bathrooms, size, size_unit, furnished, floor_level,
                parking_spaces, facilities, images, latitude, longitude,
                contact_name, contact_phone, contact_whatsapp, status, is_featured, is_sponsored, views_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p['user_id'], p['title'], p['description'], p['property_type'], p['city'], p['area'], p['address'],
            p['monthly_rent'], p['advance_payment'], p['security_deposit'], p['extra_charges'],
            p['bedrooms'], p['bathrooms'], p['size'], p['size_unit'], p['furnished'], p['floor_level'],
            p['parking_spaces'], json.dumps(p['facilities']), json.dumps(p['images']), p['latitude'], p['longitude'],
            p['contact_name'], p['contact_phone'], p['contact_whatsapp'], p['status'], p['is_featured'], p.get('is_sponsored', 0), p['views_count']
        ))
    conn.commit()

    # Get sample property IDs
    cursor.execute("SELECT id FROM properties WHERE status = 'approved' LIMIT 5")
    sample_pids = [r['id'] for r in cursor.fetchall()]

    if sample_pids:
        # Sample Favorites for Tenant
        cursor.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (tenant_id, sample_pids[0]))
        cursor.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (tenant_id, sample_pids[1]))

        # Sample Enquiry
        cursor.execute('''
            INSERT INTO enquiries (property_id, sender_id, sender_name, sender_email, sender_phone, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            sample_pids[0], tenant_id, 'Hamza Rafique', 'hamza.tenant@gmail.com', '+92 345 1122334',
            'Assalam-o-Alaikum, is this Clifton apartment still available for rent? Can we schedule a physical visit this Saturday afternoon?'
        ))

        # Sample Viewing Appointment
        cursor.execute('''
            INSERT INTO viewing_appointments (property_id, user_id, visitor_name, visitor_phone, visitor_email, preferred_date, time_slot, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sample_pids[1], tenant_id, 'Hamza Rafique', '+92 345 1122334', 'hamza.tenant@gmail.com',
            '2026-11-20', 'Afternoon (12 PM - 4 PM)', 'Interested in moving by end of month with family.', 'pending'
        ))

        # Sample Report
        cursor.execute('''
            INSERT INTO property_reports (property_id, reporter_id, reporter_email, reason, details, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            sample_pids[2], tenant_id, 'hamza.tenant@gmail.com', 'Wrong Price / Rent',
            'The rent in the advertisement was originally listed slightly differently on another board, please verify.', 'pending'
        ))

        # Monetization: Subscriptions seed
        now = datetime.now()
        thirty_days = now + timedelta(days=30)
        cursor.execute('''
            INSERT INTO subscriptions (user_id, plan_name, amount, payment_method, transaction_ref, status, listing_limit, started_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            usman_id, 'Platinum Agency', 15000, 'JazzCash', 'JC-992817441', 'active', 50,
            now.strftime('%Y-%m-%d %H:%M:%S'), thirty_days.strftime('%Y-%m-%d %H:%M:%S')
        ))
        cursor.execute('''
            INSERT INTO subscriptions (user_id, plan_name, amount, payment_method, transaction_ref, status, listing_limit, started_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bukhari_id, 'Gold Landlord', 7500, 'Easypaisa', 'EP-334182910', 'active', 20,
            now.strftime('%Y-%m-%d %H:%M:%S'), thirty_days.strftime('%Y-%m-%d %H:%M:%S')
        ))

        # Monetization: Payments seed
        cursor.execute('''
            INSERT INTO payments (user_id, property_id, payment_type, amount, payment_method, account_number, transaction_id, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            usman_id, sample_pids[0], 'featured_listing', 3500, 'JazzCash', '03214455667', 'TID-88219401', 'approved', 'Home Page Spotlight Featured Badge for 30 Days'
        ))
        cursor.execute('''
            INSERT INTO payments (user_id, property_id, payment_type, amount, payment_method, account_number, transaction_id, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            usman_id, None, 'subscription', 15000, 'JazzCash', '03214455667', 'TID-992817441', 'approved', 'Monthly Platinum Agency Subscription'
        ))
        cursor.execute('''
            INSERT INTO payments (user_id, property_id, payment_type, amount, payment_method, account_number, transaction_id, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bukhari_id, None, 'subscription', 7500, 'Easypaisa', '03335511223', 'TID-334182910', 'approved', 'Monthly Gold Landlord Subscription'
        ))

        # Monetization: Advertisements seed
        cursor.execute('''
            INSERT INTO advertisements (title, client_name, banner_image, target_url, placement, impressions, clicks, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Al-Habib Home Movers & Packers - 20% Discount for Renters',
            'Al-Habib Logistics Pakistan',
            'https://images.unsplash.com/photo-1600518464441-9154a4dea21b?auto=format&fit=crop&w=1200&q=80',
            'https://rentfinder.pk/services/packers',
            'sidebar',
            1420,
            88,
            'active'
        ))
        cursor.execute('''
            INSERT INTO advertisements (title, client_name, banner_image, target_url, placement, impressions, clicks, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Pak-Solar Home Solutions: Zero Electricity Bills for Your Rental',
            'Pak-Solar Energy Systems',
            'https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=1200&q=80',
            'https://rentfinder.pk/services/solar',
            'home_featured',
            3200,
            245,
            'active'
        ))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully! All demo records, monetization & ads created.")

if __name__ == '__main__':
    seed_all()
