# Rent Finder Pakistan 🇵🇰
> **Find Your Perfect Rental Home.**  
> Pakistan's Dedicated 3D-Animated Rental Property Marketplace & Gemini AI Platform.

---

## 🌟 Overview & Concept

**Rent Finder Pakistan** (`rentfinder.pk`) is an online rental property marketplace built specifically for Pakistani tenants, families, students, landlords, and real estate agencies. 

Unlike generic real estate portals focused on land/plot investments, Rent Finder Pakistan specializes exclusively in residential and commercial **rentals**—featuring houses, luxury flats, independent portions, rooms, retail shops, and commercial office suites across Karachi, Lahore, Islamabad, Rawalpindi, Hyderabad, Multan, Faisalabad, Peshawar, and Quetta.

---

## 🎨 Visual Design & 3D Engineering (Pinterest Research Inspired)

Inspired by the **USTA Agency** WebGL particle visual direction identified in the Pinterest reference research (`pin/621989398580723128`), the platform incorporates:
- **Obsidian Architectural Canvas:** Deep space black (`#06080E`) with blueprint dot-matrix grid overlay.
- **Dual Accent System:** Glowing Emerald Green (`#10B981` / Pakistani heritage) & Electric Cyan (`#00C8FF` / tech-forward trust).
- **Interactive 3D WebGL Hero Canvas:** Thousands of glowing particles and constellation wireframe lines reacting smoothly to cursor movement with momentum dampening.
- **3D Card Perspective Tilt:** Property cards respond dynamically in 3D space (`perspective(1000px) rotateX() rotateY() scale3d()`) on mouse hover.
- **Kinetic Ticker Marquee:** Seamless, infinite sliding ticker tapes showcasing major Pakistani cities and trust guarantees.
- **Floating 3D Glass Search Dock:** Glassmorphic floating container with backdrop blur, segmented property type pills, and cascading budget controls.

---

## 🚀 Key Modules & Capabilities

### 1. Advanced Property Search Engine
- Search by Pakistani Cities: Karachi, Lahore, Islamabad, Rawalpindi, Hyderabad, Multan, Faisalabad, Peshawar, Quetta, Sukkur.
- Filter by exact Area / Sector (e.g. DHA, Bahria Town, Gulberg, Clifton, F-7, Johar Town).
- Filter by Property Type: House, Flat / Apartment, Upper Portion, Lower Portion, Complete Portion, Room, Shop, Commercial Office, Penthouse.
- Budget range filtering in PKR (e.g. PKR 15,000 to PKR 500,000+).
- Specific bedroom & bathroom filters, furnishing status, and amenities (Sui Gas, Sweet Water, Standby Generator, Lift, CCTV, Parking).
- Sorting by Newest First, Lowest Rent, and Highest Rent.

### 2. Comprehensive Property Details
- High-definition image gallery with interactive thumbnail switcher.
- Transparent financial breakdown: Monthly rent in PKR, Advance payment (1, 2, or 3 months), and refundable Security deposit.
- Utilities & extra charges disclosure (maintenance fee, separate electric/gas sub-meter details).
- OpenStreetMap interactive vicinity map with exact coordinates.
- Landlord / Agent profile card with verified trust badges.
- **Direct 1-Click WhatsApp Chat:** Automatically opens WhatsApp with a pre-filled message citing the exact property title.
- **Direct Phone Call Button (`tel:`).**
- **Book a Physical Viewing Appointment Modal:** Allows tenants to select a date and preferred time slot (Morning, Afternoon, Evening).
- **Send Direct Message / Enquiry Form:** Stored in the landlord's dashboard.
- **Report Listing Modal:** Allows community reporting of inaccurate rents, already-rented spaces, or fraud.

### 3. Post Your Property (Landlord / Agent Submission Flow)
- Landlords & agents can list properties in minutes.
- Multi-image file uploads with automatic secure storage in `static/uploads/properties/`.
- Duplicate listing prevention algorithm (prevents identical titles and rent within the same locality).
- All submissions default to `status = 'pending'`, entering the admin moderation queue before public publication.

