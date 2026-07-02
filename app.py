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
    "--- ほかのゲーム（準備中） ---" 
]
selected_game = st.sidebar.selectbox("タイトル選択", game_list)

st.sidebar.divider()
st.sidebar.caption("※「ほかのゲーム」のデータセットを追加することで、このダッシュボードを拡張できます。")

# ==========================================
# 📌 データの読み込みと集計関数
# ==========================================
@st.cache_data
def load_data(report_file, review_file):
    try:
        df_report = pd.read_csv(report_file)
    except FileNotFoundError:
        df_report = None
        
    try:
        df_reviews = pd.read_csv(review_file)
    except FileNotFoundError:
        df_reviews = None

    return df_report, df_reviews

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
        '動作環境': ['動作', '環境', 'クラッシュ', '落ちる', '重い', 'グラボ', '最適化', 'バグ', 'エラー'],
        '戦闘・アクション': ['戦闘', 'アクション', 'ジャストガード', '武器', '相殺', '回避', '集中モード'],
        'システム・操作': ['システム', '操作', 'UI', 'もっさり', 'ショートカット', 'カメラ', 'キャラクリ']
    }
    
    total_counts = []
    recommended_counts = []
    
    df['review'] = df['review'].fillna('')
    df['voted_up'] = df['voted_up'].astype(str).str.lower()
    
    for cat in categories:
        kws = keywords[cat]
        pattern = '|'.join(kws)
        
        mentioned = df[df['review'].str.contains(pattern, na=False)]
        
        total = len(mentioned)
        rec = len(mentioned[mentioned['voted_up'] == 'true'])
        
        total_counts.append(total)
        recommended_counts.append(rec)
            
    return categories, total_counts, recommended_counts

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
# 📌 メイン画面の表示（選択されたゲームごとに分岐）
# ==========================================

if selected_game == "モンスターハンターワイルズ":
    # ----------------------------------------
    # モンスターハンターワイルズのページ
    # ----------------------------------------
    st.title("🎮 モンスターハンターワイルズ レビュー分析レポート")
    st.write("レビューデータから抽出された、各トピックごとのAI要約と評価傾向をまとめたダッシュボードです。")
    st.info("💡 **Tips:** グラフの棒（バー）や点（ポイント）をクリックすると、画面下部の該当するAI要約が開き、そこまで自動でスクロールします。")

    # ワイルズ用のデータを読み込み
    df_report, df_reviews = load_data("output.csv", "mh_wilds_structured_summary.csv")
    categories, total_counts, recommended_counts = get_radar_data(df_reviews)

    st.subheader("📊 分析結果の可視化")
    selected_topic = None

    if sum(total_counts) > 0:
        col1, col2 = st.columns(2)

        # ▼ 左側のカラム：積み上げ棒グラフ ▼
        with col1:
            st.markdown("##### 📈 6項目の言及数とおすすめ評価の比較")
            not_recommended_counts = [t - r for t, r in zip(total_counts, recommended_counts)]
            
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=categories, y=recommended_counts, name='おすすめ評価', marker_color='coral'))
            fig1.add_trace(go.Bar(x=categories, y=not_recommended_counts, name='おすすめ以外', marker_color='lightskyblue'))
            
            fig1.update_layout(
                barmode='stack', showlegend=True, margin=dict(l=40, r=40, t=40, b=40),
                clickmode='event+select'
            )
            
            event_bar = st.plotly_chart(fig1, use_container_width=True, on_select="rerun", selection_mode="points")
            if event_bar and event_bar.selection.points:
                selected_topic = event_bar.selection.points[0]["x"]

        # ▼ 右側のカラム：レーダーチャート ▼
        with col2:
            st.markdown("##### 🎯 トピック別 総評スコア（100点満点）")
            scores = [round((rec / tot) * 100, 1) if tot > 0 else 0 for tot, rec in zip(total_counts, recommended_counts)]
                    
            categories_plot = categories + [categories[0]]
            scores_plot = scores + [scores[0]]
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatterpolar(r=scores_plot, theta=categories_plot, fill='toself', name='満足度スコア', marker=dict(color='mediumpurple')))
            
            fig2.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], angle=90),
                    angularaxis=dict(direction="clockwise", rotation=90)
                ),
                showlegend=False, margin=dict(l=40, r=40, t=40, b=40),
                clickmode='event+select'
            )
            
            event_radar = st.plotly_chart(fig2, use_container_width=True, on_select="rerun", selection_mode="points")
            if not selected_topic and event_radar and event_radar.selection.points:
                if "theta" in event_radar.selection.points[0]:
                    selected_topic = event_radar.selection.points[0]["theta"]

        # ▼ 追加：感情分析（100%積み上げ横棒グラフ） ▼
        st.markdown("##### 💬 トピック別 感情分析 (Sentiment Analysis)")
        
        # ※実際のCSVに感情データがないため、画像の見た目を再現するダミーデータを使用しています。
        # 今後実際のデータを用意できた場合は、この部分をCSVからの読み込みに差し替えてください。
        sentiment_data = pd.DataFrame({
            'トピック': categories,
            'Positive': [18, 25, 40, 10,  5, 45],
            'Neutral':  [72, 60, 40, 45, 15, 40],
            'Negative': [10, 15, 20, 45, 80, 15]
        })

        fig3 = go.Figure()
        # ポジティブ（緑）
        fig3.add_trace(go.Bar(
            y=sentiment_data['トピック'], x=sentiment_data['Positive'],
            name='Positive', orientation='h', marker=dict(color='#4CAF50')
        ))
        # ニュートラル（グレー）
        fig3.add_trace(go.Bar(
            y=sentiment_data['トピック'], x=sentiment_data['Neutral'],
            name='Neutral', orientation='h', marker=dict(color='#BDBDBD')
        ))
        # ネガティブ（赤）
        fig3.add_trace(go.Bar(
            y=sentiment_data['トピック'], x=sentiment_data['Negative'],
            name='Negative', orientation='h', marker=dict(color='#F44336')
        ))

        fig3.update_layout(
            barmode='stack',
            yaxis=dict(autorange="reversed"), # 項目を上から順に並べるための設定
            margin=dict(l=40, r=40, t=40, b=40),
            height=350, # グラフの高さをお好みで調整
            clickmode='event+select'
        )
        
        # 感情分析グラフのクリック連動
        event_sentiment = st.plotly_chart(fig3, use_container_width=True, on_select="rerun", selection_mode="points")
        if not selected_topic and event_sentiment and event_sentiment.selection.points:
             if "y" in event_sentiment.selection.points[0]:
                 selected_topic = event_sentiment.selection.points[0]["y"]

    else:
        st.info("💡 グラフを表示するには、データが正しく読み込まれているか確認してください。")

    st.divider()

    # --- トピック別 AI要約の表示 ---
    if df_report is None:
        st.error("⚠️ データファイル（output.csv）が見つかりません。")
    else:
        st.subheader("📑 トピック別 AI要約")
        st.write("確認したいトピックをクリックして詳細なAI要約を開いてください。")
        st.write("AI要約は高評価、低評価、総評の３点でまとめています")
