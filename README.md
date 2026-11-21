# WhatIf - Business Decision Simulator

**Author:** Salome Sulamanidze
**Course:** INFO SCI 102

## Overview
WhatIf is a web-based decision-support tool designed for small business owners (like cafes). It helps users see the financial impact of different business decisions before making them in real life. 

## Features
1. **Profit Simulator:** Uses a grid-search algorithm to find combinations of price increases, cost cuts, and sales increases to hit a specific profit goal. It includes a "Risk Score" to recommend the safest path.
2. **AI Price Finder:** Connects to Apify to scrape Alibaba for the cheapest wholesale prices, helping business owners reduce their baseline costs.
3. **AI Influencer Finder:** Uses web scraping (DuckDuckGo) to find local influencers in a specific city and extracts their contact emails.

## How to Run Locally
1. Clone this repository.
2. Install the requirements: `pip install -r requirements.txt`
3. Create a `.streamlit/secrets.toml` file and add your Apify token: `APIFY_TOKEN = "your_token_here"`
4. Run the app: `streamlit run app.py`