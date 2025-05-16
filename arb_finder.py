# arb_finder.py

import pandas as pd

def find_arbitrage(df, threshold=0.0):
    """
    Returns a DataFrame of matches where
    sum(1 / best_price_per_outcome) < 1 - threshold%
    """
    arbs = []
    for match, grp in df.groupby('Match'):
        # pick the best price for each distinct outcome
        best = grp.loc[grp.groupby('Outcome')['Price'].idxmax()]
        best = best.copy()
        best['ImpliedProb'] = 1.0 / best['Price']
        total = best['ImpliedProb'].sum()
        edge = (1.0 - total) * 100
        if edge > threshold:
            arbs.append({
                'Match': match,
                'Edge (%)': round(edge, 2),
                'Details': "; ".join(
                    f"{row.Outcome}@{row.Price} ({row.Bookmaker})"
                    for _, row in best.iterrows()
                )
            })
    return pd.DataFrame(arbs)

if __name__ == "__main__":
    # load the combined odds file
    df = pd.read_csv('latest_odds.csv')
    # find any sure-bet edge > 0%
    arb_df = find_arbitrage(df, threshold=0.0)
    if arb_df.empty:
        print("🔍 No arbitrage opportunities found.")
    else:
        print("🏆 Arbitrage opportunities:")
        print(arb_df.to_string(index=False))
        arb_df.to_csv('arbitrage_opportunities.csv', index=False)
        print("📁 Saved arbitrage_opportunities.csv")
