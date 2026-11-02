
# ==================================================
# ATLANTIC RECORDING CORPORATION
# SPAIN TOP 50 - LIFECYCLE STAGE CLASSIFICATION
# ==================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Project directory
BASE_DIR = Path(__file__).parent

# 2. Create output directory
OUTPUT_DIR = BASE_DIR / "Stage_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# 3. Load dataset
df = pd.read_csv(BASE_DIR / "Atlantic_Spain.csv")

# 4. Convert dates
df["date"] = pd.to_datetime(
    df["date"],
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(subset=["date"])

# 5. Clean song and artist names
df["song_key"] = (
    df["song"].astype(str).str.strip().str.casefold()
)

df["artist_key"] = (
    df["artist"].astype(str).str.strip().str.casefold()
)

# 6. Convert position to numeric
df["position"] = pd.to_numeric(
    df["position"], errors="coerce"
)

df = df.dropna(
    subset=["position", "song_key", "artist_key"]
)

# 7. Remove conflicting duplicate positions
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

# 9. Sort song appearances
df = df.sort_values(
    ["song_key", "artist_key", "date"]
)

# 10. Calculate first appearance and days since entry
df["entry_date"] = df.groupby(
    ["song_key", "artist_key"]
)["date"].transform("min")

df["days_since_entry"] = (
    df["date"] - df["entry_date"]
).dt.days

# 11. Calculate previous seven observed appearance
# positions for each song

df["previous_7_avg_position"] = (
    df.groupby(["song_key", "artist_key"])["position"]
    .transform(
        lambda s: s.shift(1).rolling(
            window=7, min_periods=2
        ).mean()
    )
)

# 12. Define lifecycle classification function

def classify_stage(row):

    # New Entry: first seven calendar days
    if row["days_since_entry"] <= 7:
        return "New Entry"

    # Peak: position in Top 10
    elif row["position"] <= 10:
        return "Peak Phase"

    # If there is not enough previous data
    elif pd.isna(row["previous_7_avg_position"]):
        return "Mature Phase"

    # Growth: ranking improves by at least 3 places
    elif (
        row["previous_7_avg_position"] - row["position"]
        >= 3
    ):
        return "Growth Phase"

    # Decline: ranking worsens by at least 3 places
    elif (
        row["position"] - row["previous_7_avg_position"]
        >= 3
    ):
        return "Decline Phase"

    # Otherwise, stable ranking
    else:
        return "Mature Phase"


# 13. Apply lifecycle classification
df["lifecycle_stage"] = df.apply(
    classify_stage, axis=1
)

# 14. Save daily song-stage records
daily_output = OUTPUT_DIR / "daily_song_stages.csv"

df.to_csv(daily_output, index=False)

# 15. Count appearances in each stage
stage_counts = (
    df["lifecycle_stage"]
    .value_counts()
    .reindex([
        "New Entry",
        "Growth Phase",
        "Peak Phase",
        "Mature Phase",
        "Decline Phase"
    ], fill_value=0)
)

print("\n========== LIFECYCLE STAGE DISTRIBUTION ==========")

print(stage_counts)

# 16. Calculate percentage distribution
stage_percentage = (
    stage_counts / stage_counts.sum() * 100
).round(2)

print("\nStage Percentage:")
print(stage_percentage)

# 17. Find the last observed stage for every song
latest_stage = (
    df.sort_values("date")
    .groupby(["song_key", "artist_key"])
    .tail(1)
)

latest_stage_output = OUTPUT_DIR / "last_observed_song_stages.csv"

latest_stage.to_csv(
    latest_stage_output, index=False
)

print("\n========== LAST OBSERVED STAGE ==========")

print(
    latest_stage["lifecycle_stage"]
    .value_counts()
)

# 18. Save stage summary
summary = pd.DataFrame({
    "lifecycle_stage": stage_counts.index,
    "appearances": stage_counts.values,
    "percentage": stage_percentage.values
})

summary.to_csv(
    OUTPUT_DIR / "lifecycle_stage_summary.csv",
    index=False
)

# 19. Create lifecycle distribution graph
plt.figure(figsize=(10, 6))

stage_counts.plot(
    kind="bar",
    rot=25
)

plt.title("Spain Top 50 - Lifecycle Stage Distribution")
plt.xlabel("Lifecycle Stage")
plt.ylabel("Number of Song Appearances")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "lifecycle_stage_distribution.png"
)

plt.show()

print("\n==========================================")
print("LIFECYCLE STAGE CLASSIFICATION COMPLETED!")
print("Check the Stage_Results folder.")
print("==========================================")
