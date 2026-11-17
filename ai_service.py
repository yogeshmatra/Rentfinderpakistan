"""
Rent Finder AI - Dual-Capability Gemini AI Engine & Local Intelligence
Supports:
1. Property Assistant: Real-time DB search, filters, details, comparison, and inquiries.
2. Global AI Assistant: General knowledge, science, programming, translation (English, Urdu, Roman Urdu), business, and conversations.
Powered by Google Gemini API with intelligent built-in fallback.
"""

import os
import json
import re
import urllib.request
import urllib.error
from database import get_db, get_setting

# System prompt for Gemini
SYSTEM_INSTRUCTION = """
You are "Rent Finder AI", the official intelligent AI assistant for Rent Finder Pakistan (https://rentfinder.pk) as well as a world-class global AI assistant.

You have TWO seamless capabilities:
1. REAL ESTATE & RENTAL ASSISTANT:
   - Help users find rental houses, flats, rooms, portions, shops, and offices across all Pakistani cities (Karachi, Lahore, Islamabad, Rawalpindi, Faisalabad, Multan, Hyderabad, Quetta, Peshawar, etc.).
   - Understand budgets, advance payment, security deposits, Sui gas, K-Electric/LESCO loadshedding status, water supply (sweet water/boring), Marla/Kanal/Sq Yards conversions, and lease terms under Pakistani Tenancy Laws (e.g., Sindh Rented Premises Ordinance, Punjab Rented Premises Act).
   - Help users post their properties, compare listings, contact landlords, and book viewing appointments.
   - You understand English, Urdu (اردو), and Roman Urdu (e.g. "Mujhe Karachi me 2 bed flat chahiye under 50k").

2. GLOBAL AI ASSISTANT (Like ChatGPT):
   - Answer ANY general question with deep knowledge: education, science, mathematics, technology, coding (Python, JS, HTML, etc.), business ideas, career advice, history, geography, lifestyle, and global news.
   - Be helpful, polite, modern, concise, and structured (use markdown bullet points and bold text).

Always respond in the same language or dialect the user used (English, Urdu, or Roman Urdu).
"""

def is_property_search_intent(text):
    """Determine if query is specifically an active search for listings."""
    t = text.lower()

    # Informational / legal / how-to queries are NOT direct property searches
    informational_markers = [
        'how to', 'how can', 'rules', 'law', 'agreement', 'procedure',
        'what is', 'explain', 'difference', 'calculate', 'rights', 'legal'
    ]
    if any(m in t for m in informational_markers):
        return False

    # Search indicators
    search_verbs = ['find', 'search', 'show', 'looking for', 'need', 'available', 'rent', 'chahiye', 'dikhao', 'dhoond', 'batao']
    cities = ['karachi', 'lahore', 'islamabad', 'rawalpindi', 'hyderabad', 'sukkur', 'multan', 'faisalabad', 'quetta', 'peshawar']
    property_nouns = ['flat', 'house', 'room', 'portion', 'shop', 'office', 'apartment', 'kamra', 'makan', 'bhk']

    has_city = any(c in t for c in cities)
    has_noun = any(n in t for n in property_nouns)
    has_verb = any(v in t for v in search_verbs)
    has_budget = bool(re.search(r'\b(?:\d+k|\d{4,7}|lakh|lac)\b', t))

    return (has_city and (has_noun or has_verb)) or (has_noun and (has_budget or has_verb))

