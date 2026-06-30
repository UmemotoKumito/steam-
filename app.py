import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ページの基本設定
st.set_page_config(page_title="モンハンワイルズ レビュー分析レポート", layout="wide")

st.title("🎮 モンスターハンターワイルズ レビュー分析レポート")
st.write("レビューデータから抽出された、各トピックごとの最終分析レポートと評価傾向をまとめたダッシュボードです。")

# --- 1. データの読み込み ---
@st.cache_data
def load_data():
    # 総評レポート (output.csv) の読み込み
    try:
        df_report = pd.read_csv("output.csv")
    except FileNotFoundError:
        df_report = None
        
    # 生のレビューデータ (mh_wilds_structured_summary.csv) の読み込み
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

    # output.csv に合わせた6つのカテゴリと、分類用のキーワードを定義
    categories = ['コンテンツ・更新', '表現・演出', '難易度・進行', '動作環境', '戦闘・アクション', 'システム・操作']
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
    
    # 欠損値を空文字に変換し、voted_upを文字列の小文字に統一して判定しやすくする
    df['review'] = df['review'].fillna('')
    df['voted_up'] = df['voted_up'].astype(str).str.lower()
    
    for cat in categories:
        kws = keywords[cat]
        pattern = '|'.join(kws)
        
        # キーワードのいずれかを含むレビュー行を抽出
        mentioned = df[df['review'].str.contains(pattern, na=False)]
        
        # そのカテゴリへの言及総数と、その中でのおすすめ（True）の数をカウント
        total = len(mentioned)
        rec = len(mentioned[mentioned['voted_up'] == 'true'])
        
        total_counts.append(total)
        recommended_counts.append(rec)
            
    return categories, total_counts, recommended_counts

categories, total_counts, recommended_counts = get_radar_data(df_reviews)

# --- 3. 分析結果の可視化（レーダーチャートを横並びで表示） ---
st.subheader("📊 分析結果の可視化")

if sum(total_counts) > 0:
    col1, col2 = st.columns(2)

    # グラフの線を繋ぐために、末尾に最初の要素を追加
    categories_plot = categories + [categories[0]]
    total_counts_plot = total_counts + [total_counts[0]]
    recommended_counts_plot = recommended_counts + [recommended_counts[0]]

    # ▼ 左側のカラム：言及数とおすすめ評価の比較 ▼
    with col1:
        st.markdown("##### 📈 6項目の言及数とおすすめ評価の比較")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatterpolar(
            r=total_counts_plot, theta=categories_plot, fill='toself', name='言及された総数', marker=dict(color='lightskyblue')
        ))
        fig1.add_trace(go.Scatterpolar(
            r=recommended_counts_plot, theta=categories_plot, fill='toself', name='おすすめ評価', marker=dict(color='coral')
        ))

        max_val = max(total_counts) if total_counts else 10
        fig1.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max_val + (max_val * 0.1)])),
            showlegend=True,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ▼ 右側のカラム：総評スコア（50点満点） ▼
    with col2:
        st.markdown("##### 🎯 トピック別 総評スコア（50点満点）")
        
        scores = []
        for tot, rec in zip(total_counts, recommended_counts):
            if tot > 0:
                scores.append(round((rec / tot) * 50, 1))
            else:
                scores.append(0)
                
        scores_plot = scores + [scores[0]]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatterpolar(
            r=scores_plot, theta=categories_plot, fill='toself', name='満足度スコア', marker=dict(color='mediumpurple')
        ))
        
        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 50])),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("💡 レーダーチャートを表示するには、データが正しく読み込まれているか確認してください。")

st.divider() # 区切り線

# --- 4. トピック別 分析レポート（総評）の表示 ---
if df_report is None:
    st.error("⚠️ データファイル（output.csv）が見つかりません。GitHubにアップロードされているか確認してください。")
else:
    st.subheader("📑 トピック別 分析レポート（総評）")
    
    st.write("確認したいトピックをクリックして詳細な総評レポートを開いてください。")
    st.write("") # 少し隙間を空ける

    for index, row in df_report.iterrows():
        topic = row['topic']
        summary = row['summary']
        
        with st.expander(f"📌 {topic}", expanded=False):
            st.markdown(summary)
            
    st.divider() # ページの一番下に区切り線
