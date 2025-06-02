# LocalHarvest - UI with Tabs + Image Upload + Filters + Google Sheets

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------
# App Setup (must come FIRST)
# ------------------------
st.set_page_config(page_title="LocalHarvest", layout="centered")

# ------------------------
# Custom CSS Styles
# ------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Quicksand', sans-serif;
        background-color: #fcf8f2;
    }
    .main-title {
        text-align: center;
        color: #3E8E41;
        font-size: 2.8em;
        margin-bottom: 0.5em;
    }
    .tagline {
        text-align: center;
        font-size: 1.2em;
        color: #5f5f5f;
        margin-bottom: 2em;
    }
    .listing-card {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #fff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .listing-card strong {
        font-size: 1.2em;
        color: #3E8E41;
    }
    .submit-button button {
        background-color: #3E8E41 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------
# Google Sheets Setup
# ------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["google_sheets"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("LocalHarvest Listings").sheet1

# ------------------------
# Main Header
# ------------------------
st.markdown("<div class='main-title'>🌽 LocalHarvest</div>", unsafe_allow_html=True)
st.markdown("<div class='tagline'>Trade or sell homegrown produce in your neighborhood.</div>", unsafe_allow_html=True)

# ------------------------
# Tabs for Split View
# ------------------------
tab1, tab2 = st.tabs(["📬 Post Produce", "🍏 Browse Listings"])

with tab1:
    st.subheader("📤 Post Your Produce")
    with st.form("add_listing"):
        name = st.text_input("Item (e.g., Tomatoes, Basil)")
        type = st.selectbox("Type", ["Trade", "Sell", "Trade or Sell"])
        description = st.text_area("Description")
        location = st.text_input("ZIP Code")
        contact = st.text_input("Contact (email or phone)")
        image = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Post Listing")

    if submit and name and location and contact:
        image_url = image.name if image else ""
        listing = [
            str(uuid.uuid4()),
            name,
            type,
            description,
            location,
            contact,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            image_url
        ]
        try:
            sheet.append_row(listing)
        except:
            st.error("❌ Failed to add listing. Check your sheet access.")
        else:
            st.success(f"✅ {name} listed for {type.lower()}!")

with tab2:
    st.subheader("🔍 Find Produce Near You")
    filter_zip = st.text_input("Enter your ZIP Code:")
    filter_name = st.text_input("Search by item name (optional):")

    records = sheet.get_all_records()

    if filter_zip:
        matches = [l for l in records if str(l['zip']) == filter_zip]
        if filter_name:
            matches = [m for m in matches if filter_name.lower() in m['name'].lower()]

        if matches:
            for l in matches:
                st.markdown(f"""
                <div class='listing-card'>
                <strong>{l['name']}</strong> ({l['type']})<br>
                <span style='color:#555;'>{l['desc']}</span><br>
                📍 <strong>ZIP:</strong> {l['zip']}<br>
                📞 <strong>Contact:</strong> {l['contact']}<br>
                🕒 <em>{l['timestamp']}</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No listings found that match your search.")
    else:
        st.info("Enter your ZIP code to browse local produce.")

# ------------------------
# Coming Soon Section
# ------------------------
st.markdown("""
---
### 🔜 Coming Soon:
- Add photos to listings 📸
- Built-in chat or message requests 💬
- Filters by category or freshness 🍓
- Seller/trader verification badges ✅
- Map of nearby listings 🗺️
""")
