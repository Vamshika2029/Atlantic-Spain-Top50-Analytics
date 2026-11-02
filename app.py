
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Spain Top 50 | Atlantic Music Analytics",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 Spain Top 50 Playlist Analytics")
st.subheader("Content Maturity, Release Lifecycle & Playlist Rotation")
st.caption("Atlantic Recording Corporation | Music Analytics Project")

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    files = {
        "lifecycle": "Lifecycle_Results/song_lifecycle.csv",
        "stages": "Stage_Results/daily_song_stages.csv",
        "daily_churn": "Churn_Results/daily_churn_analysis.csv",
        "monthly_churn": "Churn_Results/monthly_churn_analysis.csv",
        "content": "Content_Results/content_song_analysis.csv",
        "popularity": "Popularity_Results/song_popularity_lifecycle.csv"
    }

    data = {}

    for key, file_path in files.items():
        full_path = BASE_DIR / file_path

        if not full_path.exists():
            st.error(f"Missing file: {file_path}")
            st.stop()

        data[key] = pd.read_csv(full_path)

    return data


data = load_data()

lifecycle = data["lifecycle"]
stages = data["stages"]
daily_churn = data["daily_churn"]
monthly_churn = data["monthly_churn"]
content = data["content"]
popularity = data["popularity"]

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Dashboard Navigation")

