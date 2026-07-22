"""Streamlit demo UI for OSINT-Enricher."""
import streamlit as st
import pandas as pd
import pydeck as pdk
from pathlib import Path

st.set_page_config(page_title="OSINT Enricher Demo", layout="wide")
st.title("?? OSINT Enricher – Demo")

# Sidebar controls
st.sidebar.header("Data source")
data_dir = st.sidebar.text_input("Enriched data directory (Parquet)", "data/enriched")
if st.sidebar.button("Load data"):
    path = Path(data_dir)
    if not path.exists():
        st.error(f"Directory {path} does not exist")
    else:
        # Read all parquet files
        files = list(path.glob("*.parquet"))
        if not files:
            st.warning("No parquet files found")
        else:
            dfs = [pd.read_pe(f) for f in files]
            df = pd.concat(dfs, ignore_index=True)
            st.session_state["df"] = df
            st.success(f"Loaded {len(df)} records")

if "df" not in st.session_state:
    st.info("?? Load data from the sidebar")
else:
    df = st.session_state["df"]
    st.subheader("Recent events")
    st.dataframe(df.head(20))

    if {"latitude", "longitude"}.issubset(df.columns):
        st.subheader("Map view")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df.dropna(subset=["latitude", "longitude"]),
            get_position=["longitude", "latitude"],
            get_radius=1000,
            get_color=[200, 30, 0, 160],
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=df["latitude"].mean(),
            longitude=df["longitude"].mean(),
            zoom=4,
            pitch=0,
        )
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{text}"})
        st.pydeck_chart(r)
    else:
        st.warning("No geolocation data available for mapping.")

    # Sentiment distribution
    if "sentiment_label" in df.columns:
        st.subheader("Sentiment breakdown")
        st.bar_chart(df["sentiment_label"].value_counts())
