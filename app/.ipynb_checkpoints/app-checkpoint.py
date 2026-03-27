import streamlit as st
import pandas as pd

df = pd.read_csv("../data/sample_student_data.csv")

st.title("📚 AI Learning Assistant Dashboard")

st.subheader("📊 Performance Overview")
st.bar_chart(df.groupby("subject")["score"].mean())

weak = df.groupby("subject")["score"].mean().idxmin()

st.subheader("⚠️ Weakest Subject")
st.write(weak)

st.subheader("🤖 AI Recommendation")
st.write(f"You should focus more on {weak}")