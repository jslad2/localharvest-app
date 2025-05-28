# Online Farmers Market MVP (PWA-style Web App using Streamlit)

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- Initialize Listings ---
if "listings" not in st.session_state:
    st.session_state.listings = []

# --- Page Setup ---
st.set_page_config(page_title="LocalHarvest", layout="centered")
st.title("🌽 LocalHarvest")
st.markdown("Trade or sell homegrown produce in your neighborhood.")

# --- Add Listing ---
st.subheader("📤 List Your Produce")
with st.form("add_listing"):
    name = st.text_input("What are you offering? (e.g., Tomatoes, Basil)")
    type = st.selectbox("Is this for sale or trade?", ["Trade", "Sell"])
    description = st.text_area("Short description")
    location = st.text_input("ZIP code")
    contact = st.text_input("Contact method (email or phone)")
    submit = st.form_submit_button("Post Listing")

if submit and name and location and contact:
    listing = {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": type,
        "desc": description,
        "zip": location,
        "contact": contact,
        "timestamp": datetime.now()
    }
    st.session_state.listings.append(listing)
    st.success(f"✅ Listed {name} for {type.lower()}!")

# --- View Listings ---
st.subheader("🍏 Available Listings Near You")
filter_zip = st.text_input("Enter your ZIP code to browse nearby listings:")

if filter_zip:
    matches = [l for l in st.session_state.listings if l['zip'] == filter_zip]
    if matches:
        for l in matches:
            st.markdown(f"""
            <div style='border:1px solid #ddd;padding:10px;border-radius:8px;margin-bottom:10px;'>
            <strong>{l['name']}</strong> ({l['type']})<br>
            {l['desc']}<br>
            📍 ZIP: {l['zip']}<br>
            📞 Contact: {l['contact']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No listings found in that ZIP code yet.")
else:
    st.info("Enter your ZIP code to browse local produce.")

# --- Coming Soon ---
st.markdown("""
---
### 🔜 Coming Soon:
- Add photos to listings 📸
- Built-in chat or message requests 💬
- Filters by category or freshness 🍓
- Seller/trader verification badges ✅
""")
