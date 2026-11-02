
# ==================================================
# ATLANTIC RECORDING CORPORATION
# SPAIN TOP 50 - CONTENT MATURITY ANALYSIS
# ==================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Project directory
BASE_DIR = Path(__file__).parent

# 2. Create output folder
OUTPUT_DIR = BASE_DIR / "Content_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# 3. Load dataset
df = pd.read_csv(BASE_DIR / "Atlantic_Spain.csv")

# 4. Convert date and numeric columns
df["date"] = pd.to_datetime(
    df["date"], dayfirst=True, errors="coerce"
)

df["position"] = pd.to_numeric(
    df["position"], errors="coerce"
)

df["duration_ms"] = pd.to_numeric(
    df["duration_ms"], errors="coerce"
)

df["total_tracks"] = pd.to_numeric(
    df["total_tracks"], errors="coerce"
)

df = df.dropna(
    subset=["date", "position", "song", "artist"]
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

# 7. Keep one appearance per song per date
df = df.drop_duplicates(
    subset=["date", "song_key", "artist_key"],
    keep="first"
)

# 8. Convert song duration into minutes
df["duration_minutes"] = (
    df["duration_ms"] / 60000
)

# 9. Normalize explicit content values
def normalize_explicit(value):

    value = str(value).strip().lower()

    if value in ["true", "1", "yes", "explicit"]:
        return "Explicit"

    elif value in ["false", "0", "no", "clean"]:
        return "Clean"

    else:
        return "Unknown"


df["content_type"] = df["is_explicit"].apply(
    normalize_explicit
)

# 10. Normalize album type
df["album_type"] = (
    df["album_type"]
    .astype(str)
    .str.strip()
    .str.title()
)

# 11. Create song-level lifecycle and attribute data

def first_valid(series):

    values = series.dropna()

    if len(values) == 0:
        return None

    return values.iloc[0]


song_data = (
    df.groupby(["song_key", "artist_key"])
    .agg(
        song=("song", "first"),

        artist=("artist", "first"),

        entry_date=("date", "min"),

        exit_date=("date", "max"),

        observed_chart_days=("date", "nunique"),

        peak_position=("position", "min"),

        popularity=("popularity", "mean"),

        duration_minutes=("duration_minutes", "mean"),

        album_type=("album_type", first_valid),

        total_tracks=("total_tracks", first_valid),

        content_type=("content_type", first_valid)
    )
    .reset_index()
)

# 12. Calculate calendar span
song_data["calendar_span_days"] = (
    song_data["exit_date"] -
    song_data["entry_date"]
).dt.days + 1

# 13. Save complete song-level data
song_data.to_csv(
    OUTPUT_DIR / "content_song_analysis.csv",
    index=False
)

# ==================================================
# ANALYSIS 1: EXPLICIT VS CLEAN
# ==================================================

valid_content = song_data[
    song_data["content_type"].isin(["Explicit", "Clean"])
]

explicit_summary = (
    valid_content.groupby("content_type")
    .agg(
        unique_songs=("song", "count"),

        average_observed_days=(
            "observed_chart_days", "mean"
        ),

        average_calendar_span=(
            "calendar_span_days", "mean"
        ),

        average_peak_position=(
            "peak_position", "mean"
        ),

        average_popularity=("popularity", "mean")
    )
    .round(2)
)

print("\n========== EXPLICIT VS CLEAN ==========")

print(explicit_summary.to_string())

explicit_summary.to_csv(
    OUTPUT_DIR / "explicit_vs_clean.csv"
)

# ==================================================
# ANALYSIS 2: SINGLE VS ALBUM
# ==================================================

valid_album = song_data[
    song_data["album_type"].isin(["Single", "Album"])
]

album_summary = (
    valid_album.groupby("album_type")
    .agg(
        unique_songs=("song", "count"),

        average_observed_days=(
            "observed_chart_days", "mean"
        ),

        average_calendar_span=(
            "calendar_span_days", "mean"
        ),

        average_peak_position=(
            "peak_position", "mean"
        ),

        average_popularity=("popularity", "mean")
    )
    .round(2)
)

print("\n========== SINGLE VS ALBUM ==========")

print(album_summary.to_string())

album_summary.to_csv(
    OUTPUT_DIR / "single_vs_album.csv"
)

# ==================================================
# ANALYSIS 3: SONG DURATION VS RETENTION
# ==================================================

duration_data = song_data.dropna(
    subset=["duration_minutes", "observed_chart_days"]
)

duration_correlation = duration_data[
    ["duration_minutes", "observed_chart_days"]
].corr().iloc[0, 1]

print("\n========== SONG DURATION ANALYSIS ==========")

print(
    "Correlation between duration and observed days:",
    round(duration_correlation, 3)
)

# ==================================================
# ANALYSIS 4: ALBUM SIZE VS RETENTION
# ==================================================

album_size_data = song_data.dropna(
    subset=["total_tracks", "observed_chart_days"]
)

album_size_correlation = album_size_data[
    ["total_tracks", "observed_chart_days"]
].corr().iloc[0, 1]

print("\n========== ALBUM SIZE ANALYSIS ==========")

print(
    "Correlation between album size and observed days:",
    round(album_size_correlation, 3)
)

# Save correlation results
correlation_summary = pd.DataFrame({
    "comparison": [
        "Song Duration vs Observed Chart Days",
        "Album Size vs Observed Chart Days"
    ],

    "correlation": [
        duration_correlation,
        album_size_correlation
    ]
})

correlation_summary.to_csv(
    OUTPUT_DIR / "correlation_analysis.csv",
    index=False
)

# ==================================================
# VISUALIZATION 1: EXPLICIT VS CLEAN
# ==================================================

plt.figure(figsize=(8, 5))

explicit_summary["average_observed_days"].plot(
    kind="bar", rot=0
)

plt.title("Explicit vs Clean Song Longevity")
plt.xlabel("Content Type")
plt.ylabel("Average Observed Chart Days")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "explicit_vs_clean.png"
)

plt.show()

# ==================================================
# VISUALIZATION 2: SINGLE VS ALBUM
# ==================================================

plt.figure(figsize=(8, 5))

album_summary["average_observed_days"].plot(
    kind="bar", rot=0
)

plt.title("Single vs Album Track Longevity")
plt.xlabel("Album Type")
plt.ylabel("Average Observed Chart Days")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "single_vs_album.png"
)

plt.show()

# ==================================================
# VISUALIZATION 3: SONG DURATION VS RETENTION
# ==================================================

plt.figure(figsize=(9, 5))

plt.scatter(
    duration_data["duration_minutes"],
    duration_data["observed_chart_days"]
)

plt.title("Song Duration vs Playlist Longevity")
plt.xlabel("Song Duration (Minutes)")
plt.ylabel("Observed Chart Days")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "duration_vs_retention.png"
)

plt.show()

# ==================================================
# VISUALIZATION 4: ALBUM SIZE VS RETENTION
# ==================================================

plt.figure(figsize=(9, 5))

plt.scatter(
    album_size_data["total_tracks"],
    album_size_data["observed_chart_days"]
)

plt.title("Album Size vs Song Longevity")
plt.xlabel("Total Tracks in Album")
plt.ylabel("Observed Chart Days")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "album_size_vs_retention.png"
)

plt.show()

# ==================================================
# FINAL OUTPUT
# ==================================================

print("\n==========================================")
print("CONTENT MATURITY ANALYSIS COMPLETED!")
print("Check the Content_Results folder.")
print("==========================================")
