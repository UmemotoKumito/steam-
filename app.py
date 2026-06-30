import streamlit as st
import streamlit.components.v1 as components  # JavaScriptを実行するために追加
import pandas as pd
import plotly.graph_objects as go

# ページの基本設定
st.set_page_config(page_title="モンハンワイルズ レビュー分析レポート", layout="wide")

st.title("🎮 モンスターハンターワイルズ レビュー分析レポート")
st.write("レビューデータから抽出された、各トピックごとのAI要約と評価傾向をまとめたダッシュボードです。")
st.info("💡 **Tips:** グラフの棒（バー）や点（ポイント）をクリックすると、画面下部の該当するAI要約が開き、そこまで自動でスクロールします。")

# --- 1. データの読み込み ---
@st.cache_data
def load_data():
    try:
        df_report = pd.read_csv("output.csv")
    except FileNotFoundError:
        df_report = None
        
    try:
        df_reviews = pd.read_csv("mh_wilds_structured_summary.csv")
    except FileNotFoundError:
        df_reviews = None

    return df_report, df_reviews

df_report, df_reviews = load_data()

# --- 2. レビューデータから6つの項目の集計 ---
@st.cache_data
def get_radar_data(df):
    if df is None:
        return [], [], []

    # グラフに表示する順番を指定された順序に変更
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
        '動作環境': ['動作', '環境', 'クラッシュ', '落ちる', '重い', 'グラボ', '最適化', 'バグ', 'エラー'],
        '戦闘・アクション': ['戦闘', 'アクション', 'ジャストガード', '武器', '相殺', '回避', '集中モード'],
        'システム・操作': ['システム', '操作', 'UI', 'もっさり', 'ショートカット', 'カメラ', 'キャラクリ']
    }
    
    total_counts = []
    recommended_counts = []
    
    df['review'] = df['review'].fillna('')
    df['voted_up'] = df['voted_up'].astype(str).str.lower()
    
    # categoriesの順番に従って集計されるため、グラフにもこの順番が反映されます
    for cat in categories:
        kws = keywords[cat]
        pattern = '|'.join(kws)
        
        mentioned = df[df['review'].str.contains(pattern, na=False)]
        
        total = len(mentioned)
        rec = len(mentioned[mentioned['voted_up'] == 'true'])
        
        total_counts.append(total)
        recommended_counts.append(rec)
            
    return categories, total_counts, recommended_counts

categories, total_counts, recommended_counts = get_radar_data(df_reviews)

# --- 3. 分析結果の可視化 ---
st.subheader("📊 分析結果の可視化")

# クリックされたトピックを保存する変数
selected_topic = None

if sum(total_counts) > 0:
    col1, col2 = st.columns(2)

    # ▼ 左側のカラム：言及数とおすすめ評価の比較（積み上げ棒グラフ） ▼
    with col1:
        st.markdown("##### 📈 6項目の言及数とおすすめ評価の比較")
        
        not_recommended_counts =