### 4. Side-by-Side Property Comparison
- Compare up to 4 selected rental properties side-by-side in a table comparing rent, advance, deposit, beds, baths, size, furnishing, parking, and contact info.

### 5. RENT FINDER AI (Dual-Capability Google Gemini Chatbot)
The floating 3D bot widget at the bottom-right combines two unified capabilities:
- **Capability A (Property Assistant):** Directly queries the SQLite database in real-time. Matches natural requests like *"Show flats in Karachi under 50k"* or *"Houses in Lahore DHA"*, and renders interactive property cards inside the chat with photos, prices in PKR, and direct links!
- **Capability B (Global AI Assistant like ChatGPT):** Answers questions on Pakistani tenancy law, lease contract requirements, general knowledge, education, programming, mathematics, and business ideas in English, Urdu (اردو), and Roman Urdu.
- **Zero-Crash Resilience:** Works with or without a Gemini API key. If no key is set, the built-in intelligent Pakistani rental NLP engine handles natural language search effortlessly.

### 6. Monetization & Earning Architecture
- **Featured Listing Upgrades:** Landlords can pay PKR 3,500 to spotlight their listing on the homepage and search header for 30 days.
- **Landlord & Dealer Subscriptions:**
  - *Free Landlord Plan:* 2 free listings.
  - *Silver Landlord Plan:* PKR 3,500/month (10 listings, 2 featured badges, WhatsApp lead alerts).
  - *Gold Landlord Plan:* PKR 7,500/month (25 listings, 5 featured badges, verified badge).
  - *Platinum Agency Plan:* PKR 15,000/month (50+ listings, dedicated agency banner, CRM leads).
- **Pakistani Payment Method Integrations:**
  - Easypaisa mobile account
  - JazzCash mobile account
  - Meezan Bank Limited (IBAN transfer)
  - Debit / Credit Cards
- **Instant Payment Proof Verification:** Landlords submit their Transaction ID (TID), allowing admins to verify and activate featured status with 1 click.
- **Sponsored Banner Advertisements:** Dedicated banner placement slots on the homepage and search sidebar.

### 7. Full-Featured Admin Control Panel (`/admin`)
- Accessible only by authorized administrators (`admin@rentfinder.pk` / `admin123`).
- **Dashboard Stats:** Total properties, pending queue, active users, total revenue, viewings booked, reported listings.
- **Property Management:** 1-click Approve, 1-click Reject with customizable reason, Toggle Featured spotlight, Delete property.
- **User Moderation:** View user roles (tenant, landlord, agent), grant/revoke official **Verified Landlord** trust badges.
- **Reports Moderation:** Review community complaints, with action to Dismiss report or Suspend/Remove property.
- **Monetization Console:** Review submitted payment proofs (TIDs) and activate subscriptions.
- **Ad Banner Manager:** Add and manage advertising sponsor banners.
- **System Settings:** Update site name, logo, helpline phone, WhatsApp, office address, announcement bar, Gemini API key, Gemini model, and bank account details directly from the web interface.

---

## 📁 Complete Folder Structure

