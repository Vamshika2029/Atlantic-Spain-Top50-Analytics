
# ==========================================
# ATLANTIC RECORDING CORPORATION
# SPAIN TOP 50 - EXPLORATORY DATA ANALYSIS
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Set project folder
BASE_DIR = Path(__file__).parent

# 2. Create output folders
OUTPUT_DIR = BASE_DIR / "EDA_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

# 3. Load dataset
df = pd.read_csv(BASE_DIR / "Atlantic_Spain.csv")

print("\n========== DATASET INFORMATION ==========")

# 4. Convert date into datetime format
df["date"] = pd.to_datetime(
    df["date"],
    format="%d-%m-%Y",
    errors="coerce"
)

# 5. Display basic information
print("\nDataset Shape:", df.shape)
print("\nColumn Names:")
print(df.columns.tolist())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

# 6. Check duplicate records
print("\nExact Duplicate Records:", df.duplicated().sum())

# 7. Check daily playlist entries
daily_count = df.groupby("date").size()

print("\nDaily Playlist Entry Summary:")
print(daily_count.describe())

# Find dates that do not have exactly 50 records
incorrect_dates = daily_count[daily_count != 50]

print("\nDates with incorrect entry counts:")
print(incorrect_dates)

# Save daily validation report
daily_count.rename("entry_count").to_csv(
    OUTPUT_DIR / "daily_entry_validation.csv"
)

# 8. Calculate song duration in minutes
df["duration_minutes"] = df["duration_ms"] / 60000

print("\n========== DESCRIPTIVE STATISTICS ==========")

print("\nPopularity Statistics:")
print(df["popularity"].describe())

print("\nSong Duration Statistics:")
print(df["duration_minutes"].describe())

print("\nAlbum Type Distribution:")
print(df["album_type"].value_counts())

print("\nExplicit Content Distribution:")
print(df["is_explicit"].value_counts())

# 9. Count unique songs and artists
print("\nUnique Songs:",
      df[["song", "artist"]].drop_duplicates().shape[0])

print("Unique Artists:", df["artist"].nunique())

# 10. Top 10 artists by playlist appearances
top_artists = df["artist"].value_counts().head(10)

print("\nTop 10 Artists:")
print(top_artists)

# 11. Save summary statistics
df.describe(include="all").to_csv(
    OUTPUT_DIR / "descriptive_statistics.csv"
)

# ==========================================
# VISUALIZATIONS
# ==========================================

# GRAPH 1: Album Type Distribution
plt.figure(figsize=(8, 5))
df["album_type"].value_counts().plot(
    kind="bar",
    rot=0
)
plt.title("Playlist Distribution by Album Type")
plt.xlabel("Album Type")
plt.ylabel("Number of Appearances")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "album_type.png")
plt.show()

# GRAPH 2: Explicit vs Clean Songs
plt.figure(figsize=(7, 5))
df["is_explicit"].value_counts().plot(
    kind="bar",
    rot=0
)
plt.title("Explicit vs Clean Songs")
plt.xlabel("Explicit Content")
plt.ylabel("Number of Appearances")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "explicit_content.png")
plt.show()

# GRAPH 3: Top 10 Artists
plt.figure(figsize=(10, 6))
top_artists.sort_values().plot(kind="barh")
plt.title("Top 10 Artists in Spain Top 50")
plt.xlabel("Playlist Appearances")
plt.ylabel("Artist")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top_artists.png")
plt.show()

# GRAPH 4: Song Duration Distribution
plt.figure(figsize=(8, 5))
plt.hist(df["duration_minutes"], bins=20)
plt.title("Distribution of Song Durations")
plt.xlabel("Duration (Minutes)")
plt.ylabel("Number of Appearances")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "song_duration.png")
plt.show()

# GRAPH 5: Daily Playlist Entries
plt.figure(figsize=(12, 5))
daily_count.plot()
plt.title("Daily Playlist Entry Count")
plt.xlabel("Date")
plt.ylabel("Number of Entries")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "daily_entries.png")
plt.show()

print("\n======================================")
print("EDA COMPLETED SUCCESSFULLY!")
print("Check the EDA_Results folder.")
print("======================================")
