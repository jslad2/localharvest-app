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
# Session Initialization
# ------------------------
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Post"
if st.session_state.get("update_success"):
    st.success("✅ Listing updated successfully!")
    del st.session_state["update_success"]

# ------------------------
# Tab Labels
# ------------------------
tab_labels = {
    "Post": "\U0001F4EC Post Produce",
    "Browse": "\U0001F34F Browse Listings",
    "My": "\U0001F4C2 My Listings"
}

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
    margin-bottom: 10px;
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
# User Login
# ------------------------
st.sidebar.header("\U0001F510 Login")
email_input = st.sidebar.text_input("Your Email", placeholder="you@email.com")
if st.sidebar.button("Log In"):
    if "@" in email_input and "." in email_input:
        st.session_state["user_email"] = email_input
        st.sidebar.success(f"Logged in as {email_input}")
    else:
        st.sidebar.error("Please enter a valid email.")

# ------------------------
# Header
# ------------------------
st.markdown("<div class='main-title'>\U0001F33D LocalHarvest</div>", unsafe_allow_html=True)
st.markdown("<div class='tagline'>Trade or sell homegrown produce in your neighborhood.</div>", unsafe_allow_html=True)

# ------------------------
# Tab Selection
# ------------------------
selected_tab = st.radio("Choose a section:", list(tab_labels.values()), horizontal=True, label_visibility="collapsed")
tab1_selected = selected_tab == tab_labels["Post"]
tab2_selected = selected_tab == tab_labels["Browse"]
tab3_selected = selected_tab == tab_labels["My"]

# ------------------------
# Load Data
# ------------------------
try:
    data = sheet.get_all_values()
    for row in data[1:]:
        while len(row) < 9:
            row.append("")
    df = pd.DataFrame(data[1:], columns=[
        "id", "item", "type", "desc", "zip", "contact", "timestamp", "image", "price"
    ])
except Exception as e:
    st.error(f"Could not load listings: {e}")
    st.stop()

df = df.sort_values("timestamp", ascending=False)

# ------------------------
# Post Produce
# ------------------------
if tab1_selected:
    st.subheader("\U0001F4E4 Post Your Produce")
    if not st.session_state["user_email"]:
        st.warning("Please log in using the sidebar to post produce.")
    else:
        name = st.text_input("Item", placeholder="e.g., Tomatoes, Basil")
        type = st.selectbox("Type", ["", "Trade", "Sell", "Trade or Sell"])

        if type:
            with st.form("add_listing", clear_on_submit=True):
                description = st.text_area("Description")
                location = st.text_input("ZIP Code", placeholder="e.g., 90210")
                contact_method = st.selectbox("Preferred Contact Method", ["Email", "Phone", "Both"])
                contact = st.text_input("Enter contact detail", value=st.session_state["user_email"])
                price = st.text_input("Price") if type in ["Sell", "Trade or Sell"] else ""
                image = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])
                submit = st.form_submit_button("Post Listing")

            if submit:
                if not (name and location and contact):
                    st.warning("Please fill out all required fields.")
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
                        st.success(f"✅ {name} listed successfully!")
                    except Exception as e:
                        st.error(f"❌ Failed to add listing: {e}")

# ------------------------
# Browse Listings
# ------------------------
elif tab2_selected:
    st.subheader("\U0001F50D Browse Listings")
    all_zips = sorted(df["zip"].unique())
    zip_filter = st.selectbox("Filter by ZIP Code", options=["All"] + all_zips)
    matches = df if zip_filter == "All" else df[df["zip"].str.startswith(zip_filter)]

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

# ------------------------
# My Listings
# ------------------------
elif tab3_selected:
    st.subheader("\U0001F4C2 My Listings")
    user = st.session_state["user_email"]
    if not user:
        st.warning("Please log in to view your listings.")
    else:
        my_listings = df[df["contact"].str.contains(user, case=False, na=False)]
        for _, row in my_listings.iterrows():
            image_html = f"<img class='listing-thumb' src='{row['image']}'/>" if row['image'] else ""
            price_line = f"💲 <strong>Price:</strong> {row['price']}<br>" if row['price'] else ""
            st.markdown(f"""
            <div class='listing-card'>
            <strong>{row['item']}</strong> ({row['type']})<br>
            <span style='color:#555;'>{row['desc']}</span><br>
            📍 <strong>ZIP:</strong> {row['zip']}<br>
            📞 <strong>Contact:</strong> {row['contact']}<br>
            {price_line}
            {image_html}
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("📝 Edit", key=f"edit_{row['id']}"):
                    st.session_state["edit_mode"] = row.to_dict()
                    st.session_state["active_tab"] = "My"
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                    st.session_state["confirm_delete"] = row.to_dict()

# ------------------------
# Confirm Delete
# ------------------------
if "confirm_delete" in st.session_state:
    row = st.session_state["confirm_delete"]
    st.warning(f"⚠ Are you sure you want to delete: **{row['item']}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, delete it"):
            all_rows = sheet.get_all_values()
            for i, r in enumerate(all_rows):
                if r[0] == row["id"]:
                    sheet.delete_rows(i + 1)
                    break
            del st.session_state["confirm_delete"]
            st.session_state["active_tab"] = "My"
            st.rerun()
    with col2:
        if st.button("❌ Cancel"):
            del st.session_state["confirm_delete"]

# ------------------------
# Edit Listing Form
# ------------------------
if "edit_mode" in st.session_state and st.session_state["edit_mode"]:
    listing = st.session_state["edit_mode"]
    st.subheader("✏️ Edit Listing")
    with st.form("edit_listing"):
        new_name = st.text_input("Item", value=listing["item"])
        new_type = st.selectbox("Type", ["Trade", "Sell", "Trade or Sell"], index=["Trade", "Sell", "Trade or Sell"].index(listing["type"]))
        new_desc = st.text_area("Description", value=listing["desc"])
        new_zip = st.text_input("ZIP Code", value=listing["zip"])
        new_contact = st.text_input("Contact Info", value=listing["contact"])
        new_price = st.text_input("Price", value=listing["price"])
        new_image = st.file_uploader("Replace Image? (optional)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Update Listing")

    if submitted:
        updated_image = listing["image"]
        if new_image:
            image_bytes = new_image.read()
            updated_image = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"

        updated_row = [
            listing["id"], new_name, new_type, new_desc, new_zip, new_contact,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), updated_image, new_price
        ]

        all_rows = sheet.get_all_values()
        for i, r in enumerate(all_rows):
            if r[0] == listing["id"]:
                sheet.delete_rows(i + 1)
                break

        sheet.append_row(updated_row)
        st.session_state["edit_mode"] = None
        st.session_state["update_success"] = True
        st.session_state["active_tab"] = "My"
        st.rerun()
