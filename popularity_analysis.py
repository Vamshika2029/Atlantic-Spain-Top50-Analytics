
# ==================================================
# ATLANTIC RECORDING CORPORATION
# SPAIN TOP 50 - POPULARITY VS LIFECYCLE ANALYSIS
# ==================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 1. Project directory
BASE_DIR = Path(__file__).parent

# 2. Create output folder
OUTPUT_DIR = BASE_DIR / "Popularity_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# 3. Load original dataset
df = pd.read_csv(BASE_DIR / "Atlantic_Spain.csv")

# 4. Convert columns
df["date"] = pd.to_datetime(
    df["date"], dayfirst=True, errors="coerce"
)

df["position"] = pd.to_numeric(
    df["position"], errors="coerce"
)

df["popularity"] = pd.to_numeric(
    df["popularity"], errors="coerce"
)

df = df.dropna(
    subset=["date", "song", "artist", "position", "popularity"]
)

# 5. Normalize song and artist names
df["song_key"] = (
    df["song"].astype(str).str.strip().str.casefold()
)

df["artist_key"] = (
    df["artist"].astype(str).str.strip().str.casefold()
)

# 6. Remove duplicate playlist positions
df = df.sort_values(["date", "position"])

df = df.drop_duplicates(
    subset=["date", "position"],
    keep="first"
)

# 7. Remove repeated song appearances on the same date
df = df.drop_duplicates(
    subset=["date", "song_key", "artist_key"],
    keep="first"
)

# 8. Sort observations
df = df.sort_values(
    ["song_key", "artist_key", "date"]
)

# 9. Create song-level popularity summary
song_results = []

for (song, artist), group in df.groupby(
    ["song_key", "artist_key"]
):

    group = group.sort_values("date")

    first_date = group["date"].iloc[0]

    last_date = group["date"].iloc[-1]

    first_popularity = group["popularity"].iloc[0]

    last_popularity = group["popularity"].iloc[-1]

    max_popularity = group["popularity"].max()

    peak_popularity_date = group.loc[
        group["popularity"].idxmax(), "date"
    ]

    # Calculate popularity change
    popularity_change = (
        last_popularity - first_popularity
    )

    # Calculate time to highest observed popularity
    days_to_peak_popularity = (
        peak_popularity_date - first_date
    ).days

    song_results.append({

        "song": group["song"].iloc[0],

        "artist": group["artist"].iloc[0],

        "first_date": first_date,

        "last_date": last_date,

        "first_popularity": first_popularity,

        "last_popularity": last_popularity,

        "maximum_popularity": max_popularity,

        "popularity_change": popularity_change,

        "days_to_peak_popularity": days_to_peak_popularity,

        "average_popularity": group["popularity"].mean(),

        "peak_chart_position": group["position"].min(),

        "observed_chart_days": group["date"].nunique()
    })

# 10. Create DataFrame
popularity_df = pd.DataFrame(song_results)

# 11. Save song-level results
popularity_df.to_csv(
    OUTPUT_DIR / "song_popularity_lifecycle.csv",
    index=False
)

print("\n========== POPULARITY LIFECYCLE SUMMARY ==========")

print(
    "Total songs:",
    len(popularity_df)
)

print(
    "Average first popularity:",
    round(popularity_df["first_popularity"].mean(), 2)
)

print(
    "Average last popularity:",
    round(popularity_df["last_popularity"].mean(), 2)
)

print(
    "Average maximum popularity:",
    round(popularity_df["maximum_popularity"].mean(), 2)
)

print(
    "Average popularity change:",
    round(popularity_df["popularity_change"].mean(), 2)
)

print(
    "Average days to peak popularity:",
    round(popularity_df["days_to_peak_popularity"].mean(), 2)
)

# 12. Correlation analysis
correlation = popularity_df[
    ["average_popularity", "observed_chart_days",
     "peak_chart_position"]
].corr()

print("\n========== POPULARITY CORRELATION ==========")

