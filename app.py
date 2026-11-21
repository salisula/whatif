import streamlit as st
import simulator
import ai_tools
import pandas as pd
from fpdf import FPDF
import os

# 1. PAGE CONFIG
st.set_page_config(page_title="WhatIf | Decision Engine", page_icon="⚡", layout="wide")

# 2. CUSTOM CSS (The "Expensive" Look)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stDeployButton"] { display: none; }
    [data-testid="stHeader"] { background: transparent; }
    .stButton>button {
        border-radius: 8px; font-weight: 600; transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 192, 241, 0.3);
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input { border-radius: 8px; }
    div[data-testid="metric-container"] {
        background-color: #1E1E1E; border: 1px solid #333;
        padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- COMPREHENSIVE COUNTRY & CURRENCY LISTS ---
COUNTRY_MAP = {
    "Afghanistan": "AF", "Albania": "AL", "Algeria": "DZ", "Argentina": "AR", "Armenia": "AM", "Australia": "AU",
    "Austria": "AT", "Azerbaijan": "AZ", "Bahrain": "BH", "Bangladesh": "BD", "Belarus": "BY", "Belgium": "BE",
    "Brazil": "BR", "Bulgaria": "BG", "Canada": "CA", "Chile": "CL", "China": "CN", "Colombia": "CO",
    "Croatia": "HR", "Cyprus": "CY", "Czechia": "CZ", "Denmark": "DK", "Egypt": "EG", "Estonia": "EE",
    "Finland": "FI", "France": "FR", "Georgia": "GE", "Germany": "DE", "Greece": "GR", "Hungary": "HU",
    "Iceland": "IS", "India": "IN", "Indonesia": "ID", "Iran": "IR", "Iraq": "IQ", "Ireland": "IE",
    "Israel": "IL", "Italy": "IT", "Japan": "JP", "Jordan": "JO", "Kazakhstan": "KZ", "Kenya": "KE",
    "Kuwait": "KW", "Latvia": "LV", "Lebanon": "LB", "Lithuania": "LT", "Luxembourg": "LU", "Malaysia": "MY",
    "Mexico": "MX", "Moldova": "MD", "Mongolia": "MN", "Morocco": "MA", "Netherlands": "NL", "New Zealand": "NZ",
    "Nigeria": "NG", "North Macedonia": "MK", "Norway": "NO", "Pakistan": "PK", "Peru": "PE", "Philippines": "PH",
    "Poland": "PL", "Portugal": "PT", "Qatar": "QA", "Romania": "RO", "Russia": "RU", "Saudi Arabia": "SA",
    "Serbia": "RS", "Singapore": "SG", "Slovakia": "SK", "Slovenia": "SI", "South Africa": "ZA", "South Korea": "KR",
    "Spain": "ES", "Sweden": "SE", "Switzerland": "CH", "Taiwan": "TW", "Thailand": "TH", "Turkey": "TR",
    "Ukraine": "UA", "United Arab Emirates": "AE", "United Kingdom": "GB", "United States": "US", "Uruguay": "UY",
    "Uzbekistan": "UZ", "Vietnam": "VN"
}
CURRENCY_MAP = {
    "USD": "$", "EUR": "€", "GBP": "£", "GEL": "₾", "JPY": "¥", "CNY": "¥", "AUD": "A$", "CAD": "C$",
    "CHF": "CHF", "HKD": "HK$", "SGD": "S$", "NZD": "NZ$", "KRW": "₩", "INR": "₹", "BRL": "R$",
    "RUB": "₽", "ZAR": "R", "TRY": "₺", "MXN": "Mex$", "TWD": "NT$", "DKK": "kr", "SEK": "kr",
    "NOK": "kr", "PLN": "zł", "THB": "฿", "IDR": "Rp", "HUF": "Ft", "CZK": "Kč", "ILS": "₪",
    "CLP": "CLP$", "PHP": "₱", "AED": "د.إ", "COP": "COL$", "SAR": "﷼", "MYR": "RM", "RON": "lei",
    "VND": "₫", "EGP": "E£", "PKR": "₨", "NGN": "₦", "BDT": "৳", "UAH": "₴", "KZT": "₸"
}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00C0F1; margin-bottom: 0;'>⚡ WhatIf</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.9em;'>Decision Engine</p>", unsafe_allow_html=True)
    st.divider()
    
    st.subheader("🌍 Region & Currency")
    selected_country = st.selectbox("Country", list(COUNTRY_MAP.keys()), index=list(COUNTRY_MAP.keys()).index("Georgia"))
    country_code = COUNTRY_MAP[selected_country]
    selected_currency = st.selectbox("Currency", list(CURRENCY_MAP.keys()), index=list(CURRENCY_MAP.keys()).index("GEL"))
    currency_symbol = CURRENCY_MAP[selected_currency]
    
    st.divider()

    st.subheader("1. Current Metrics")
    price = st.number_input(f"Price per product ({currency_symbol})", value=5.00, step=0.50)
    cost = st.number_input(f"Cost per product ({currency_symbol})", value=2.00, step=0.50)
    st.caption("💡 Tip: Use the AI Price Finder to reduce this cost.")
    sales = st.number_input("Monthly Sales (units)", value=1000, step=100)
    fixed = st.number_input(f"Fixed Expenses ({currency_symbol})", value=1500.00, step=100.0)

    st.divider()

    st.subheader("2. Goals & Limits")
    current_profit = simulator.calculate_profit(price, cost, sales, fixed)
    goal_profit = st.number_input(f"Target Monthly Profit ({currency_symbol})", value=float(current_profit + 2000), step=500.0)

    st.write("What is realistic?")
    max_price_inc = st.slider("Max Price Increase (%)", 0, 50, 20, 5)
    max_cost_cut = st.slider("Max Cost Cut (%)", 0, 50, 10, 5)
    max_sales_inc = st.slider("Max Sales Increase (%)", 0, 100, 30, 5)
    
    st.divider()
    
    st.subheader(f"🌍 {selected_country} Inflation")
    inflation_rate = ai_tools.get_inflation_rate(country_code)
    if inflation_rate is not None:
        st.metric("Current Inflation", f"{inflation_rate}%", help="Source: World Bank API")
    else:
        st.metric("Current Inflation", "Data unavailable")

    st.divider()
    calculate_button = st.button("🚀 Run Simulation", use_container_width=True, type="primary")


# --- PDF GENERATOR FUNCTION ---
def generate_pdf_report(strategies_df, current_p, target_p, price, cost, sales, fixed, symbol):
    pdf = FPDF()
    
    font_regular = None
    font_bold = None
    
    regular_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    bold_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf"
    ]
    
    for path in regular_paths:
        if os.path.exists(path):
            font_regular = path
            break
            
    for path in bold_paths:
        if os.path.exists(path):
            font_bold = path
            break
            
    if font_regular:
        pdf.add_font("CustomFont", "", font_regular)
        pdf.add_font("CustomFont", "B", font_bold if font_bold else font_regular)
        font_family = "CustomFont"
    else:
        font_family = "Helvetica"
        symbol = "GEL "
        
    pdf.add_page()
    pdf.set_font(font_family, "B", 20)
    pdf.cell(0, 10, "WhatIf - Business Strategy Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    pdf.set_font(font_family, "B", 14)
    pdf.cell(0, 10, "1. Current Business Metrics", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_family, "", 12)
    pdf.cell(0, 8, f"Price per product: {symbol}{price:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Cost per product: {symbol}{cost:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Monthly Sales: {sales} units", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Fixed Expenses: {symbol}{fixed:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Current Profit: {symbol}{current_p:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Target Goal: {symbol}{target_p:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font(font_family, "B", 14)
    pdf.cell(0, 10, "2. Recommended Strategies", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_family, "B", 10)
    pdf.cell(25, 10, "Price Inc", border=1, align="C")
    pdf.cell(25, 10, "Cost Cut", border=1, align="C")
    pdf.cell(25, 10, "Sales Inc", border=1, align="C")
    pdf.cell(30, 10, "Projected Profit", border=1, align="C")
    pdf.cell(25, 10, "Risk Score", border=1, align="C")
    pdf.ln()
    
    pdf.set_font(font_family, "", 10)
    for _, row in strategies_df.iterrows():
        pdf.cell(25, 10, row["Price Increase"], border=1, align="C")
        pdf.cell(25, 10, row["Cost Cut"], border=1, align="C")
        pdf.cell(25, 10, row["Sales Increase"], border=1, align="C")
        pdf.cell(30, 10, f"{symbol}{row['Projected Profit']:.2f}", border=1, align="C")
        pdf.cell(25, 10, str(row["Risk Score"]), border=1, align="C")
        pdf.ln()
        
    # THE FIX IS HERE
    return bytes(pdf.output())


# --- MAIN PAGE: Tabs ---
st.title("Decision Engine")
st.markdown("### Advanced analytics and AI sourcing for small businesses.")
st.write("")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Strategy Simulator", "🛒 AI Price Finder", "📣 AI Influencer Finder", "⚔️ Competitor Mockup"])

# --- TAB 1: SIMULATOR ---
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Monthly Profit", f"{currency_symbol}{current_profit:,.2f}")
    col2.metric("Target Profit Goal", f"{currency_symbol}{goal_profit:,.2f}", f"+{currency_symbol}{goal_profit - current_profit:,.2f} needed")
    col3.metric("Current Profit Margin", f"{((price - cost) / price) * 100:.1f}%")

    st.write("")

    if calculate_button:
        if goal_profit <= current_profit:
            st.warning("Your target goal is already lower than your current profit!")
        else:
            with st.spinner("Analyzing thousands of business combinations..."):
                strategies = simulator.find_strategies(
                    price, cost, sales, fixed, goal_profit,
                    max_price_inc, max_cost_cut, max_sales_inc
                )
            
            if not strategies:
                st.error("No strategies found. Try increasing your limits or lowering your goal.")
            else:
                st.success(f"Found {len(strategies)} strategies to hit your goal.")
                
                df = pd.DataFrame(strategies)
                
                col_table, col_chart = st.columns([1.2, 1])
                
                with col_table:
                    st.subheader("Recommended Strategies")
                    st.dataframe(
                        df,
                        use_container_width=True,
                        column_config={
                            "Projected Profit": st.column_config.NumberColumn(format=f"{currency_symbol}%.2f"),
                            "Risk Score": st.column_config.ProgressColumn(
                                "Risk Score", min_value=0, max_value=100, format="%f"
                            )
                        }
                    )
                    
                    with st.container(border=True):
                        st.write("**Export Data**")
                        col_csv, col_pdf = st.columns(2)
                        with col_csv:
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Download CSV", csv, "whatif_strategies.csv", "text/csv", use_container_width=True)
                        with col_pdf:
                            pdf_bytes = generate_pdf_report(df, current_profit, goal_profit, price, cost, sales, fixed, currency_symbol)
                            st.download_button(
                                label="📄 Download PDF",
                                data=pdf_bytes,
                                file_name="WhatIf_Business_Report.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                
                with col_chart:
                    st.subheader("Profit Visualization")
                    chart_data = pd.DataFrame({
                        "Type": ["Current", "Target"] + [f"Strat {i+1}" for i in range(len(strategies))],
                        "Profit": [current_profit, goal_profit] + [s["Projected Profit"] for s in strategies]
                    })
                    st.bar_chart(chart_data.set_index("Type"), color="#00C0F1")
    else:
        st.info("👈 Adjust your business metrics in the sidebar and click **'Run Simulation'** to see your paths to profit.")

# --- TAB 2: PRICE FINDER ---
with tab2:
    with st.container(border=True):
        st.subheader("Smart Sourcing (AI)")
        st.write(f"Scrapes Alibaba and 1688 to find wholesale prices, converted to **{selected_currency}**.")
        
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            product_input = st.text_input("Product to source:", placeholder="e.g., 'coffee beans', 'packaging boxes'", label_visibility="collapsed")
        with col_btn:
            search_btn = st.button("Search Prices", use_container_width=True, type="primary")
            
        if search_btn and product_input:
            with st.spinner("Connecting to global supply chain database..."):
                results = ai_tools.ai_search_suppliers(product_input, target_currency=selected_currency)
                
                if results and "Error" in results[0]:
                    st.error(results[0]["Error"])
                else:
                    st.success("Found cheapest suppliers!")
                    st.dataframe(
                        results,
                        use_container_width=True,
                        column_config={
                            "Link": st.column_config.LinkColumn("Order Link", display_text="View Product")
                        }
                    )

# --- TAB 3: INFLUENCER FINDER ---
with tab3:
    with st.container(border=True):
        st.subheader("Influencer Scouting (AI)")
        st.write("Identifies local creators and extracts their stats and contact info.")
        
        col_city, col_niche, col_platform = st.columns(3)
        with col_city:
            default_city = "Tbilisi" if selected_country == "Georgia" else "New York"
            city = st.text_input("Target City", value=default_city)
        with col_niche:
            niche = st.text_input("Industry / Niche", value="Food")
        with col_platform:
            platform = st.selectbox("Platform", ["Instagram", "TikTok"])
            
        scout_btn = st.button("Find Creators", use_container_width=True, type="primary")
            
        if scout_btn:
            with st.spinner(f"Scouting top {platform} creators..."):
                inf_results = ai_tools.ai_find_influencers(city, niche, platform)
                
                if inf_results and "Error" in inf_results[0]:
                    st.error(inf_results[0]["Error"])
                else:
                    st.success(f"Found creators in {city}!")
                    st.dataframe(
                        inf_results,
                        use_container_width=True,
                        column_config={
                            "Photo": st.column_config.ImageColumn("Profile Photo", width="small"),
                            "Name": st.column_config.TextColumn("Full Name"),
                            "Followers": st.column_config.NumberColumn("Followers", format="%d"),
                            "Contact": st.column_config.TextColumn("Contact Info"),
                            "Link": st.column_config.LinkColumn("Profile Link", display_text="View Profile")
                        },
                        hide_index=True
                    )

# --- TAB 4: COMPETITOR MOCKUP ---
with tab4:
    with st.container(border=True):
        st.subheader("Competitor Analysis")
        st.write("See how your pricing stacks up against a local competitor.")
        
        col_comp, col_analyze = st.columns([1, 2])
        
        with col_comp:
            comp_name = st.text_input("Competitor Name (Optional)", value="Local Competitor")
            comp_price = st.number_input(f"{comp_name}'s Price ({currency_symbol})", value=4.50, step=0.50)
            
        with col_analyze:
            if comp_price > 0:
                price_diff = price - comp_price
                percent_diff = (price_diff / comp_price) * 100
                
                col_my, col_theirs = st.columns(2)
                col_my.metric("Your Price", f"{currency_symbol}{price:.2f}", f"{percent_diff:.1f}% vs Competitor")
                col_theirs.metric(f"{comp_name} Price", f"{currency_symbol}{comp_price:.2f}")
                
                st.write("")
                
                if price > comp_price:
                    st.warning(f"⚠️ You are **more expensive** than {comp_name} by {currency_symbol}{abs(price_diff):.2f} ({abs(percent_diff):.1f}%).")
                    st.info("💡 **Strategy Tip:** You may need to justify this higher price by emphasizing better quality, faster service, or a superior atmosphere. Alternatively, use the Strategy Simulator to see if you can cut costs to match their price.")
                elif price < comp_price:
                    st.success(f"✅ You are **cheaper** than {comp_name} by {currency_symbol}{abs(price_diff):.2f} ({abs(percent_diff):.1f}%).")
                    st.info("💡 **Strategy Tip:** This is a massive advantage! Highlight your affordability in your marketing campaigns and on social media to steal their customers.")
                else:
                    st.info(f"🤝 You and {comp_name} have the exact same price.")
                    st.info("💡 **Strategy Tip:** Since price isn't a differentiator, compete on customer service, loyalty programs, or product uniqueness.")