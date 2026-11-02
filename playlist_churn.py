
# ==================================================
# ATLANTIC RECORDING CORPORATION
# SPAIN TOP 50 - PLAYLIST ROTATION & CHURN ANALYSIS
# ==================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Project directory
BASE_DIR = Path(__file__).parent

# 2. Create output folder
OUTPUT_DIR = BASE_DIR / "Churn_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# 3. Load original dataset
df = pd.read_csv(BASE_DIR / "Atlantic_Spain.csv")

# 4. Convert date format
df["date"] = pd.to_datetime(
    df["date"],
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(subset=["date"])

# 5. Normalize song and artist names
df["song_key"] = (
    df["song"].astype(str).str.strip().str.casefold()
)

df["artist_key"] = (
    df["artist"].astype(str).str.strip().str.casefold()
)

# 6. Convert position into numeric format
df["position"] = pd.to_numeric(
    df["position"], errors="coerce"
)

df = df.dropna(
    subset=["position", "song_key", "artist_key"]
)

# 7. Remove duplicate playlist positions
df = df.sort_values(["date", "position"])

df = df.drop_duplicates(
    subset=["date", "position"],
    keep="first"
)

# 8. Keep one appearance per song-artist per date
df = df.drop_duplicates(
    subset=["date", "song_key", "artist_key"],
    keep="first"
)

# 9. Create song identification key
df["song_id"] = (
    df["song_key"] + " | " + df["artist_key"]
)

# 10. Create daily playlist snapshots
daily_playlists = {}

for date, group in df.groupby("date"):

    daily_playlists[date] = set(group["song_id"])

dates = sorted(daily_playlists.keys())

# 11. Calculate daily entries, exits and retention
daily_results = []

for i in range(1, len(dates)):

    previous_date = dates[i - 1]
    current_date = dates[i]

    previous_songs = daily_playlists[previous_date]
    current_songs = daily_playlists[current_date]

    # Songs newly entering the playlist
    new_entries = current_songs - previous_songs

    # Songs leaving the playlist
    exits = previous_songs - current_songs

    # Songs remaining in the playlist
    retained = previous_songs & current_songs

    previous_size = len(previous_songs)

    # Entry churn percentage
    entry_churn = (
        len(new_entries) / previous_size * 100
        if previous_size > 0 else 0
    )

    # Exit churn percentage
    exit_churn = (
        len(exits) / previous_size * 100
        if previous_size > 0 else 0
    )

    # Percentage of songs retained
    retention_rate = (
        len(retained) / previous_size * 100
        if previous_size > 0 else 0
    )

    daily_results.append({

        "date": current_date,

        "previous_date": previous_date,

        "days_between_snapshots": (
            current_date - previous_date
        ).days,

        "previous_playlist_size": previous_size,

        "current_playlist_size": len(current_songs),

        "new_entries": len(new_entries),

        "exits": len(exits),

        "retained_songs": len(retained),

        "entry_churn_rate": round(entry_churn, 2),

        "exit_churn_rate": round(exit_churn, 2),

        "retention_rate": round(retention_rate, 2)
    })

# 12. Create daily results DataFrame
daily_df = pd.DataFrame(daily_results)

# 13. Display daily results
print("\n========== DAILY PLAYLIST CHURN ==========")

print(daily_df.head(10).to_string(index=False))

# 14. Calculate overall statistics
print("\n========== OVERALL CHURN STATISTICS ==========")

print(
    "Average New Entries:",
    round(daily_df["new_entries"].mean(), 2)
)

print(
    "Average Exits:",
    round(daily_df["exits"].mean(), 2)
)

print(
    "Average Entry Churn Rate:",
    round(daily_df["entry_churn_rate"].mean(), 2), "%"
)

print(
    "Average Exit Churn Rate:",
    round(daily_df["exit_churn_rate"].mean(), 2), "%"
)

print(
    "Average Retention Rate:",
    round(daily_df["retention_rate"].mean(), 2), "%"
)

print(
    "Average Days Between Snapshots:",
    round(daily_df["days_between_snapshots"].mean(), 2)
)

# 15. Save daily churn results
daily_df.to_csv(
    OUTPUT_DIR / "daily_churn_analysis.csv",
    index=False
)

# 16. Monthly churn analysis
daily_df["month"] = (
    daily_df["date"].dt.to_period("M")
)

monthly_df = (
    daily_df.groupby("month")
    .agg(
        total_entries=("new_entries", "sum"),

        total_exits=("exits", "sum"),

        average_entries=("new_entries", "mean"),

        average_exits=("exits", "mean"),

        average_retention=("retention_rate", "mean"),

        total_previous_songs=(
            "previous_playlist_size", "sum"
        )
    )
    .reset_index()
)

# 17. Calculate monthly churn rates
monthly_df["entry_churn_rate"] = (
    monthly_df["total_entries"]
    / monthly_df["total_previous_songs"] * 100
).round(2)

monthly_df["exit_churn_rate"] = (
    monthly_df["total_exits"]
    / monthly_df["total_previous_songs"] * 100
).round(2)

monthly_df["month"] = (
    monthly_df["month"].astype(str)
)

print("\n========== MONTHLY PLAYLIST CHURN ==========")

print(monthly_df.to_string(index=False))

# 18. Save monthly results
monthly_df.to_csv(
    OUTPUT_DIR / "monthly_churn_analysis.csv",
    index=False
)

# 19. Graph 1 - Daily Entries and Exits
plt.figure(figsize=(13, 6))

plt.plot(
    daily_df["date"],
    daily_df["new_entries"],
    label="New Entries"
)

plt.plot(
    daily_df["date"],
    daily_df["exits"],
    label="Exits"
)

plt.title("Daily Playlist Entries and Exits")
plt.xlabel("Date")
plt.ylabel("Number of Songs")

plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "daily_entries_exits.png"
)

plt.show()

# 20. Graph 2 - Monthly Churn Rate
plt.figure(figsize=(12, 6))

plt.plot(
    monthly_df["month"],
    monthly_df["entry_churn_rate"],
    marker="o",
    label="Entry Churn"
)

plt.plot(
    monthly_df["month"],
    monthly_df["exit_churn_rate"],
    marker="o",
    label="Exit Churn"
)

plt.title("Monthly Playlist Churn Rate")
plt.xlabel("Month")
plt.ylabel("Churn Rate (%)")

plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "monthly_churn_rate.png"
)

plt.show()

# 21. Graph 3 - Monthly Average Retention
plt.figure(figsize=(12, 6))

plt.bar(
    monthly_df["month"],
    monthly_df["average_retention"]
)

plt.title("Monthly Average Playlist Retention")
plt.xlabel("Month")
plt.ylabel("Retention Rate (%)")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "monthly_retention.png"
)

plt.show()

print("\n======================================")
print("PLAYLIST CHURN ANALYSIS COMPLETED!")
print("Check the Churn_Results folder.")
print("======================================")
