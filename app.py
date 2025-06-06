import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64

# ------------------------
# App Setup
# ------------------------
st.set_page_config(page_title="LocalHarvest", layout="centered")

# ------------------------
# CSS Styling
# ------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500&display=swap');
html, body, [class*="css"] {
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
img.listing-thumb {
    max-width: 120px;
    display: block;
    margin-top: 10px;
    margin-bottom: 5px;
    border-radius: 8px;
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
# Header
# ------------------------
st.markdown("<div class='main-title'>🌽 LocalHarvest</div>", unsafe_allow_html=True)
st.markdown("<div class='tagline'>Trade or sell homegrown produce in your neighborhood.</div>", unsafe_allow_html=True)

# ------------------------
# Tabs
# ------------------------
tab1, tab2 = st.tabs(["📬 Post Produce", "🍏 Browse Listings"])

# ------------------------
# POST Produce
# ------------------------
with tab1:
    st.subheader("📤 Post Your Produce")

    name = st.text_input("Item", placeholder="e.g., Tomatoes, Basil")
    type = st.selectbox("Type", ["", "Trade", "Sell", "Trade or Sell"])

    if type:
        with st.form("add_listing", clear_on_submit=True):
            description = st.text_area("Description")
            location = st.text_input("ZIP Code", placeholder="e.g., 90210", help="Your 5-digit postal code")
            contact_method = st.selectbox("Preferred Contact Method", ["Email", "Phone", "Both"])
            contact = st.text_input("Enter contact detail", placeholder="email@example.com")
            price = st.text_input("Price", placeholder="$5 per bunch") if type in ["Sell", "Trade or Sell"] else ""
            image = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])
            submit = st.form_submit_button("Post Listing")

        if submit:
            if not (name and location and contact):
                st.warning("❗ Please fill out all required fields (Item, ZIP Code, Contact).")
            else:
                image_url = ""
                if image:
                    image_bytes = image.read()
                    image_url = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"

                listing = [
                    str(uuid.uuid4()), name, type, description, location,
                    f"{contact_method}: {contact}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), image_url, price
                ]

                try:
                    sheet.append_row(listing)
                    st.success(f"✅ {name} listed successfully on {listing[6]}!")
                except Exception as e:
                    st.error(f"❌ Failed to add listing: {e}")

# ------------------------
# Browse Listings
# ------------------------
with tab2:
    st.subheader("🔍 Browse Listings")

    try:
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=[
            "id", "item", "type", "desc", "zip", "contact", "timestamp", "image", "price"
        ])
    except Exception as e:
        st.error(f"Could not load listings: {e}")
        st.stop()

    df = df.sort_values("timestamp", ascending=False)
    all_zips = sorted(df["zip"].unique())
    zip_filter = st.selectbox("Filter by ZIP Code", options=["All"] + all_zips)

    if zip_filter == "All":
        matches = df
    else:
        matches = df[df["zip"].str.startswith(zip_filter)]

    if matches.empty:
        st.warning("⚠ No listings found.")
    else:
        for _, l in matches.iterrows():
            image_html = f"<img class='listing-thumb' src='{l['image']}'/>" if l['image'] else ""
            price_line = f"💲 <strong>Price:</strong> {l['price']}<br>" if l['price'] else ""
            st.markdown(f"""
            <div class='listing-card'>
            <strong>{l['item']}</strong> ({l['type']})<br>
            <span style='color:#555;'>{l['desc']}</span><br>
            📍 <strong>ZIP:</strong> {l['zip']}<br>
            📞 <strong>Contact:</strong> {l['contact']}<br>
            {price_line}
            {image_html}
            </div>
            """, unsafe_allow_html=True)
