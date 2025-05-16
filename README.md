# Sports Odds Bot

A Python toolkit to fetch live IPL & EPL odds, detect risk-free single-match arbitrage, and interactively demo bet-slip preparation on Unibet & Betfair in dry-run mode.

---

## 📋 Prerequisites

- Python 3.10+  
- Google Chrome  
- ChromeDriver (managed via webdriver-manager)  
- Accounts on Unibet & Betfair  
- API key from [the-odds-api.com](https://the-odds-api.com)

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rishab-acharya/sports-odds-monitor.git
   cd sports-odds-monitor
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1    # PowerShell on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with your credentials and API key:
   ```ini
   ODDS_API_KEY=your_odds_api_key
   B365_USER=your_betfair_username
   B365_PASS=your_betfair_password
   UNI_USER=your_unibet_username
   UNI_PASS=your_unibet_password
   DRY_RUN=true
   ```

## 🎯 Usage

### 1. Fetch Odds (EPL & IPL)
```bash
python fetch_odds.py
```
- Generates `latest_odds.csv` containing:
  - EPL matches (Home, Draw, Away)  
  - IPL matches (Home, Away; Draw excluded)

### 2. Find Single-Match Arbitrage
```bash
python arb_finder.py
```
- Prints opportunities and saves `arbitrage_opportunities.csv`.

### 3. Interactive Selenium Demo
```bash
python selenium_demo_interactive.py
```
- Lists detected arbs, prompts for selection, then opens browser windows to:
  - Log in to Unibet & Betfair  
  - Fill each leg’s bet-slip in dry-run (no real bets placed)

---

## 📝 File Summary

- `fetch_odds.py`  
- `arb_finder.py`  
- `selenium_demo_interactive.py`  
- `.env.example`  
- `requirements.txt`

---

## 📂 Updating the README

After editing:
```bash
git add README.md .env.example
git commit -m "📄 Update README with complete instructions"
git push
```