def query_database_for_properties(query_text):
    """Extract filters from query_text and run matching DB query."""
    conn = get_db()
    cursor = conn.cursor()

    text_lower = query_text.lower()

    # Detect City
    cities = ['karachi', 'lahore', 'islamabad', 'rawalpindi', 'hyderabad', 'sukkur', 'multan', 'faisalabad', 'quetta', 'peshawar']
    matched_city = None
    for c in cities:
        if c in text_lower:
            matched_city = c.capitalize()
            break

    # Detect Property Type
    types_map = {
        'flat': 'Flat', 'apartment': 'Flat',
        'house': 'House', 'bangla': 'House', 'bungalow': 'House', 'makan': 'House', 'kothi': 'House',
        'room': 'Room', 'kamra': 'Room', 'studio': 'Room',
        'portion': 'Upper Portion', 'upper portion': 'Upper Portion', 'lower portion': 'Lower Portion',
        'shop': 'Shop', 'dukan': 'Shop', 'store': 'Shop',
        'office': 'Office', 'daftar': 'Office', 'commercial': 'Office'
    }
    matched_type = None
    for k, v in types_map.items():
        if re.search(r'\b' + re.escape(k) + r'\b', text_lower):
            matched_type = v
            break

    # Detect Budget / Rent Limit (e.g. 50k, 50,000, 1 lakh, under 80000)
    max_rent = None
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)', text_lower)
    if lakh_match:
        max_rent = int(float(lakh_match.group(1)) * 100000)
    else:
        k_match = re.search(r'(\d+)\s*k\b', text_lower)
        if k_match:
            max_rent = int(k_match.group(1)) * 1000
        else:
            num_match = re.search(r'(?:under|below|max|rs\.?|pkr)\s*[:=]?\s*(\d{4,7})', text_lower)
            if num_match:
                max_rent = int(num_match.group(1))

    # Detect Bedrooms
    beds = None
    bed_match = re.search(r'(\d+)\s*(?:bed|bedroom|kamray)', text_lower)
    if bed_match:
        beds = int(bed_match.group(1))

    # Build SQL
    sql = "SELECT id, title, city, area, property_type, monthly_rent, bedrooms, bathrooms, size, size_unit, images, furnished, status FROM properties WHERE status = 'approved'"
    params = []

    if matched_city:
        sql += " AND LOWER(city) = LOWER(?)"
        params.append(matched_city)
    if matched_type:
        sql += " AND property_type = ?"
        params.append(matched_type)
    if max_rent:
        sql += " AND monthly_rent <= ?"
        params.append(max_rent)
    if beds:
        sql += " AND bedrooms >= ?"
        params.append(beds)

    sql += " ORDER BY is_featured DESC, id DESC LIMIT 4"

    rows = cursor.execute(sql, params).fetchall()

    # If no strict match, fallback to broader search
    if not rows and (matched_city or matched_type):
        broad_sql = "SELECT id, title, city, area, property_type, monthly_rent, bedrooms, bathrooms, size, size_unit, images, furnished, status FROM properties WHERE status = 'approved'"
        broad_params = []
        if matched_city:
            broad_sql += " AND LOWER(city) = LOWER(?)"
            broad_params.append(matched_city)
        broad_sql += " ORDER BY is_featured DESC, id DESC LIMIT 3"
        rows = cursor.execute(broad_sql, broad_params).fetchall()

    conn.close()

    results = []
    for r in rows:
        imgs = []
        try:
            imgs = json.loads(r['images'])
        except:
            imgs = []
        first_img = imgs[0] if imgs else 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=600&q=80'

        results.append({
            'id': r['id'],
            'title': r['title'],
            'city': r['city'],
            'area': r['area'],
            'property_type': r['property_type'],
            'monthly_rent': r['monthly_rent'],
            'bedrooms': r['bedrooms'],
            'bathrooms': r['bathrooms'],
            'size': f"{r['size']} {r['size_unit']}",
            'furnished': r['furnished'],
            'image': first_img,
            'url': f"/properties/{r['id']}"
        })

    return results

