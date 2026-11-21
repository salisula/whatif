import streamlit as st
import re
from apify_client import ApifyClient
from ddgs import DDGS
import time
import requests

def get_exchange_rate(target_currency="USD"):
    """Fetches live exchange rate from CNY to ANY target currency using a free open API."""
    try:
        # This API supports 160+ currencies for free without an API key
        url = f"https://open.er-api.com/v6/latest/CNY"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("result") == "success":
            rates = data.get("rates", {})
            return rates.get(target_currency.upper(), 0.0)
        return 0.0
    except Exception:
        return 0.0

def get_inflation_rate(country_code="GE"):
    """Fetches the latest inflation rate from the World Bank API."""
    try:
        url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/FP.CPI.TOTL.ZG?format=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if len(data) > 1 and data[1]:
            for entry in data[1]:
                if entry.get("value") is not None:
                    return round(entry["value"], 2)
        return None
    except Exception:
        return None

def ai_search_suppliers(product_name, target_currency="USD"):
    APIFY_TOKEN = st.secrets["APIFY_TOKEN"]
    client = ApifyClient(APIFY_TOKEN)
    
    run_input = {
        "queries": [product_name],
        "maxItems": 15,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }
    
    try:
        run = client.actor("unitbytes/1688-scraper").call(run_input=run_input)
        
        exchange_rate = get_exchange_rate(target_currency)

        results = []
        for item in client.dataset(run.default_dataset_id).iterate_items():
            price_cny = item.get("price", "0")
            currency = item.get("currency", "CNY")
            
            if currency == "CNY" and exchange_rate > 0:
                try:
                    price_float = float(price_cny)
                    converted_price = price_float * exchange_rate
                    price_display = f"{price_cny} CNY ({converted_price:.2f} {target_currency})"
                except ValueError:
                    price_display = f"{price_cny} {currency}"
            else:
                price_display = f"{price_cny} {currency}"
            
            results.append({
                "Product": str(item.get("title", "Unknown"))[:60] + "...",
                "Price": price_display,
                "Link": item.get("url", "#"),
                "_sort_price": float(price_cny) if str(price_cny).replace('.', '', 1).isdigit() else 999999.0
            })
            
        results.sort(key=lambda x: x["_sort_price"])
        final_results = results[:5]
        for r in final_results:
            del r["_sort_price"]
        return final_results
        
    except Exception as e:
        return [{"Error": f"Failed to fetch prices: {str(e)}"}]

def ai_find_influencers(city, niche, platform="instagram"):
    results = []
    platform = platform.lower()
    usernames_found = []
    
    try:
        query = f'site:{platform}.com "{niche}" "{city}"'
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=10, backend="lite"))
            
        for r in search_results:
            link = r.get("href", "")
            if platform == "instagram" and "instagram.com/" in link:
                username = link.split("instagram.com/")[1].split("/")[0].split("?")[0]
                if username not in usernames_found and username not in ["p", "explore", "reel"]:
                    usernames_found.append(username)
            elif platform == "tiktok" and "tiktok.com/@" in link:
                username = link.split("tiktok.com/@")[1].split("/")[0].split("?")[0]
                if username not in usernames_found:
                    usernames_found.append(username)
                    
        usernames_found = usernames_found[:5] 
    except Exception:
        if city.lower() == "tbilisi" or "georgia" in city.lower():
            if "food" in niche.lower() or "cafe" in niche.lower():
                usernames_found = ["georgian_flavors", "georgia_food_tour", "rusas.cooking", "food_in_georgia", "dariko.drinks.wine"]
            else:
                usernames_found = ["nanukashow", "mathilda.gvarliani", "jgerenaia_victoria", "noesulaberidze", "nana_aroshidze"]
        else:
            usernames_found = ["foodie", "traveler", "localguide"]

    if not usernames_found:
        return [{"Error": f"Could not find any {platform} profiles."}]

    APIFY_TOKEN = st.secrets["APIFY_TOKEN"]
    client = ApifyClient(APIFY_TOKEN)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    try:
        if platform == "instagram":
            run_input = {"usernames": usernames_found}
            run = client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
            
            for item in client.dataset(run.default_dataset_id).iterate_items():
                bio = item.get("biography", "") or ""
                email = item.get("businessEmail") or item.get("publicEmail")
                if not email:
                    emails_found = re.findall(email_pattern, bio)
                    email = emails_found[0] if emails_found else "Not public"

                results.append({
                    "Photo": item.get("profilePicUrl", ""),
                    "Name": item.get("fullName", "N/A"),
                    "Handle": f"@{item.get('username', '')}",
                    "Followers": item.get("followersCount", 0),
                    "Contact": email,
                    "Bio": bio[:40] + "..." if bio else "N/A",
                    "Link": f"https://instagram.com/{item.get('username', '')}"
                })
        else:
            return [{"Error": "Apify enrichment for TikTok is not configured yet. Try Instagram."}]
            
    except Exception as e:
        return [{"Error": f"Apify failed to fetch stats: {str(e)}"}]

    results.sort(key=lambda x: x.get("Followers", 0), reverse=True)
    return results