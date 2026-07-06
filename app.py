"""TrafficVision - Streamlit canlı istatistik dashboard'u.

Çalıştırma: streamlit run dashboard/app.py
"""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "trafficvision.db"

st.set_page_config(page_title="TrafficVision Dashboard", page_icon="🚦", layout="wide")
st.title("🚦 TrafficVision — Trafik Analiz Paneli")


def load_data() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame(columns=["id", "timestamp", "vehicle_class", "speed_kmh"])
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM counts", conn)
    conn.close()
    if not df.empty:
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
        df["hour"] = df["datetime"].dt.hour
    return df


df = load_data()

if df.empty:
    st.info("Henüz veri yok. Önce `python src/main.py --source <video>` ile analiz çalıştırın.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Araç", len(df))
    col2.metric("Ortalama Hız (km/h)", f"{df['speed_kmh'].mean():.1f}")
    col3.metric("Maks. Hız (km/h)", f"{df['speed_kmh'].max():.1f}")

    st.subheader("Saatlik Yoğunluk")
    hourly = df.groupby("hour").size().reset_index(name="count")
    fig1 = px.bar(hourly, x="hour", y="count", labels={"hour": "Saat", "count": "Araç Sayısı"})
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Hız Dağılımı")
    fig2 = px.histogram(df, x="speed_kmh", nbins=20, labels={"speed_kmh": "Hız (km/h)"})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Ham Veri")
    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
