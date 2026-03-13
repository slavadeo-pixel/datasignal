from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

def calculate_probability(home_win, home_goals, away_loss, away_concede, form):
    probability = (
        home_win * 0.35 +
        home_goals * 10 * 0.2 +
        away_loss * 0.25 +
        away_concede * 10 * 0.1 +
        form * 5 * 0.1
    ) / 100
    return probability

def calculate_odds(probability):
    if probability <= 0:
        return 0
    return round(1 / probability, 2)

def analyze():
    files = [
        "data/E0.csv",
        "data/SP1.csv",
        "data/I1.csv",
        "data/D1.csv",
        "data/F1.csv"
    ]

    results = []

    for file in files:
        df = pd.read_csv(file)

        teams = df["HomeTeam"].unique()

        for team in teams:

            home = df[df["HomeTeam"] == team]
            away = df[df["AwayTeam"] == team]

            if len(home) < 5 or len(away) < 5:
                continue

            home_wins = len(home[home["FTR"] == "H"])
            home_games = len(home)

            away_losses = len(away[away["FTR"] == "H"])
            away_games = len(away)

            home_goals = home["FTHG"].mean()
            away_concede = away["FTHG"].mean()
            form = len(home.tail(5)[home.tail(5)["FTR"] == "H"])

            home_win = (home_wins / home_games) * 100
            away_loss = (away_losses / away_games) * 100

            probability = calculate_probability(home_win, home_goals, away_loss, away_concede, form)
            odds = calculate_odds(probability)

            results.append({
                "team": team,
                "home_win": round(home_win, 1),
                "home_goals": round(home_goals, 2),
                "away_loss": round(away_loss, 1),
                "form": form,
                "prob": round(probability * 100, 1),
                "odds": odds
            })

    # сортировка по вероятности
    results = sorted(results, key=lambda x: x["prob"], reverse=True)

    return results[:20]

@app.route("/")
def index():
    matches = analyze()
    return render_template("index.html", matches=matches)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