```
Rent Finder Pakistan/
│
├── app.py                     # Main Flask web application, route handlers, API endpoints
├── database.py                # Database connection, schemas, migrations, helper queries
├── seed_data.py               # Generates realistic Pakistani demo listings, users, monetization
├── ai_service.py              # Rent Finder AI (Gemini REST API + local database search engine)
├── test_app.py                # Comprehensive automated unit & integration test suite (9 tests)
├── requirements.txt           # Python package dependencies (Flask, Werkzeug)
├── .env.example               # Environment variables configuration template
├── run.bat                    # 1-Click Windows server startup batch file
├── README.md                  # Complete documentation and setup manual
│
├── static/
│   ├── css/
│   │   ├── style.css          # Main 3D styles: obsidian canvas, emerald/cyan accents, glassmorphism
│   │   └── admin.css          # Admin panel & user dashboard styling
│   ├── js/
│   │   ├── main.js            # 3D WebGL hero canvas, 3D card tilt, toast alerts, favorites, compare
│   │   └── chatbot.js         # Rent Finder AI floating widget, suggestions, card renderer
│   ├── images/                # Static brand assets and fallback graphics
│   └── uploads/
│       └── properties/        # User-uploaded property photos
│
└── templates/
    ├── base.html              # Master layout with navbar, announcements, chatbot, footer
    ├── index.html             # Homepage: 3D hero, search dock, ticker marquee, featured, cities
    ├── properties.html        # Search & Browse properties with interactive filter sidebar
    ├── property_detail.html   # Full details, gallery, map, contact, appointment & report modals
    ├── post_property.html     # Landlord/agent listing creation form with upload preview
    ├── compare.html           # Side-by-side spec comparison table of up to 4 listings
    ├── pricing.html           # Monetization plans, featured add-ons, Easypaisa/JazzCash instructions
    ├── login.html             # User & Admin authentication
    ├── register.html          # Registration with role selection (Tenant, Landlord, Agent)
    ├── about.html             # Mission, team, provincial coverage in Pakistan
    ├── contact.html           # Office address, helpline, contact inquiry form
    ├── terms.html             # Pakistani tenancy law compliance & regulations
    ├── privacy.html           # Data protection & privacy policy
    │
    ├── dashboard/             # User & Landlord Dashboard
    │   ├── overview.html      # Account stats, active plan, quick actions
    │   ├── listings.html      # Manage submitted listings, moderation statuses, view counts
    │   ├── favorites.html     # Saved properties list
    │   ├── enquiries.html     # Incoming tenant leads and outgoing messages
    │   ├── appointments.html  # Scheduled physical viewings
    │   └── profile.html       # Profile settings & bio
    │
    └── admin/                 # Admin Control Panel
        ├── base_admin.html    # Dedicated admin layout with sidebar
        ├── dashboard.html     # Platform statistics, pending moderation queue, transactions
        ├── properties.html    # All listings management, approve/reject, toggle featured
        ├── users.html         # User & agent management, verification badge toggles
        ├── reports.html       # Reported listings moderation
        ├── monetization.html  # Revenue dashboard & payment TID verification
        ├── ads.html           # Banner advertisements manager
        └── settings.html      # Website, Gemini AI key, and bank accounts configuration
```

---

## ⚙️ Installation & Local Setup

### Prerequisites
- Python 3.10+ installed on your system.

### 1. Clone or Open the Project Folder
```bash
cd "c:\Users\oxford\Desktop\Rent Finder Pakistan"
```

### 2. (Optional) Create a Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies are lightweight: Flask and Werkzeug)*

### 4. Seed the Database
Populate the database with realistic demo properties across Karachi, Lahore, Islamabad, etc., along with admin accounts and monetization records:
```bash
python seed_data.py
```

### 5. Run the Application
You can run using the provided Windows script:
- Double-click **`run.bat`**  
OR run via terminal:
```bash
python app.py
```

Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Demo Account Credentials

| Role | Email | Password | Description |
|---|---|---|---|
| **Admin** | `admin@rentfinder.pk` | `admin123` | Full access to `/admin` command center |
| **Agent / Dealer** | `usman.realtors@gmail.com` | `password123` | Malik Usman Real Estate (Platinum Plan) |
| **Landlord** | `farhan.bukhari@yahoo.com` | `password123` | Syed Farhan Bukhari (Islamabad Properties) |
| **Tenant** | `hamza.tenant@gmail.com` | `password123` | Hamza Rafique (Active tenant account) |

---

## 🤖 Google Gemini AI Setup

1. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Log in as Admin (`admin@rentfinder.pk` / `admin123`) and navigate to **System Settings** (`/admin/settings`).
3. Paste your API key in the **Google Gemini API Key** field, select your preferred model (`gemini-1.5-flash`), and click **Save All Settings**.
4. Alternatively, you can set the environment variable:
   ```bash
   set GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```
5. If no API key is entered, the chatbot seamlessly operates using its built-in local natural language database engine.

---

## 🧪 Running Automated Tests

Run the full 9-point unit & integration test suite to verify every route, database query, AI chatbot response, and admin protection guard:
```bash
python test_app.py
```

All 9 tests will run and verify:
- Homepage rendering with 3D canvas and dual typography
- City and budget property search filters
- Property detail view with booking and report modals
- Comparison table of up to 4 listings
- Monetization and Pakistani payment gateways
- AI Chatbot natural language property matching
- AI Chatbot global knowledge response
- Admin route authentication guard
- Admin login and moderation operations

---

## 🌐 Production Deployment Guide

### Option A: Cloud VPS (Ubuntu / Debian on DigitalOcean, Linode, AWS EC2, or Contabo)
1. Install Python, Nginx, and Gunicorn:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv nginx
   ```
2. Clone project to `/var/www/rentfinder`:
   ```bash
   git clone <repo-url> /var/www/rentfinder
   cd /var/www/rentfinder
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt gunicorn
   python3 seed_data.py
   ```
3. Create a systemd service (`/etc/systemd/system/rentfinder.service`):
   ```ini
   [Unit]
   Description=Rent Finder Pakistan Gunicorn Daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/rentfinder
   Environment="PATH=/var/www/rentfinder/venv/bin"
   ExecStart=/var/www/rentfinder/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

   [Install]
   WantedBy=multi-user.target
   ```
   Start and enable:
   ```bash
   sudo systemctl start rentfinder
   sudo systemctl enable rentfinder
   ```
4. Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/rentfinder`):
   ```nginx
   server {
       server_name rentfinder.pk www.rentfinder.pk;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }

       location /static {
           alias /var/www/rentfinder/static;
           expires 30d;
       }
   }
   ```
   Enable and restart:
   ```bash
   sudo ln -s /etc/nginx/sites-available/rentfinder /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```
5. Install SSL Certificate via Let's Encrypt Certbot:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d rentfinder.pk -d www.rentfinder.pk
   ```

### Option B: Platform as a Service (Railway / Render / Heroku)
1. Add a `Procfile`:
   ```
   web: gunicorn app:app
   ```
2. Connect your GitHub repository to Railway or Render.
3. Add environment variable `GEMINI_API_KEY` in the dashboard.
4. Deploy!

---

## 💰 Monetization & Pakistani Payment Integration Guide

1. Navigate to **Pricing & Plans** (`/pricing`).
2. Landlords choose between **Silver Landlord (PKR 3,500)**, **Gold Landlord (PKR 7,500)**, or **Platinum Agency (PKR 15,000)**.
3. Payments can be sent to the official accounts shown:
   - **Easypaisa:** Account # `0300 8291034` (Rent Finder Pakistan Pvt Ltd)
   - **JazzCash:** Account # `0301 9988776` (Rent Finder Pakistan)
   - **Meezan Bank Ltd:** IBAN `PK45MEZN0001020304050607`
4. The landlord enters their Transaction ID (TID) in the **Submit Payment Verification** modal.
5. In the Admin Panel (`/admin/monetization`), the administrator reviews the incoming TID against the bank/Easypaisa statement and clicks **Verify & Activate**, which automatically grants featured badges and upgrades the subscriber's account.

---

## 🛡️ Trust & Safety Guarantees
- **Zero Fake Badges:** Landlords must submit CNIC / property documents to receive the verified badge.
- **Human Moderation Queue:** New listings stay `pending` until approved by admin.
- **Tenancy Law Guidance:** Detailed references to the Sindh Rented Premises Ordinance 1979 and Punjab Rented Premises Act 2009 are available at `/terms`.
