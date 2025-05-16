# fetch_odds.py

import os
import requests
import pandas as pd
from dotenv import load_dotenv

def load_api_key():
    load_dotenv()
    key = os.getenv('ODDS_API_KEY')
    if not key:
        print("❌ ERROR: ODDS_API_KEY not found in .env")
        exit(1)
    return key

def fetch_sport_odds(sport_key, regions, exclude=None):
    """
    Fetch odds for a given sport_key.
    exclude: an outcome name (case-insensitive) to skip (e.g. 'draw').
    """
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        'apiKey': API_KEY,
        'regions': regions,
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"❌ ERROR fetching {sport_key}: {resp.status_code} {resp.text}")
        return []
    data = resp.json()
    rows = []
    for match in data:
        home = match['home_team']
        away = match['away_team']
        for book in match.get('bookmakers', []):
            for market in book.get('markets', []):
                for outcome in market.get('outcomes', []):
                    name = outcome['name'].strip()
                    # skip unwanted outcomes
                    if exclude and name.lower() == exclude.lower():
                        continue
                    rows.append({
                        'Match': f"{home} vs {away}",
                        'Bookmaker': book['title'],
                        'Outcome': name,
                        'Price': outcome['price']
                    })
    return rows

if __name__ == "__main__":
    API_KEY = load_api_key()

    all_rows = []
    # 1) Premier League (include Draw)
    all_rows += fetch_sport_odds(
        sport_key="soccer_epl",
        regions="uk",       # UK books for EPL
        exclude=None        # no exclusion: include draw
    )

    # 2) IPL (exclude Draw)
    all_rows += fetch_sport_odds(
        sport_key="cricket_ipl",
        regions="uk,au",    # remove 'in'—use UK & AU
        exclude="Draw"      # skip Draw outcome
    )

    df = pd.DataFrame(all_rows)
    out_file = "latest_odds.csv"
    df.to_csv(out_file, index=False)
    print(f"✅ Saved {len(df)} rows to {out_file}")
