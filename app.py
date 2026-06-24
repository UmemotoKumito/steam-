import streamlit as st
import pandas as pd

# ページの基本設定
st.set_page_config(page_title="モンハンワイルズ レビュー分析レポート", layout="wide")

st.title("🎮 モンスターハンターワイルズ レビュー分析レポート")
st.write("レビューデータから抽出された、各トピックごとの最終分析レポートをまとめたダッシュボードです。")

# 1. データの読み込み
@st.cache_data
def load_data():
    try:
        # 新しいファイル名に変更しています
        return pd.read_csv("output.csv")
    except FileNotFoundError:
        return None

df = load_data()

# もしデータが見つからなかった場合のエラー表示
if df is None:
    st.error("⚠️ データファイル（output.csv）が見つかりません。GitHubにアップロードされているか確認してください。")
else:
    st.subheader("📑 トピック別 分析レポート")
    
    st.write("確認したいトピックをクリックして開いてください。")
    st.write("") # 少し隙間を空ける

    # 2. データをループして、トピックごとに折りたたみ（Expander）で表示
    for index, row in df.iterrows():
        topic = row['topic']
        summary = row['summary']
        
        # 📌 マークをつけてトピック名を見やすく表示
        with st.expander(f"📌 {topic}", expanded=False):
            # Markdown形式で改行などをそのまま綺麗に表示
            st.markdown(summary)
            
    st.divider() # ページの一番下に区切り線
