import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import os

# ページの基本設定
st.set_page_config(page_title="ゲームレビュー分析レポート", layout="wide")

# ==========================================
# 📌 サイドバー（ナビゲーション）の設定
# ==========================================
st.sidebar.title("🎮 ナビゲーション")
st.sidebar.write("分析したいタイトルを選択してください。")

# 今後ゲームを追加する場合は、このリストにタイトル名を書き足します
game_list = [
    "モンスターハンターワイルズ",
    "--- ほかのゲーム（準備中） ---" # 後から追加するためのプレースホルダー
]
selected_game = st.sidebar.selectbox("タイトル選択", game_list)

st.sidebar.divider()
st.sidebar.caption("※「ほかのゲーム」のデータセットを追加することで、このダッシュボードを拡張できます。")

# ==========================================
# 📌 データの読み込みと集計関数
# ==========================================
@st.cache_data
def load_data(report_file, review_file, chart_csv_file):
    try:
        df_report = pd.read_csv(report_file)
    except FileNotFoundError:
        df_report = None
        
    try:
        df_reviews = pd.read_csv(review_file)
    except FileNotFoundError:
        df_reviews = None
        
    try:
        df_chart = pd.read_csv(chart_csv_file)
        if 'Unnamed: 0' in df_chart.columns:
            df_chart.rename(columns={'Unnamed: 0': 'トピック'}, inplace=True)
    except FileNotFoundError:
        df_chart = None

    return df_report, df_reviews, df_chart

@st.cache_data
def get_radar_data(df):
    if df is None:
        return [], [], []

    categories = [
        '難易度・進行',
        'コンテンツ・更新',
        '戦闘・アクション',
        'システム・操作',
        '動作環境',
        '表現・演出'
    ]
    
    keywords = {
        'コンテンツ・更新': ['コンテンツ', 'アプデ', 'アップデート', '追加', 'ボリューム', 'モンスター', 'DLC'],
        '表現・演出': ['表現', '演出', 'グラフィック', 'グラ', 'BGM', '音楽', '映像', 'マップ', '世界観'],
        '難易度・進行': ['難易度', '進行', 'ストーリー', '鎧玉', '簡単', '難しい', '周回', '作業'],
        '動作環境': ['動作', '環境