def call_gemini_api(prompt, chat_history=None, api_key=None, context_properties=None):
    """Calls Gemini REST API directly using standard urllib."""
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY') or get_setting('gemini_api_key', '')

    if not api_key:
        return None

    model = get_setting('gemini_model', 'gemini-1.5-flash')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    contents = []

    # Inject context about matched properties if any
    enhanced_prompt = prompt
    if context_properties:
        prop_summary = "\n".join([
            f"- ID {p['id']}: {p['title']} in {p['area']}, {p['city']} | Rent: PKR {p['monthly_rent']:,}/mo | {p['bedrooms']} Beds, {p['bathrooms']} Baths | Size: {p['size']}"
            for p in context_properties
        ])
        enhanced_prompt = f"User Question: {prompt}\n\n[DATABASE CONTEXT - Currently Matching Properties in Pakistan]:\n{prop_summary}\n\nPlease reference these exact properties in your answer where appropriate."

    # Chat history
    if chat_history:
        for m in chat_history[-6:]:
            role = 'user' if m.get('role') == 'user' else 'model'
            contents.append({
                'role': role,
                'parts': [{'text': m.get('content', '')}]
            })

    contents.append({
        'role': 'user',
        'parts': [{'text': enhanced_prompt}]
    })

    payload = {
        'contents': contents,
        'systemInstruction': {
            'parts': [{'text': SYSTEM_INSTRUCTION}]
        },
        'generationConfig': {
            'temperature': 0.7,
            'maxOutputTokens': 1000
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            result = json.loads(response.read().decode('utf-8'))
            candidate = result.get('candidates', [{}])[0]
            parts = candidate.get('content', {}).get('parts', [{}])
            reply = parts[0].get('text', '') if parts else ''
            return reply
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def fallback_intelligent_response(user_message, matched_properties=None):
    """Rich built-in response engine when Gemini API key is not configured or offline."""
    msg = user_message.strip()
    msg_lower = msg.lower()

    # If properties matched for a search
    if matched_properties:
        count = len(matched_properties)
        lines = [
            f"I found **{count} matching rental propert{'ies' if count > 1 else 'y'}** in our verified database based on your request:\n"
        ]
        for p in matched_properties:
            lines.append(f"• **{p['title']}** ({p['city']}) - **PKR {p['monthly_rent']:,}/month** [{p['bedrooms']} Bed | {p['size']}]")
        lines.append("\nYou can click on any property card below to view all high-definition images, floor plan, landlord contact & WhatsApp, or to schedule a direct physical viewing!")
        return "\n".join(lines)

    # Pakistani Tenancy Laws & Rent Agreements
    if any(k in msg_lower for k in ['agreement', 'law', 'legal', 'punjab rented', 'sindh rented', 'rules']):
        return """### Legal Rent Agreements Under Pakistani Law:
Under the **Sindh Rented Premises Ordinance 1979** and the **Punjab Rented Premises Act 2009**, rental agreements must adhere to standard statutory procedures:

1. **Written Agreement:** Every tenancy agreement must be written on official non-judicial Stamp Paper (typically Rs. 1,200 to Rs. 2,000 depending on provincial stamp duty) and attested.
2. **Registration:** In Punjab and Islamabad, agreements must be registered with the local **Rent Registrar** at the designated police facilitation center (Khidmat Markaz) or sub-registrar.
3. **Advance & Security Deposit:** 
   - Advance rent is commonly 1 to 2 months.
   - Refundable security deposit is normally 2 to 3 months rent, which the landlord must refund upon vacating, minus verified unpaid bills or damages.
4. **Annual Rent Escalation:** Legally recognized annual increase is typically capped at **10%** unless mutually stipulated otherwise.
5. **Notice Period:** A minimum of **1 to 2 months prior written notice** is required by either party before termination of tenancy."""

    # Posting property guidance
    if any(k in msg_lower for k in ['how to post', 'add property', 'listing', 'post property', 'property kaise lagaye']):
        return """### How to Post Your Rental Property on Rent Finder Pakistan:
1. Click the **[Post Property](/post-property)** button in the top navigation bar.
2. Sign in or create a free Landlord/Agent account.
3. Fill in your property details: Title, Pakistani city, exact area/sector, monthly rent in PKR, advance & security deposit.
4. Upload clear photos of your house, flat, or commercial space.
5. Submit for verification! Our moderation team reviews all listings within 2 hours to ensure quality and trust for tenants.

*Tip: You can also upgrade to a **Featured Listing** to get 5x more tenant inquiries!*"""

    # Landlord contact guidance
    if any(k in msg_lower for k in ['contact', 'whatsapp', 'call landlord', 'rabta']):
        return """### Contacting Landlords & Agents:
Every approved listing on **Rent Finder Pakistan** provides:
- Direct **WhatsApp chat button** with pre-filled property reference.
- Direct **Phone Call button** (`tel:`).
- Instant **Enquiry form** sent straight to the owner's dashboard.
- **Book Viewing Appointment** to schedule a convenient date & time slot.

Simply open any listing and use the owner contact card on the right!"""

    # Security deposit explanation
    if any(k in msg_lower for k in ['security deposit', 'advance', 'security kitni', 'advance payment']):
        return """### Standard Advance & Security in Pakistan:
- **Residential (Flats/Houses):** Typically **2 to 3 months rent** as refundable security deposit plus **1 to 2 months advance rent**.
- **Commercial (Shops/Offices):** Usually **3 to 6 months advance/security**, depending on location and fittings.
- Under Pakistani tenancy laws, the security deposit must be refunded upon termination of tenancy subject to bill clearance and property condition."""

    # Urdu greetings
    if any(k in msg_lower for k in ['urdu', 'roman urdu', 'salam', 'assalam', 'aoa', 'hello', 'hi']):
        return """Wa Alaikum Assalam! Welcome to **Rent Finder AI**! 🇵🇰

Mein aap ki rental properties dhoondne mein aur har qisam ke aam sawalat (General Knowledge, Science, Programming, Studies) mein madad kar sakta hoon.

Aap mujh se puch sakte hain:
- *"Karachi Gulshan me flat dikhao"*
- *"Lahore DHA me 1 Kanal house under 3.5 lakh"*
- *"Islamabad F-7 me house"*
- Ya koi bhi aam sawal jaise: *"Write a Python script for web scraping"* ya *"Pakistan rental agreements rules"*.

Batayein aaj aap ki kis tarah madad karoon?"""

    # General Knowledge / Programming / Tech / Science
    return f"""Hello! I am **Rent Finder AI**, your dual-purpose real estate & global knowledge assistant.

Regarding your query:
> *"{msg}"*

I can assist you with full details across rental properties in Pakistan, property valuation, tenancy law, and general topics including science, technology, programming, mathematics, education, and business planning.

> **Pro Tip:** To enable live generative AI responses for complex technical tasks, enter your `GEMINI_API_KEY` in the [Admin Settings](/admin/settings) panel or `.env` file.

How can I assist you further today?"""

def process_chat_message(user_message, session_id='guest', user_id=None, chat_history=None):
    """Main orchestrator for user chat messages."""
    clean_msg = user_message.strip()
    if not clean_msg:
        return {'text': "Please enter a question or property search request.", 'properties': []}

    matched_properties = []
    # If the user is specifically searching for property listings
    if is_property_search_intent(clean_msg):
        matched_properties = query_database_for_properties(clean_msg)

    # Try Gemini API first
    api_key = os.environ.get('GEMINI_API_KEY') or get_setting('gemini_api_key', '')
    ai_text = None
    if api_key:
        ai_text = call_gemini_api(clean_msg, chat_history=chat_history, api_key=api_key, context_properties=matched_properties)

    # Fallback to local intelligence if Gemini API not configured or failed
    if not ai_text:
        ai_text = fallback_intelligent_response(clean_msg, matched_properties)

    # Save to database
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (session_id, user_id, role, content, properties_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, 'user', clean_msg, None))
        cursor.execute('''
            INSERT INTO chat_messages (session_id, user_id, role, content, properties_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, 'assistant', ai_text, json.dumps(matched_properties) if matched_properties else None))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Chat logging error:", e)

    return {
        'text': ai_text,
        'properties': matched_properties
    }
