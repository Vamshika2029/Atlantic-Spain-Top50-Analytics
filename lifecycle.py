
# ============================================
# ATLANTIC RECORDING CORPORATION
# SPAIN TOP 50 - SONG LIFECYCLE ANALYSIS
# ============================================

import pandas as pd
from pathlib import Path

# 1. Project folder
BASE_DIR = Path(__file__).parent

# 2. Output folder
OUTPUT_DIR = BASE_DIR / "Lifecycle_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# 3. Load original dataset
df = pd.read_csv(BASE_DIR / "Atlantic_Spain.csv")

print("\n========== SONG LIFECYCLE ANALYSIS ==========")

# 4. Convert date column
df["date"] = pd.to_datetime(
    df["date"],
    dayfirst=True,
    errors="coerce"
)

# Remove rows with invalid dates
df = df.dropna(subset=["date"])

# 5. Clean song and artist names for matching
df["song_key"] = (
    df["song"].astype(str).str.strip().str.casefold()
)

df["artist_key"] = (
    df["artist"].astype(str).str.strip().str.casefold()
)

# 6. Convert position into numeric values
df["position"] = pd.to_numeric(
    df["position"], errors="coerce"
)

df = df.dropna(
    subset=["position", "song_key", "artist_key"]
)

# 7. Sort records by date and position
df = df.sort_values(["date", "position"])

# Keep only the first occurrence of each
# playlist position on each date

df = df.drop_duplicates(
    subset=["date", "position"],
    keep="first"
)


# 8. Group records by song and artist
lifecycle_records = []

for (song_key, artist_key), group in df.groupby(
    ["song_key", "artist_key"]
):

    group = group.sort_values("date")

    # First and last appearance
    entry_date = group["date"].min()
    exit_date = group["date"].max()

    # Best ranking (smaller number means better rank)
    peak_position = group["position"].min()

    # First date when the song achieved its best rank
    peak_date = group.loc[
        group["position"] == peak_position, "date"
    ].min()

    # Calculate lifecycle measurements
    calendar_span = (
        (exit_date - entry_date).days + 1
    )

    observed_days = group["date"].nunique()

    gap_days = calendar_span - observed_days

    time_to_peak = (
        peak_date - entry_date
    ).days

    average_position = group["position"].mean()

    # Store results
    lifecycle_records.append({

        "song": group["song"].iloc[0],

        "artist": group["artist"].iloc[0],

        "entry_date": entry_date,

        "exit_date": exit_date,

        "calendar_span_days": calendar_span,

        "observed_chart_days": observed_days,

        "gap_days": gap_days,

        "peak_position": peak_position,

        "peak_date": peak_date,

        "time_to_peak_days": time_to_peak,

        "average_position": round(
            average_position, 2
        )
    })

# 9. Create lifecycle DataFrame
lifecycle_df = pd.DataFrame(lifecycle_records)

# 10. Sort by observed chart days
lifecycle_df = lifecycle_df.sort_values(
    "observed_chart_days",
    ascending=False
)

# 11. Display results
print("\nTotal Unique Song-Artist Combinations:",
      len(lifecycle_df))

print("\nAverage Calendar Span:",
      round(lifecycle_df["calendar_span_days"].mean(), 2))

print("\nAverage Observed Chart Days:",
      round(lifecycle_df["observed_chart_days"].mean(), 2))

print("\nAverage Time to Peak:",
      round(lifecycle_df["time_to_peak_days"].mean(), 2))

print("\nAverage Peak Position:",
      round(lifecycle_df["peak_position"].mean(), 2))

# 12. Display top 10 longest observed lifecycles
print("\n========== TOP 10 SONGS BY OBSERVED DAYS ==========")

print(
    lifecycle_df[
        ["song", "artist", "observed_chart_days",
         "peak_position", "time_to_peak_days"]
    ].head(10).to_string(index=False)
)

# 13. Save lifecycle results
output_file = OUTPUT_DIR / "song_lifecycle.csv"

lifecycle_df.to_csv(output_file, index=False)

print("\nLifecycle results saved successfully!")
print("File location:", output_file)

print("\n========== ANALYSIS COMPLETED ==========")
