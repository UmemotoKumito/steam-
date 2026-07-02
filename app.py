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

game_list = [
    "モンスターハンターワイルズ",
    "--- ほかのゲーム（準備中） ---"
]
selected_game = st.sidebar.selectbox("タイトル選択", game_list)

st.sidebar.divider()
st.sidebar.caption("※「ほかのゲーム」のデータセットを追加することで、このダッシュボードを拡張できます。")

# ==========================================
# 📌 データの読み込み関数
# ==========================================
@st.cache_data
def load_data():
    # ① AI要約レポートデータ（既存）の読み込み
    try:
        df_report = pd.read_csv("output.csv")
    except FileNotFoundError:
        df_report = None
        
    # ② 新しく追加されたグラフ用データの読み込み
    try:
        df_chart = pd.read_csv("グラフ作成、全体入り.csv")
        # 最初の列（Unnamed: 0）を「トピック」という名前に変更して扱いやすくする
        df_chart.rename(columns={df_chart.columns[0]: 'トピック'}, inplace=True)
    except FileNotFoundError:
        df_chart = None

    return df_report, df_chart

# トピック名と画像ファイル名の紐づけ
topic_images = {
    '難易度・進行': '難易度.png',
    'コンテンツ・更新': 'コンテンツ.png',
    '戦闘・アクション': '戦闘.png',
    'システム・操作': 'システム.png',
    '動作環境': '動作環境.png',
    '表現・演出': '表現.png'
}

# ==========================================
# 📌 メイン画面の表示
# ==========================================

if selected_game == "モンスターハンターワイルズ":
    st.title("🎮 モンスターハンターワイルズ レビュー分析レポート")
    st.write("レビューデータから抽出された、各トピックごとのAI要約と評価傾向をまとめたダッシュボードです。")
    st.info("💡 **Tips:** どのグラフの棒（バー）や点（ポイント）をクリックしても、画面下部の該当するAI要約が開き、そこまで自動でスクロールします。")

    # データを読み込み
    df_report, df_chart = load_data()

    st.subheader("📊 分析結果の可視化")
    selected_topic = None

    if df_chart is not None:
        # --------------------------------------------------
        # 上段：2つの棒グラフを横並びに配置
        # --------------------------------------------------
        col1, col2 = st.columns(2)

        # ▼ 棒グラフ①：トピック別の総言及数（合計） ▼
        with col1:
            st.markdown("##### 📊 ① トピック別の総言及数（合計）")
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=df_chart['トピック'],
                y=df_chart['合計'],
                text=df_chart['合計'],
                textposition='outside',
                marker_color='royalblue',
                name='総言及数'
            ))
            fig1.update_layout(
                margin=dict(l=40, r=40, t=40, b=40),
                clickmode='event+select',
                yaxis=dict(title='言及数（件）')
            )
            # クリックイベントの取得
            event_bar1 = st.plotly_chart(fig1, use_container_width=True, on_select="rerun", selection_mode="points")
            if event_bar1 and event_bar1.selection.points:
                selected_topic = event_bar1.selection.points[0]["x"]

        # ▼ 棒グラフ②：トピック別の評価割合（100%積み上げ） ▼
        with col2:
            st.markdown("##### 📈 ② トピック別の評価内訳（100%積み上げ）")
            fig2 = go.Figure()
            
            # Positive（ポジティブ）
            fig2.add_trace(go.Bar(
                x=df_chart['トピック'], 
                y=df_chart['positive'], 
                name='Positive', 
                marker_color='#4CAF50',
                text=df_chart['割合ぽじ'], 
                textposition='inside'
            ))
            # Neutral（中立）※CSV内の列名「nuetral」に合わせています
            fig2.add_trace(go.Bar(
                x=df_chart['トピック'], 
                y=df_chart['nuetral'], 
                name='Neutral', 
                marker_color='#FFC107',
                text=df_chart['割合なちゅ'], 
                textposition='inside'
            ))
            # Negative（ネガティブ）
            fig2.add_trace(go.Bar(
                x=df_chart['トピック'], 
                y=df_chart['negative'], 
                name='Negative', 
                marker_color='#EF5350',
                text=df_chart['割合ねが'], 
                textposition='inside'
            ))
            fig2.update_layout(
                barmode='stack',       # 積み上げ
                barnorm='percent',     # 100%基準に引き伸ばす
                showlegend=True, 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=40, r=40, t=40, b=40),
                clickmode='event+select'
            )
            # クリックイベントの取得
            event_bar2 = st.plotly_chart(fig2, use_container_width=True, on_select="rerun", selection_mode="points")
            if not selected_topic and event_bar2 and event_bar2.selection.points:
                selected_topic = event_
