# selenium_demo_interactive.py

import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─── LOAD CONFIG ──────────────────────────────────────────────────────────────
load_dotenv()
B365_USER = os.getenv("B365_USER")
B365_PASS = os.getenv("B365_PASS")
UNI_USER = os.getenv("UNI_USER")
UNI_PASS = os.getenv("UNI_PASS")
DRY_RUN   = os.getenv("DRY_RUN", "true").lower() == "true"

if not all([B365_USER, B365_PASS, UNI_USER, UNI_PASS]):
    print("❌ Please fill in B365_USER/B365_PASS and UNI_USER/UNI_PASS in your .env")
    sys.exit(1)

# ─── SELENIUM HELPERS ──────────────────────────────────────────────────────────
def init_driver(headless=False):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless")
        opts.add_argument("--disable-gpu")
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=opts
    )

def login_unibet(driver):
    """
    1) Go to Unibet homepage
    2) Accept cookies
    3) Open login modal
    4) Enter credentials & submit
    5) Wait for account element
    """
    wait = WebDriverWait(driver, 15)
    driver.get("https://www.unibet.com")

    # Accept cookie banner if present
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[contains(text(),'Allow necessary only') or contains(text(),'Allow all cookies')]"
        )))
        cookie_btn.click()
    except:
        pass

    # Open login modal
    login_link = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//a[contains(@href,'/login') or contains(text(),'Log in')]"
    )))
    login_link.click()

    # Wait for modal to appear
    time.sleep(1)

    # Enter credentials
    wait.until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys(UNI_USER)
    driver.find_element(By.NAME, "password").send_keys(UNI_PASS)
    driver.find_element(By.XPATH, "//button[contains(text(),'Log in')]").click()

    # Confirm login
    wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "button[aria-label*='My account'], .account-overview"
    )))
    print("✅ Logged into Unibet successfully")

def login_betfair(driver):
    """
    1) Go to Betfair exchange football
    2) Accept cookies
    3) Click Log In (opens iframe)
    4) Switch to iframe, fill creds & submit
    5) Switch back and confirm login
    """
    wait = WebDriverWait(driver, 15)
    driver.get("https://www.betfair.com/exchange/football")

    # Accept cookie banner if present
    try:
        btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[contains(text(),'Accept Cookies') or contains(text(),'Allow necessary only')]"
        )))
        btn.click()
    except:
        pass

    # Click the Log In button
    login_btn = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "button[data-test='header-login-button'], button[aria-label='Log in']"
    )))
    login_btn.click()

    # Switch into login SSO iframe
    iframe = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "iframe[src*='identitysso.betfair.com']"
    )))
    driver.switch_to.frame(iframe)

    # Enter credentials
    wait.until(EC.element_to_be_clickable((By.ID, "ssousername"))).send_keys(B365_USER)
    driver.find_element(By.ID, "ssopassword").send_keys(B365_PASS)
    driver.find_element(By.ID, "login-button").click()

    # Back to main content
    driver.switch_to.default_content()

    # Confirm login
    wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "span[data-test='header-account-button'], .market-container"
    )))
    print("✅ Logged into Betfair successfully")

def navigate_and_click(driver, match, outcome):
    """
    Searches for the match name and clicks the given outcome price button.
    """
    wait = WebDriverWait(driver, 10)
    search = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.search-input")))
    search.clear()
    search.send_keys(match)
    time.sleep(1)
    driver.find_element(By.XPATH, f"//span[text()='{match}']").click()

    btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//button[contains(.,'{outcome}') and contains(@class,'price-button')]"
    )))
    btn.click()

def place_bet(driver):
    if DRY_RUN:
        print("  ⏸ DRY RUN: skipping final Place Bet click")
    else:
        driver.find_element(By.XPATH, "//button[contains(text(),'Place bet')]").click()
        print("  ✅ Bet placed!")

# ─── MAIN DEMO FLOW ────────────────────────────────────────────────────────────
def main():
    arb_file = "arbitrage_opportunities.csv"
    if not os.path.exists(arb_file):
        print(f"🔍 Run arb_finder.py first to generate {arb_file}")
        return

    df = pd.read_csv(arb_file)
    if df.empty:
        print("🔍 No arbitrage opportunities to demo.")
        return

    # List opportunities
    print("🏆 Available Arbs:\n")
    for i, row in df.iterrows():
        print(f"[{i}] {row.Match} → Edge {row['Edge (%)']}%")
    idx = int(input("\nEnter the number of the arb to demo: "))
    if idx not in df.index:
        print("❌ Invalid selection.")
        return

    sel = df.loc[idx]
    legs = [leg.strip() for leg in sel.Details.split(";")]

    # Demo each leg
    for leg in legs:
        outcome, rest = leg.split("@", 1)
        price, bookie = rest.split(" ", 1)
        bookie = bookie.strip("()")
        print(f"\n➡️  Demo: {sel.Match} → {outcome}@{price} on {bookie}")

        driver = init_driver(headless=False)
        try:
            if bookie.lower() == "unibet":
                login_unibet(driver)
            elif "betfair" in bookie.lower() or "bet365" in bookie.lower():
                login_betfair(driver)
            else:
                print("  ❌ Unsupported bookmaker:", bookie)
                driver.quit()
                continue

            navigate_and_click(driver, sel.Match, outcome)
            place_bet(driver)

        except Exception as e:
            print("  ⚠️  Demo error:", e)
        finally:
            time.sleep(2)
            driver.quit()

    print("\n✅ Demo complete.")

if __name__ == "__main__":
    main()
