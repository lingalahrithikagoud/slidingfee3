
import streamlit as st
import pandas as pd
import io
from datetime import datetime
import os

# Fixed logo path from your screenshot
logo_path = "C:\\Users\\harik\\sliding fee 3\\image.ico"
if os.path.exists(logo_path):
    st.image(logo_path, width=100)

st.set_page_config(page_title="Amistad Sliding Fee Calculator", layout="centered")
st.title("Amistad Health – Sliding Fee Schedule Calculator")
st.markdown("Estimate sliding fee category by entering family size, income sources, and service category.")

FREQ_MAP = {
    "Hourly (Daily)": 260,
    "Hourly (Weekly)": 52,
    "Hourly (Monthly)": 12,
    "Biweekly": 26,
    "Monthly": 12,
    "Quarterly": 4,
    "Yearly": 1
}

# Service category selection (flattened)
service_category = st.selectbox("🏥 Select Visit Type", [
    "Womens Health", "Family Practice", "Pediatrics", "Dental", "Behavioral Health"
])

def sliding_fee_category(family_size, annual_income):
    thresholds = {
        1: [15060, 18825, 22590, 26355, 30120],
        2: [20440, 25550, 30660, 35770, 40880],
        3: [25820, 32275, 38730, 45185, 51640],
        4: [31200, 39000, 46800, 54600, 62400],
        5: [36580, 45725, 54870, 64015, 73160],
        6: [41960, 52450, 62940, 73430, 83920],
        7: [47340, 59175, 71010, 82845, 94680],
        8: [52720, 65900, 79080, 92260, 105440]
    }
    if family_size > 8:
        extra = family_size - 8
        thresholds[family_size] = [x + extra * 5380 for x in thresholds[8]]
    limits = thresholds.get(family_size)
    if annual_income <= limits[0]: return "A – 100% FPL → $25 Nominal Fee"
    elif annual_income <= limits[1]: return "B – 125% FPL → 90% Discount"
    elif annual_income <= limits[2]: return "C – 150% FPL → 80% Discount"
    elif annual_income <= limits[3]: return "D – 175% FPL → 70% Discount"
    elif annual_income <= limits[4]: return "E – 200% FPL → 60% Discount"
    else: return "Above 200% FPL → No sliding discount"

# Inputs
family_size = st.number_input("👨‍👩‍👧‍👦 Family Size", min_value=1, value=1)
num_rows = st.number_input("➕ Number of Income Entries", min_value=1, value=2)

records = []
for i in range(int(num_rows)):
    with st.expander(f"Income Source #{i+1}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            member = st.text_input(f"Member #{i+1}", key=f"mem{i}")
            source = st.text_input(f"Source #{i+1}", key=f"src{i}")
            freq = st.selectbox(f"Frequency #{i+1}", list(FREQ_MAP.keys()), key=f"freq{i}")
        with col2:
            if "Hourly" in freq:
                rate = st.number_input(f"Hourly Rate #{i+1}", min_value=0.0, key=f"hr{i}")
                hours = st.number_input(f"Hours/Week #{i+1}", min_value=0.0, key=f"hw{i}")
                total = rate * hours * FREQ_MAP[freq]
            else:
                amt = st.number_input(f"Amount #{i+1}", min_value=0.0, key=f"amt{i}")
                total = amt * FREQ_MAP[freq]
        records.append({
            "Household Member": member,
            "Income Source": source,
            "Frequency": freq,
            "Annual Equivalent": round(total, 2)
        })

# Output
if st.button("💾 Calculate"):
    df = pd.DataFrame(records)
    total_income = df["Annual Equivalent"].sum()
    category = sliding_fee_category(family_size, total_income)

    st.subheader("📊 Results")
    st.metric(label="Total Annual Income", value=f"${total_income:,.2f}")
    st.success(f"Sliding Fee Category: **{category}**")
    st.markdown(f"**Visit Category**: {service_category}")
    st.dataframe(df)

    # Excel Export
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Income")
    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer,
        file_name="income_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
