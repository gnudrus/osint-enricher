"""Streamlit demo UI for OSINT Enricher."""

from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="OSINT Enricher Demo", layout="wide")
st.title("OSINT Enricher — Demo")

st.sidebar.header("Data source")
data_dir = st.sidebar.text_input("Enriched data directory (Parquet)", "data/enriched")
if st.sidebar.button("Load data"):
    path = Path(data_dir)
    if not path.is_dir():
        st.error(f"Directory {path} does not exist")
    else:
        files = list(path.glob("*.parquet"))
        if not files:
            st.warning("No Parquet files found")
        else:
            st.session_state["df"] = pd.concat(
                [pd.read_parquet(file) for file in files], ignore_index=True
            )
            st.success(f"Loaded {len(st.session_state['df'])} records")

if "df" not in st.session_state:
    st.info("Load data from the sidebar")
else:
    df = st.session_state["df"]
    st.subheader("Recent events")
    st.dataframe(df.head(20))

    if {"latitude", "longitude"}.issubset(df.columns):
        mapped = df.dropna(subset=["latitude", "longitude"])
        if not mapped.empty:
            st.subheader("Map view")
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=mapped,
                get_position=["longitude", "latitude"],
                get_radius=1000,
                get_color=[200, 30, 0, 160],
                pickable=True,
            )
            view_state = pdk.ViewState(
                latitude=float(mapped["latitude"].mean()),
                longitude=float(mapped["longitude"].mean()),
                zoom=4,
            )
            st.pydeck_chart(
                pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{text}"})
            )
    else:
        st.warning("No geolocation data available for mapping")

    if "sentiment_label" in df.columns:
        st.subheader("Sentiment breakdown")
        st.bar_chart(df["sentiment_label"].value_counts())
