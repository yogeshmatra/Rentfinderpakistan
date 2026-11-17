"""
Rent Finder Pakistan - Main Web Application
Flask backend serving 3D-animated marketplace, API routes, authentication,
monetization, admin panel, and Rent Finder AI.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, jsonify, send_from_directory, abort
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

import database as db
import ai_service

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'rentfinder_pk_secret_key_2026_super_secure')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'properties')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Context Processor for Global Template Variables
@app.context_processor
def inject_global_data():
    settings = db.get_all_settings()
    current_user = None
    saved_count = 0
    if 'user_id' in session:
        current_user = db.find_user_by_id(session['user_id'])
        if current_user:
            conn = db.get_db()
            saved_count = conn.execute("SELECT COUNT(*) as c FROM favorites WHERE user_id = ?", (session['user_id'],)).fetchone()['c']
            conn.close()

    return {
        'site_settings': settings,
        'current_user': current_user,
        'saved_count': saved_count,
        'now': datetime.now()
    }

# Custom Template Filters
@app.template_filter('format_currency')
def format_currency_filter(val):
    try:
        val = int(val)
        if val >= 10000000:
            return f"{val / 10000000:.2f} Crore"
        elif val >= 100000:
            return f"{val / 100000:.2f} Lakh"
        return f"{val:,}"
    except:
        return str(val)

@app.template_filter('from_json')
def from_json_filter(val):
    try:
        return json.loads(val)
    except:
        return []

# Helper: Require Login / Admin
def login_required(role=None):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('login', next=request.path))
            if role:
                user = db.find_user_by_id(session['user_id'])
                if not user or (role == 'admin' and user['role'] != 'admin'):
                    flash("Access denied. Authorized administrators only.", "danger")
                    return redirect(url_for('index'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# -------------------------------------------------------------
# PUBLIC ROUTES
# -------------------------------------------------------------

@app.route('/')
def index():
    conn = db.get_db()
    # Featured approved properties
    featured = conn.execute('''
        SELECT * FROM properties 
        WHERE status = 'approved' AND is_featured = 1 
        ORDER BY id DESC LIMIT 6
    ''').fetchall()

    # If fewer than 6 featured, backfill with top approved
    if len(featured) < 6:
        featured = conn.execute('''
            SELECT * FROM properties 
            WHERE status = 'approved' 
            ORDER BY is_featured DESC, id DESC LIMIT 6
        ''').fetchall()

    # Recent properties
    recent = conn.execute('''
        SELECT * FROM properties 
        WHERE status = 'approved' 
        ORDER BY id DESC LIMIT 8
    ''').fetchall()

    # City counts
    city_counts_raw = conn.execute('''
        SELECT city, COUNT(*) as count 
        FROM properties 
        WHERE status = 'approved' 
        GROUP BY city
    ''').fetchall()
    city_counts = {r['city']: r['count'] for r in city_counts_raw}

    # Sponsored Ads
    hero_ad = conn.execute("SELECT * FROM advertisements WHERE placement = 'home_featured' AND status = 'active' ORDER BY id DESC LIMIT 1").fetchone()

    # Stats
    total_listings = conn.execute("SELECT COUNT(*) as c FROM properties WHERE status = 'approved'").fetchone()['c']
    total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']

    conn.close()

    return render_template(
        'index.html',
        featured_properties=featured,
        recent_properties=recent,
        city_counts=city_counts,
        hero_ad=hero_ad,
        stats={'listings': total_listings, 'users': total_users}
    )

@app.route('/properties')
def properties():
    city = request.args.get('city', '').strip()
    area = request.args.get('area', '').strip()
    prop_type = request.args.get('type', '').strip()
    min_rent = request.args.get('min_rent', '').strip()
    max_rent = request.args.get('max_rent', '').strip()
    bedrooms = request.args.get('bedrooms', '').strip()
    bathrooms = request.args.get('bathrooms', '').strip()
    furnished = request.args.get('furnished', '').strip()
    facility = request.args.get('facility', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()

    sql = "SELECT * FROM properties WHERE status = 'approved'"
    params = []

    if city:
        sql += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if area:
        sql += " AND (LOWER(area) LIKE LOWER(?) OR LOWER(address) LIKE LOWER(?))"
        params.extend([f"%{area}%", f"%{area}%"])
    if prop_type:
        sql += " AND property_type = ?"
        params.append(prop_type)
    if min_rent.isdigit():
        sql += " AND monthly_rent >= ?"
        params.append(int(min_rent))
    if max_rent.isdigit():
        sql += " AND monthly_rent <= ?"
        params.append(int(max_rent))
    if bedrooms.isdigit():
        sql += " AND bedrooms >= ?"
        params.append(int(bedrooms))
    if bathrooms.isdigit():
        sql += " AND bathrooms >= ?"
        params.append(int(bathrooms))
    if furnished and furnished != 'All':
        sql += " AND furnished = ?"
        params.append(furnished)
    if facility:
        sql += " AND facilities LIKE ?"
        params.append(f"%{facility}%")

    if sort_by == 'lowest':
        sql += " ORDER BY monthly_rent ASC"
    elif sort_by == 'highest':
        sql += " ORDER BY monthly_rent DESC"
    else:
        sql += " ORDER BY is_featured DESC, id DESC"

    conn = db.get_db()
    items = conn.execute(sql, params).fetchall()

    # Unique cities and areas for filter dropdowns
    available_cities = [r['city'] for r in conn.execute("SELECT DISTINCT city FROM properties WHERE status = 'approved' ORDER BY city").fetchall()]
    available_types = ['House', 'Flat', 'Room', 'Upper Portion', 'Lower Portion', 'Complete Portion', 'Shop', 'Office', 'Penthouse']

    # Sidebar Ad
    sidebar_ad = conn.execute("SELECT * FROM advertisements WHERE placement = 'sidebar' AND status = 'active' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    return render_template(
        'properties.html',
        properties=items,
        total_count=len(items),
        selected_city=city,
        selected_area=area,
        selected_type=prop_type,
        min_rent=min_rent,
        max_rent=max_rent,
        selected_bedrooms=bedrooms,
        selected_bathrooms=bathrooms,
        selected_furnished=furnished,
        selected_facility=facility,
        selected_sort=sort_by,
        available_cities=available_cities,
        available_types=available_types,
        sidebar_ad=sidebar_ad
    )

@app.route('/properties/<int:prop_id>')
def property_detail(prop_id):
    conn = db.get_db()
    prop = conn.execute("SELECT * FROM properties WHERE id = ?", (prop_id,)).fetchone()
    if not prop:
        conn.close()
        abort(404)

    # Increment view count
    conn.execute("UPDATE properties SET views_count = views_count + 1 WHERE id = ?", (prop_id,))
    conn.commit()

    # Get owner/agent info
    owner = conn.execute("SELECT id, name, email, phone, whatsapp, role, is_verified, avatar, bio, created_at FROM users WHERE id = ?", (prop['user_id'],)).fetchone()

    # Similar properties in the same city or type
    similar = conn.execute('''
        SELECT * FROM properties 
        WHERE status = 'approved' AND id != ? AND (city = ? OR property_type = ?)
        ORDER BY is_featured DESC, id DESC LIMIT 3
    ''', (prop_id, prop['city'], prop['property_type'])).fetchall()

    # Check if favorited by current user
    is_favorite = False
    if 'user_id' in session:
        fav = conn.execute("SELECT id FROM favorites WHERE user_id = ? AND property_id = ?", (session['user_id'], prop_id)).fetchone()
        is_favorite = bool(fav)

    conn.close()

    return render_template(
        'property_detail.html',
        property=prop,
        owner=owner,
        similar_properties=similar,
        is_favorite=is_favorite
    )

# -------------------------------------------------------------
# PROPERTY ACTIONS (Appointments, Enquiries, Reports)
# -------------------------------------------------------------

@app.route('/properties/<int:prop_id>/enquire', methods=['POST'])
def submit_enquiry(prop_id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    message = request.form.get('message', '').strip()

    if not (name and email and phone and message):
        flash("All fields are required to send an enquiry.", "danger")
        return redirect(url_for('property_detail', prop_id=prop_id))

    sender_id = session.get('user_id')
    conn = db.get_db()
    conn.execute('''
        INSERT INTO enquiries (property_id, sender_id, sender_name, sender_email, sender_phone, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (prop_id, sender_id, name, email, phone, message))
    conn.commit()
    conn.close()

    flash("Your inquiry has been submitted! The landlord / agent will contact you shortly.", "success")
    return redirect(url_for('property_detail', prop_id=prop_id))

@app.route('/properties/<int:prop_id>/appointment', methods=['POST'])
def book_appointment(prop_id):
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    date = request.form.get('preferred_date', '').strip()
    slot = request.form.get('time_slot', 'Morning (9 AM - 12 PM)').strip()
    notes = request.form.get('notes', '').strip()

    if not (name and phone and date):
        flash("Please provide your name, phone number, and preferred date.", "danger")
        return redirect(url_for('property_detail', prop_id=prop_id))

    user_id = session.get('user_id')
    conn = db.get_db()
    conn.execute('''
        INSERT INTO viewing_appointments (property_id, user_id, visitor_name, visitor_phone, visitor_email, preferred_date, time_slot, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', (prop_id, user_id, name, phone, email, date, slot, notes))
    conn.commit()
    conn.close()

    flash("Viewing appointment requested successfully! The owner will confirm via call / WhatsApp.", "success")
    return redirect(url_for('property_detail', prop_id=prop_id))

@app.route('/properties/<int:prop_id>/report', methods=['POST'])
def report_property(prop_id):
    reason = request.form.get('reason', 'Other').strip()
    details = request.form.get('details', '').strip()
    email = request.form.get('email', '').strip()

    reporter_id = session.get('user_id')
    conn = db.get_db()
    conn.execute('''
        INSERT INTO property_reports (property_id, reporter_id, reporter_email, reason, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (prop_id, reporter_id, email, reason, details))
    conn.commit()
    conn.close()

    flash("Thank you for your report. Our trust & safety moderation team will investigate this listing.", "info")
    return redirect(url_for('property_detail', prop_id=prop_id))

# -------------------------------------------------------------
# POST PROPERTY (Landlord / Agent submission)
# -------------------------------------------------------------

@app.route('/post-property', methods=['GET', 'POST'])
def post_property():
    if 'user_id' not in session:
        flash("Please log in or register as a Landlord / Agent to post your property.", "warning")
        return redirect(url_for('login', next=url_for('post_property')))

    if request.method == 'POST':
        user_id = session['user_id']
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        prop_type = request.form.get('property_type', 'Flat').strip()
        city = request.form.get('city', 'Karachi').strip()
        area = request.form.get('area', '').strip()
        address = request.form.get('address', '').strip()
        monthly_rent = request.form.get('monthly_rent', '0').strip()
        advance_payment = request.form.get('advance_payment', '2 Months Advance').strip()
        security_deposit = request.form.get('security_deposit', '0').strip()
        extra_charges = request.form.get('extra_charges', 'Utilities separate').strip()
        bedrooms = request.form.get('bedrooms', '0').strip()
        bathrooms = request.form.get('bathrooms', '0').strip()
        size = request.form.get('size', '0').strip()
        size_unit = request.form.get('size_unit', 'Marla').strip()
        furnished = request.form.get('furnished', 'Unfurnished').strip()
        floor_level = request.form.get('floor_level', 'Ground Floor').strip()
        parking_spaces = request.form.get('parking_spaces', '0').strip()
        contact_name = request.form.get('contact_name', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        contact_whatsapp = request.form.get('contact_whatsapp', '').strip()

        # Facilities selected
        facilities = request.form.getlist('facilities')

        # Validation
        if not (title and description and city and area and monthly_rent.isdigit()):
            flash("Please fill in all mandatory fields with valid values.", "danger")
            return redirect(url_for('post_property'))

        monthly_rent_val = int(monthly_rent)

        # Duplicate listing prevention
        if db.check_duplicate_property(user_id, title, city, area, monthly_rent_val):
            flash("A property listing with identical title, location and rent already exists under your account.", "danger")
            return redirect(url_for('post_property'))

        # Handle uploaded images
        images_list = []
        uploaded_files = request.files.getlist('images')
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_name = f"prop_{uuid.uuid4().hex[:12]}.{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                file.save(save_path)
                images_list.append(f"/static/uploads/properties/{unique_name}")

        # Optional manual image URLs
        manual_urls = request.form.get('image_urls', '').strip()
        if manual_urls:
            for u in manual_urls.split('\n'):
                u = u.strip()
                if u and u.startswith(('http://', 'https://')):
                    images_list.append(u)

        # Fallback placeholder if no images uploaded
        if not images_list:
            images_list = ['https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80']

        # Coordinates approximation by city
        city_coords = {
            'Karachi': (24.8607, 67.0011),
            'Lahore': (31.5204, 74.3587),
            'Islamabad': (33.6844, 73.0479),
            'Rawalpindi': (33.5651, 73.0169),
            'Faisalabad': (31.4504, 73.1350),
            'Multan': (30.1575, 71.5249),
            'Hyderabad': (25.3960, 68.3578),
            'Peshawar': (34.0151, 71.5249),
            'Quetta': (30.1798, 66.9750),
            'Sukkur': (27.7052, 68.8574)
        }
        lat, lng = city_coords.get(city, (24.8607, 67.0011))

        # Save to DB with 'pending' status for admin approval
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO properties (
                user_id, title, description, property_type, city, area, address,
                monthly_rent, advance_payment, security_deposit, extra_charges,
                bedrooms, bathrooms, size, size_unit, furnished, floor_level,
                parking_spaces, facilities, images, latitude, longitude,
                contact_name, contact_phone, contact_whatsapp, status, is_featured
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 0)
        ''', (
            user_id, title, description, prop_type, city, area, address,
            monthly_rent_val, advance_payment, int(security_deposit) if security_deposit.isdigit() else 0,
            extra_charges, int(bedrooms) if bedrooms.isdigit() else 0, int(bathrooms) if bathrooms.isdigit() else 0,
            float(size) if size.replace('.', '', 1).isdigit() else 0.0, size_unit, furnished, floor_level,
            int(parking_spaces) if parking_spaces.isdigit() else 0,
            json.dumps(facilities), json.dumps(images_list), lat, lng,
            contact_name, contact_phone, contact_whatsapp
        ))
        conn.commit()
        prop_id = cursor.lastrowid
        conn.close()

        flash("Property submitted successfully! Your listing is now pending review and will be published once approved by our moderation team.", "success")
        return redirect(url_for('dashboard_listings'))

    # GET
    return render_template('post_property.html')

# -------------------------------------------------------------
# COMPARE PROPERTIES
# -------------------------------------------------------------

@app.route('/compare')
def compare():
    ids_str = request.args.get('ids', '')
    pids = []
    if ids_str:
        for x in ids_str.split(','):
            if x.strip().isdigit():
                pids.append(int(x.strip()))

    properties_to_compare = []
    if pids:
        conn = db.get_db()
        placeholders = ','.join(['?'] * len(pids))
        properties_to_compare = conn.execute(f"SELECT * FROM properties WHERE id IN ({placeholders}) AND status = 'approved'", pids).fetchall()
        conn.close()

    return render_template('compare.html', properties=properties_to_compare)

# -------------------------------------------------------------
# MONETIZATION & PRICING
# -------------------------------------------------------------

@app.route('/pricing')
def pricing():
    settings = db.get_all_settings()
    return render_template('pricing.html', settings=settings)

@app.route('/api/payments/submit', methods=['POST'])
def submit_payment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first.'}), 401

    user_id = session['user_id']
    payment_type = request.form.get('payment_type', 'featured_listing')
    amount = request.form.get('amount', '3500')
    payment_method = request.form.get('payment_method', 'Easypaisa')
    account_number = request.form.get('account_number', '')
    transaction_id = request.form.get('transaction_id', '').strip()
    property_id = request.form.get('property_id')
    notes = request.form.get('notes', '')

    if not transaction_id:
        return jsonify({'success': False, 'message': 'Transaction ID / Reference Number is required.'}), 400

    conn = db.get_db()
    conn.execute('''
        INSERT INTO payments (user_id, property_id, payment_type, amount, payment_method, account_number, transaction_id, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    ''', (user_id, int(property_id) if property_id and property_id.isdigit() else None, payment_type, int(amount) if amount.isdigit() else 3500, payment_method, account_number, transaction_id, notes))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Payment submitted for verification! Our billing team will verify your transaction within 30 minutes and activate your feature.'
    })

# -------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        user = db.find_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            if not user['is_active']:
                flash("Your account has been deactivated. Please contact support.", "danger")
                return redirect(url_for('login'))

            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please check your credentials.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        phone = request.form.get('phone', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        city = request.form.get('city', 'Karachi').strip()
        role = request.form.get('role', 'user').strip()

        if not (name and email and password):
            flash("Name, email, and password are required.", "danger")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for('register'))

        existing = db.find_user_by_email(email)
        if existing:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        user_id = db.create_user(name, email, password, phone, whatsapp, city, role)
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            session['user_role'] = role
            flash("Account registered successfully! Welcome to Rent Finder Pakistan.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Registration failed. Please try again.", "danger")

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out securely.", "info")
    return redirect(url_for('index'))

# -------------------------------------------------------------
# USER DASHBOARD
# -------------------------------------------------------------

@app.route('/dashboard')
@login_required()
def dashboard():
    user_id = session['user_id']
    conn = db.get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    # User's listings count
    my_listings_count = conn.execute("SELECT COUNT(*) as c FROM properties WHERE user_id = ?", (user_id,)).fetchone()['c']
    saved_count = conn.execute("SELECT COUNT(*) as c FROM favorites WHERE user_id = ?", (user_id,)).fetchone()['c']
    enquiries_count = conn.execute("SELECT COUNT(*) as c FROM enquiries WHERE sender_id = ?", (user_id,)).fetchone()['c']
    appointments_count = conn.execute("SELECT COUNT(*) as c FROM viewing_appointments WHERE user_id = ?", (user_id,)).fetchone()['c']

    # Active subscription
    active_sub = conn.execute("SELECT * FROM subscriptions WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()

    # Recent activities
    recent_enquiries = conn.execute('''
        SELECT e.*, p.title as property_title 
        FROM enquiries e 
        JOIN properties p ON e.property_id = p.id 
        WHERE e.sender_id = ? 
        ORDER BY e.id DESC LIMIT 4
    ''', (user_id,)).fetchall()

    conn.close()

    return render_template(
        'dashboard/overview.html',
        user=user,
        stats={
            'listings': my_listings_count,
            'saved': saved_count,
            'enquiries': enquiries_count,
            'appointments': appointments_count
        },
        active_sub=active_sub,
        recent_enquiries=recent_enquiries
    )

@app.route('/dashboard/listings')
@login_required()
def dashboard_listings():
    user_id = session['user_id']
    conn = db.get_db()
    listings = conn.execute("SELECT * FROM properties WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    return render_template('dashboard/listings.html', listings=listings)

@app.route('/dashboard/favorites')
@login_required()
def dashboard_favorites():
    user_id = session['user_id']
    conn = db.get_db()
    favorites = conn.execute('''
        SELECT p.* 
        FROM favorites f 
        JOIN properties p ON f.property_id = p.id 
        WHERE f.user_id = ? 
        ORDER BY f.id DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return render_template('dashboard/favorites.html', favorites=favorites)

@app.route('/dashboard/enquiries')
@login_required()
def dashboard_enquiries():
    user_id = session['user_id']
    conn = db.get_db()
    # Outgoing inquiries (sent by tenant)
    sent_enquiries = conn.execute('''
        SELECT e.*, p.title as prop_title, p.city as prop_city 
        FROM enquiries e 
        JOIN properties p ON e.property_id = p.id 
        WHERE e.sender_id = ? 
        ORDER BY e.id DESC
    ''', (user_id,)).fetchall()

    # Incoming inquiries (received by landlord/agent on their properties)
    received_enquiries = conn.execute('''
        SELECT e.*, p.title as prop_title 
        FROM enquiries e 
        JOIN properties p ON e.property_id = p.id 
        WHERE p.user_id = ? 
        ORDER BY e.id DESC
    ''', (user_id,)).fetchall()
    conn.close()

    return render_template('dashboard/enquiries.html', sent=sent_enquiries, received=received_enquiries)

@app.route('/dashboard/appointments')
@login_required()
def dashboard_appointments():
    user_id = session['user_id']
    conn = db.get_db()
    # Booked by user
    my_appointments = conn.execute('''
        SELECT a.*, p.title as prop_title, p.city as prop_city, p.contact_phone 
        FROM viewing_appointments a 
        JOIN properties p ON a.property_id = p.id 
        WHERE a.user_id = ? 
        ORDER BY a.id DESC
    ''', (user_id,)).fetchall()

    # Received by landlord
    received_appointments = conn.execute('''
        SELECT a.*, p.title as prop_title 
        FROM viewing_appointments a 
        JOIN properties p ON a.property_id = p.id 
        WHERE p.user_id = ? 
        ORDER BY a.id DESC
    ''', (user_id,)).fetchall()
    conn.close()

    return render_template('dashboard/appointments.html', booked=my_appointments, received=received_appointments)

@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required()
def dashboard_profile():
    user_id = session['user_id']
    conn = db.get_db()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        city = request.form.get('city', 'Karachi').strip()
        bio = request.form.get('bio', '').strip()

        conn.execute('''
            UPDATE users SET name = ?, phone = ?, whatsapp = ?, city = ?, bio = ?
            WHERE id = ?
        ''', (name, phone, whatsapp, city, bio, user_id))
        conn.commit()
        session['user_name'] = name
        flash("Your profile information has been updated.", "success")

    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return render_template('dashboard/profile.html', user=user)

# -------------------------------------------------------------
# AJAX FAVORITES API
# -------------------------------------------------------------

@app.route('/api/favorites/toggle', methods=['POST'])
def toggle_favorite():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to save favorites.'}), 401

    data = request.get_json() or {}
    prop_id = data.get('property_id')
    if not prop_id:
        return jsonify({'success': False, 'message': 'Invalid property ID'}), 400

    user_id = session['user_id']
    conn = db.get_db()
    existing = conn.execute("SELECT id FROM favorites WHERE user_id = ? AND property_id = ?", (user_id, prop_id)).fetchone()

    if existing:
        conn.execute("DELETE FROM favorites WHERE id = ?", (existing['id'],))
        is_saved = False
        msg = "Property removed from saved list."
    else:
        conn.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (user_id, prop_id))
        is_saved = True
        msg = "Property added to saved favorites!"

    conn.commit()
    count = conn.execute("SELECT COUNT(*) as c FROM favorites WHERE user_id = ?", (user_id,)).fetchone()['c']
    conn.close()

    return jsonify({'success': True, 'is_saved': is_saved, 'message': msg, 'total_saved': count})

# -------------------------------------------------------------
# RENT FINDER AI CHATBOT API (GEMINI INTEGRATION)
# -------------------------------------------------------------

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('sessionId', 'guest_' + request.remote_addr)
    user_id = session.get('user_id')

    if not message:
        return jsonify({'success': False, 'error': 'Message cannot be empty.'}), 400

    # Retrieve recent chat history for this session
    conn = db.get_db()
    recent_history = conn.execute('''
        SELECT role, content FROM chat_messages 
        WHERE session_id = ? 
        ORDER BY id DESC LIMIT 6
    ''', (session_id,)).fetchall()
    conn.close()

    history_list = [{'role': r['role'], 'content': r['content']} for r in reversed(recent_history)]

    # Process message via AI Service
    response_data = ai_service.process_chat_message(
        user_message=message,
        session_id=session_id,
        user_id=user_id,
        chat_history=history_list
    )

    return jsonify({
        'success': True,
        'response': response_data['text'],
        'properties': response_data['properties']
    })

@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    session_id = request.args.get('sessionId', 'guest_' + request.remote_addr)
    conn = db.get_db()
    messages = conn.execute('''
        SELECT id, role, content, properties_json, created_at 
        FROM chat_messages 
        WHERE session_id = ? 
        ORDER BY id ASC LIMIT 50
    ''', (session_id,)).fetchall()
    conn.close()

    result = []
    for m in messages:
        props = []
        if m['properties_json']:
            try:
                props = json.loads(m['properties_json'])
            except:
                props = []
        result.append({
            'id': m['id'],
            'role': m['role'],
            'content': m['content'],
            'properties': props,
            'time': m['created_at']
        })

    return jsonify({'success': True, 'history': result})

# -------------------------------------------------------------
# ADMIN PANEL ROUTES
# -------------------------------------------------------------

@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    conn = db.get_db()

    total_props = conn.execute("SELECT COUNT(*) as c FROM properties").fetchone()['c']
    approved_props = conn.execute("SELECT COUNT(*) as c FROM properties WHERE status = 'approved'").fetchone()['c']
    pending_props = conn.execute("SELECT COUNT(*) as c FROM properties WHERE status = 'pending'").fetchone()['c']
    rejected_props = conn.execute("SELECT COUNT(*) as c FROM properties WHERE status = 'rejected'").fetchone()['c']

    total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    total_landlords = conn.execute("SELECT COUNT(*) as c FROM users WHERE role IN ('landlord', 'agent')").fetchone()['c']
    total_enquiries = conn.execute("SELECT COUNT(*) as c FROM enquiries").fetchone()['c']
    total_appointments = conn.execute("SELECT COUNT(*) as c FROM viewing_appointments").fetchone()['c']
    total_reports = conn.execute("SELECT COUNT(*) as c FROM property_reports WHERE status = 'pending'").fetchone()['c']

    # Total Revenue Calculation
    rev_row = conn.execute("SELECT SUM(amount) as s FROM payments WHERE status = 'approved'").fetchone()
    total_revenue = rev_row['s'] if rev_row['s'] else 0

    # Recent pending properties requiring attention
    pending_list = conn.execute('''
        SELECT p.*, u.name as owner_name, u.email as owner_email 
        FROM properties p 
        JOIN users u ON p.user_id = u.id 
        WHERE p.status = 'pending' 
        ORDER BY p.id DESC LIMIT 5
    ''').fetchall()

    # Recent payments
    recent_payments = conn.execute('''
        SELECT p.*, u.name as user_name 
        FROM payments p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.id DESC LIMIT 5
    ''').fetchall()

    conn.close()

    return render_template(
        'admin/dashboard.html',
        stats={
            'total_properties': total_props,
            'approved_properties': approved_props,
            'pending_properties': pending_props,
            'rejected_properties': rejected_props,
            'total_users': total_users,
            'total_landlords': total_landlords,
            'total_enquiries': total_enquiries,
            'total_appointments': total_appointments,
            'total_reports': total_reports,
            'total_revenue': total_revenue
        },
        pending_properties=pending_list,
        recent_payments=recent_payments
    )

@app.route('/admin/properties')
@login_required(role='admin')
def admin_properties():
    status_filter = request.args.get('status', 'all')
    sql = '''
        SELECT p.*, u.name as owner_name, u.email as owner_email 
        FROM properties p 
        JOIN users u ON p.user_id = u.id
    '''
    params = []
    if status_filter != 'all':
        sql += " WHERE p.status = ?"
        params.append(status_filter)

    sql += " ORDER BY p.id DESC"

    conn = db.get_db()
    items = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template('admin/properties.html', properties=items, current_status=status_filter)

@app.route('/admin/properties/<int:prop_id>/status', methods=['POST'])
@login_required(role='admin')
def admin_change_property_status(prop_id):
    new_status = request.form.get('status', 'approved')
    reason = request.form.get('reason', '')

    conn = db.get_db()
    conn.execute('''
        UPDATE properties SET status = ?, rejection_reason = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (new_status, reason, prop_id))
    conn.commit()
    conn.close()

    flash(f"Property #{prop_id} status updated to '{new_status}'.", "success")
    return redirect(request.referrer or url_for('admin_properties'))

@app.route('/admin/properties/<int:prop_id>/toggle-featured', methods=['POST'])
@login_required(role='admin')
def admin_toggle_featured(prop_id):
    conn = db.get_db()
    prop = conn.execute("SELECT is_featured FROM properties WHERE id = ?", (prop_id,)).fetchone()
    if prop:
        new_val = 0 if prop['is_featured'] else 1
        conn.execute("UPDATE properties SET is_featured = ? WHERE id = ?", (new_val, prop_id))
        conn.commit()
        flash(f"Featured status for Property #{prop_id} toggled to {'Featured' if new_val else 'Standard'}.", "success")
    conn.close()
    return redirect(request.referrer or url_for('admin_properties'))

@app.route('/admin/properties/<int:prop_id>/delete', methods=['POST'])
@login_required(role='admin')
def admin_delete_property(prop_id):
    conn = db.get_db()
    conn.execute("DELETE FROM properties WHERE id = ?", (prop_id,))
    conn.commit()
    conn.close()
    flash(f"Property #{prop_id} has been permanently deleted.", "info")
    return redirect(url_for('admin_properties'))

@app.route('/admin/users')
@login_required(role='admin')
def admin_users():
    conn = db.get_db()
    users = conn.execute('''
        SELECT u.*, COUNT(p.id) as property_count 
        FROM users u 
        LEFT JOIN properties p ON u.id = p.user_id 
        GROUP BY u.id 
        ORDER BY u.id DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle-verify', methods=['POST'])
@login_required(role='admin')
def admin_toggle_user_verified(user_id):
    conn = db.get_db()
    user = conn.execute("SELECT is_verified FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        new_val = 0 if user['is_verified'] else 1
        conn.execute("UPDATE users SET is_verified = ? WHERE id = ?", (new_val, user_id))
        conn.commit()
        flash(f"User #{user_id} verification badge toggled to {'Verified' if new_val else 'Unverified'}.", "success")
    conn.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/reports')
@login_required(role='admin')
def admin_reports():
    conn = db.get_db()
    reports = conn.execute('''
        SELECT r.*, p.title as prop_title, p.city as prop_city 
        FROM property_reports r 
        JOIN properties p ON r.property_id = p.id 
        ORDER BY r.id DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/reports.html', reports=reports)

@app.route('/admin/reports/<int:report_id>/resolve', methods=['POST'])
@login_required(role='admin')
def admin_resolve_report(report_id):
    action = request.form.get('action', 'dismiss')  # 'dismiss' or 'suspend_property'
    conn = db.get_db()
    rep = conn.execute("SELECT property_id FROM property_reports WHERE id = ?", (report_id,)).fetchone()
    if rep:
        if action == 'suspend_property':
            conn.execute("UPDATE properties SET status = 'rejected', rejection_reason = 'Suspended due to verified violation report.' WHERE id = ?", (rep['property_id'],))
            conn.execute("UPDATE property_reports SET status = 'resolved' WHERE id = ?", (report_id,))
            flash("Property listing suspended and report resolved.", "success")
        else:
            conn.execute("UPDATE property_reports SET status = 'dismissed' WHERE id = ?", (report_id,))
            flash("Report dismissed.", "info")
        conn.commit()
    conn.close()
    return redirect(url_for('admin_reports'))

@app.route('/admin/monetization')
@login_required(role='admin')
def admin_monetization():
    conn = db.get_db()
    payments = conn.execute('''
        SELECT p.*, u.name as user_name, u.email as user_email, pr.title as prop_title 
        FROM payments p 
        JOIN users u ON p.user_id = u.id 
        LEFT JOIN properties pr ON p.property_id = pr.id 
        ORDER BY p.id DESC
    ''').fetchall()

    subscriptions = conn.execute('''
        SELECT s.*, u.name as user_name, u.email as user_email 
        FROM subscriptions s 
        JOIN users u ON s.user_id = u.id 
        ORDER BY s.id DESC
    ''').fetchall()
    conn.close()

    return render_template('admin/monetization.html', payments=payments, subscriptions=subscriptions)

@app.route('/admin/payments/<int:pay_id>/status', methods=['POST'])
@login_required(role='admin')
def admin_payment_status(pay_id):
    new_status = request.form.get('status', 'approved')
    conn = db.get_db()
    conn.execute("UPDATE payments SET status = ? WHERE id = ?", (new_status, pay_id))
    # If approved and was featured_listing, enable is_featured on the property
    if new_status == 'approved':
        pay = conn.execute("SELECT property_id, payment_type FROM payments WHERE id = ?", (pay_id,)).fetchone()
        if pay and pay['property_id'] and pay['payment_type'] == 'featured_listing':
            conn.execute("UPDATE properties SET is_featured = 1 WHERE id = ?", (pay['property_id'],))
    conn.commit()
    conn.close()
    flash(f"Payment #{pay_id} marked as {new_status}.", "success")
    return redirect(url_for('admin_monetization'))

@app.route('/admin/ads', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_ads():
    conn = db.get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        client = request.form.get('client_name', '').strip()
        banner = request.form.get('banner_image', '').strip()
        target = request.form.get('target_url', '').strip()
        placement = request.form.get('placement', 'sidebar').strip()

        if title and banner and target:
            conn.execute('''
                INSERT INTO advertisements (title, client_name, banner_image, target_url, placement)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, client, banner, target, placement))
            conn.commit()
            flash("Advertisement banner created successfully!", "success")

    ads = conn.execute("SELECT * FROM advertisements ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin/ads.html', ads=ads)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_settings():
    if request.method == 'POST':
        keys = [
            'site_name', 'site_tagline', 'contact_email', 'contact_phone', 'whatsapp_number',
            'office_address', 'announcement_bar', 'gemini_api_key', 'gemini_model',
            'featured_listing_fee', 'easypaisa_number', 'easypaisa_title',
            'jazzcash_number', 'jazzcash_title', 'bank_name', 'bank_account',
            'bank_iban', 'bank_title'
        ]
        for k in keys:
            if k in request.form:
                db.set_setting(k, request.form[k].strip())

        flash("Website and AI settings saved successfully!", "success")
        return redirect(url_for('admin_settings'))

    settings = db.get_all_settings()
    return render_template('admin/settings.html', settings=settings)

# -------------------------------------------------------------
# STATIC & INFO PAGES
# -------------------------------------------------------------

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash("Thank you for reaching out! Our team in Karachi will reply to your message within 24 hours.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# -------------------------------------------------------------
# APPLICATION ENTRYPOINT
# -------------------------------------------------------------

if __name__ == '__main__':
    db.init_db()
    print("=" * 60)
    print(" Rent Finder Pakistan Server Running on http://127.0.0.1:5000")
    print(" Admin Login: admin@rentfinder.pk | admin123")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