print(correlation.round(3).to_string())

correlation.to_csv(
    OUTPUT_DIR / "popularity_correlation.csv"
)

# 13. Positive and negative popularity changes
positive_growth = (
    popularity_df["popularity_change"] > 0
).sum()

negative_growth = (
    popularity_df["popularity_change"] < 0
).sum()

no_change = (
    popularity_df["popularity_change"] == 0
).sum()

print("\n========== POPULARITY MOVEMENT ==========")

print("Popularity increased:", positive_growth)

print("Popularity decreased:", negative_growth)

print("No change:", no_change)

# 14. Display top 10 songs by popularity
top_songs = popularity_df.sort_values(
    "maximum_popularity",
    ascending=False
).head(10)

print("\n========== TOP 10 SONGS BY MAXIMUM POPULARITY ==========")

print(
    top_songs[
        ["song", "artist", "maximum_popularity",
         "popularity_change", "observed_chart_days"]
    ].to_string(index=False)
)

# 15. Graph 1 - First vs Last Popularity
plt.figure(figsize=(9, 6))

plt.scatter(
    popularity_df["first_popularity"],
    popularity_df["last_popularity"]
)

plt.title("First vs Last Song Popularity")

plt.xlabel("First Appearance Popularity")

plt.ylabel("Last Appearance Popularity")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "first_vs_last_popularity.png"
)

plt.show()

# 16. Graph 2 - Popularity Change Distribution
plt.figure(figsize=(9, 6))

plt.hist(
    popularity_df["popularity_change"],
    bins=25
)

plt.title("Distribution of Song Popularity Changes")

plt.xlabel("Popularity Change")

plt.ylabel("Number of Songs")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "popularity_change_distribution.png"
)

plt.show()

# 17. Graph 3 - Popularity vs Chart Longevity
plt.figure(figsize=(9, 6))

plt.scatter(
    popularity_df["average_popularity"],
    popularity_df["observed_chart_days"]
)

plt.title("Popularity vs Playlist Longevity")

plt.xlabel("Average Popularity")

plt.ylabel("Observed Chart Days")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "popularity_vs_longevity.png"
)

plt.show()

# 18. Graph 4 - Popularity by Lifecycle Stage
stage_file = (
    BASE_DIR / "Stage_Results" /
    "daily_song_stages.csv"
)

if stage_file.exists():

    stage_df = pd.read_csv(stage_file)

    stage_df["date"] = pd.to_datetime(
        stage_df["date"], errors="coerce"
    )

    stage_df["song_key"] = (
        stage_df["song"].astype(str)
        .str.strip().str.casefold()
    )

    stage_df["artist_key"] = (
        stage_df["artist"].astype(str)
        .str.strip().str.casefold()
    )

    stage_df["popularity"] = pd.to_numeric(
        stage_df["popularity"], errors="coerce"
    )

    stage_summary = (
        stage_df.groupby("lifecycle_stage")
        ["popularity"].mean()
        .reindex([
            "New Entry",
            "Growth Phase",
            "Peak Phase",
            "Mature Phase",
            "Decline Phase"
        ])
    )

    print("\n========== POPULARITY BY LIFECYCLE STAGE ==========")

    print(stage_summary.round(2).to_string())

    stage_summary.to_csv(
        OUTPUT_DIR / "popularity_by_lifecycle_stage.csv"
    )

    plt.figure(figsize=(10, 6))

    stage_summary.plot(kind="bar", rot=25)

    plt.title("Average Popularity by Lifecycle Stage")

    plt.xlabel("Lifecycle Stage")

    plt.ylabel("Average Popularity")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "popularity_by_lifecycle_stage.png"
    )

    plt.show()

else:

    print("Lifecycle stage file not found.")

# 19. Final message
print("\n==========================================")
print("POPULARITY LIFECYCLE ANALYSIS COMPLETED!")
print("Check the Popularity_Results folder.")
print("==========================================")
