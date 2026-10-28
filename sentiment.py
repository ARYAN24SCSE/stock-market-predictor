"""
Sentiment Analysis Module using VADER (Valence Aware Dictionary and sEntiment Reasoner)
Analyzes stock market news headlines and produces compound scores and market stance
(Bullish / Neutral / Bearish).
"""

from typing import Dict, List
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Initialize analyzer instance
_analyzer = SentimentIntensityAnalyzer()

# Financial domain lexicons to refine VADER sensitivity for market terms
FINANCIAL_LEXICON_UPDATES = {
    "surge": 2.5,
    "surges": 2.5,
    "surging": 2.5,
    "soar": 2.5,
    "soars": 2.5,
    "bullish": 2.8,
    "rally": 2.2,
    "rallies": 2.2,
    "breakout": 2.0,
    "outperform": 2.2,
    "upgrade": 2.0,
    "upgraded": 2.0,
    "dividend": 1.2,
    "profit": 1.8,
    "record": 1.5,
    "plunge": -2.8,
    "plunges": -2.8,
    "plunging": -2.8,
    "slump": -2.5,
    "slumps": -2.5,
    "bearish": -2.8,
    "selloff": -2.6,
    "downgrade": -2.2,
    "downgraded": -2.2,
    "lawsuit": -2.0,
    "investigation": -1.8,
    "drop": -1.5,
    "drops": -1.5,
    "losses": -2.0,
}
_analyzer.lexicon.update(FINANCIAL_LEXICON_UPDATES)


def analyze_headline(headline: str) -> Dict:
    """
    Computes sentiment scores for a single headline.
    Returns:
    - compound: [-1.0 to 1.0]
    - pos, neu, neg: [0.0 to 1.0]
    - sentiment: Bullish / Neutral / Bearish
    """
    if not headline or not headline.strip():
        return {
            "compound": 0.0,
            "pos": 0.0,
            "neu": 1.0,
            "neg": 0.0,
            "sentiment": "Neutral",
            "emoji": "⚪"
        }

    scores = _analyzer.polarity_scores(headline)
    compound = scores["compound"]

    if compound >= 0.15:
        sentiment = "Bullish"
        emoji = "🟢"
    elif compound <= -0.15:
        sentiment = "Bearish"
        emoji = "🔴"
    else:
        sentiment = "Neutral"
        emoji = "⚪"

    return {
        "compound": round(compound, 3),
        "pos": round(scores["pos"], 3),
        "neu": round(scores["neu"], 3),
        "neg": round(scores["neg"], 3),
        "sentiment": sentiment,
        "emoji": emoji
    }


def analyze_news_list(news_items: List[Dict]) -> Dict:
    """
    Processes a list of news items (each containing 'title', 'publisher', etc.)
    Returns:
    - enriched_df: DataFrame containing all items with their sentiment scores
    - summary: aggregate statistics (overall compound, bullish/neutral/bearish counts, stance)
    """
    if not news_items:
        return {
            "enriched_df": pd.DataFrame(),
            "summary": {
                "overall_score": 0.0,
                "overall_sentiment": "Neutral",
                "bullish_count": 0,
                "neutral_count": 0,
                "bearish_count": 0,
                "total_count": 0,
                "bullish_pct": 0.0,
                "bearish_pct": 0.0,
            }
        }

    records = []
    compounds = []
    bullish_count = 0
    neutral_count = 0
    bearish_count = 0

    for item in news_items:
        title = item.get("title", "")
        res = analyze_headline(title)
        compounds.append(res["compound"])

        if res["sentiment"] == "Bullish":
            bullish_count += 1
        elif res["sentiment"] == "Bearish":
            bearish_count += 1
        else:
            neutral_count += 1

        records.append({
            "Published": item.get("published", "N/A"),
            "Headline": title,
            "Source": item.get("publisher", "Yahoo/Finnhub"),
            "Sentiment": f"{res['emoji']} {res['sentiment']}",
            "Score": res["compound"],
            "URL": item.get("link", "#")
        })

    df = pd.DataFrame(records)
    avg_score = round(float(sum(compounds) / len(compounds)), 3) if compounds else 0.0
    total = len(news_items)

    if avg_score >= 0.10:
        overall_sentiment = "Bullish"
    elif avg_score <= -0.10:
        overall_sentiment = "Bearish"
    else:
        overall_sentiment = "Neutral"

    summary = {
        "overall_score": avg_score,
        "overall_sentiment": overall_sentiment,
        "bullish_count": bullish_count,
        "neutral_count": neutral_count,
        "bearish_count": bearish_count,
        "total_count": total,
        "bullish_pct": round((bullish_count / total) * 100, 1) if total > 0 else 0.0,
        "bearish_pct": round((bearish_count / total) * 100, 1) if total > 0 else 0.0,
    }

    return {
        "enriched_df": df,
        "summary": summary
    }