section = st.sidebar.radio(
    "Select Analysis",
    [
        "Overview",
        "Song Lifecycle",
        "Playlist Rotation",
        "Content Maturity",
        "Popularity Analysis"
    ]
)

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if section == "Overview":

    st.header("Project Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Unique Songs",
        f"{len(lifecycle):,}"
    )

    col2.metric(
        "Average Chart Days",
        f"{lifecycle['observed_chart_days'].mean():.1f}"
    )

    col3.metric(
        "Average Popularity",
        f"{popularity['average_popularity'].mean():.1f}"
    )

    col4.metric(
        "Average Retention",
        f"{daily_churn['retention_rate'].mean():.2f}%"
    )

    st.divider()

    st.subheader("Project Objectives")

    st.write("""
    This project analyzes the Spain Top 50 playlist to understand
    how songs enter, perform, mature and leave the playlist.

    The analysis focuses on:

    - Song lifecycle and chart longevity
    - Playlist entries, exits and retention
    - Explicit versus clean content
    - Singles versus album tracks
    - Popularity patterns across song lifecycles
    """)

    st.subheader("Top 10 Longest-Running Songs")

    top_songs = lifecycle.nlargest(
        10, "observed_chart_days"
    )

    fig = px.bar(
        top_songs.sort_values("observed_chart_days"),
        x="observed_chart_days",
        y="song",
        orientation="h",
        color="observed_chart_days",
        title="Top 10 Songs by Observed Chart Days",
        labels={
            "observed_chart_days": "Observed Chart Days",
            "song": "Song"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# SONG LIFECYCLE
# --------------------------------------------------

elif section == "Song Lifecycle":

    st.header("Song Lifecycle Analysis")

    st.write(
        "Explore how long songs remain on the Spain Top 50 playlist."
    )

    fig = px.histogram(
        lifecycle,
        x="observed_chart_days",
        nbins=30,
        title="Distribution of Song Chart Longevity",
        labels={"observed_chart_days": "Observed Chart Days"}
    )

    st.plotly_chart(fig, use_container_width=True)

    if "peak_position" in lifecycle.columns:

        fig2 = px.scatter(
            lifecycle,
            x="observed_chart_days",
            y="peak_position",
            hover_data=["song", "artist"],
            title="Chart Longevity vs Peak Position",
            labels={
                "observed_chart_days": "Observed Chart Days",
                "peak_position": "Best Chart Position"
            }
        )

        fig2.update_yaxes(autorange="reversed")
        st.plotly_chart(fig2, use_container_width=True)

    if "lifecycle_stage" in stages.columns:

        stage_counts = stages["lifecycle_stage"].value_counts().reset_index()
        stage_counts.columns = ["Lifecycle Stage", "Count"]

        fig3 = px.bar(
            stage_counts,
            x="Lifecycle Stage",
            y="Count",
            title="Song Lifecycle Stage Distribution",
            color="Lifecycle Stage"
        )

        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Song Lifecycle Data")
    st.dataframe(lifecycle, use_container_width=True)

# --------------------------------------------------
# PLAYLIST ROTATION
# --------------------------------------------------

elif section == "Playlist Rotation":

    st.header("Playlist Rotation Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average New Entries",
        f"{daily_churn['new_entries'].mean():.2f}"
    )

    col2.metric(
        "Average Exits",
        f"{daily_churn['exits'].mean():.2f}"
    )

    col3.metric(
        "Average Entry Churn",
        f"{daily_churn['entry_churn_rate'].mean():.2f}%"
    )

    st.subheader("Daily Playlist Entries and Exits")

    fig = px.line(
        daily_churn,
        x="date",
        y=["new_entries", "exits"],
        title="Daily Entries vs Exits"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Churn Rate")

    fig2 = px.line(
        monthly_churn,
        x="month",
        y="entry_churn_rate",
        markers=True,
        title="Monthly Playlist Churn Rate"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Monthly Retention")

    fig3 = px.line(
        monthly_churn,
        x="month",
        y="average_retention",
        markers=True,
        title="Average Monthly Retention Rate"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(monthly_churn, use_container_width=True)

# --------------------------------------------------
# CONTENT MATURITY
# --------------------------------------------------

elif section == "Content Maturity":

    st.header("Content Maturity Analysis")

    st.subheader("Explicit vs Clean Songs")

    explicit_summary = (
        content.groupby("content_type")
        .agg(
            total_songs=("song", "nunique"),
            average_popularity=("popularity", "mean"),
            average_chart_days=("observed_chart_days", "mean")
        )
        .reset_index()
    )

    fig = px.bar(
        explicit_summary,
        x="content_type",
        y="average_chart_days",
        color="content_type",
        title="Explicit vs Clean: Average Chart Longevity",
        labels={
            "content_type": "Content Type",
            "average_chart_days": "Average Chart Days"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(explicit_summary, use_container_width=True)

    st.subheader("Singles vs Albums")

    album_summary = (
        content.groupby("album_type")
        .agg(
            total_songs=("song", "nunique"),
            average_popularity=("popularity", "mean"),
            average_chart_days=("observed_chart_days", "mean")
        )
        .reset_index()
    )

    fig2 = px.bar(
        album_summary,
        x="album_type",
        y="average_chart_days",
        color="album_type",
        title="Singles vs Albums: Average Chart Longevity",
        labels={
            "album_type": "Release Type",
            "average_chart_days": "Average Chart Days"
        }
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(album_summary, use_container_width=True)

    st.subheader("Duration vs Chart Longevity")

    fig3 = px.scatter(
        content,
        x="duration_minutes",
        y="observed_chart_days",
        color="album_type",
        hover_data=["song", "artist"],
        title="Song Duration vs Chart Longevity"
    )

    st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------
# POPULARITY ANALYSIS
# --------------------------------------------------

elif section == "Popularity Analysis":

    st.header("Popularity Lifecycle Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "First Popularity",
        f"{popularity['first_popularity'].mean():.2f}"
    )

    col2.metric(
        "Last Popularity",
        f"{popularity['last_popularity'].mean():.2f}"
    )

    col3.metric(
        "Average Popularity Change",
        f"{popularity['popularity_change'].mean():+.2f}"
    )

    st.subheader("First vs Last Popularity")

    fig = px.scatter(
        popularity,
        x="first_popularity",
        y="last_popularity",
        hover_data=["song", "artist"],
        title="First Popularity vs Last Popularity"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Popularity Change Distribution")

    fig2 = px.histogram(
        popularity,
        x="popularity_change",
        nbins=30,
        title="Distribution of Popularity Change"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Popularity vs Chart Longevity")

    fig3 = px.scatter(
        popularity,
        x="average_popularity",
        y="observed_chart_days",
        hover_data=["song", "artist"],
        title="Average Popularity vs Observed Chart Days"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Popularity Data")
    st.dataframe(popularity, use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Atlantic Spain Top 50 Music Analytics Project | "
    "Data-driven playlist lifecycle and content maturity analysis"
)
