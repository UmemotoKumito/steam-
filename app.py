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
                selected_topic = event_bar2.selection.points[0]["x"]

        # --------------------------------------------------
        # 下段：レーダーチャートを配置（3カラムの中央を使って綺麗に配置）
        # --------------------------------------------------
        st.write("") 
        col_space1, col_radar, col_space2 = st.columns([1, 2, 1])

        # ▼ レーダーチャート：トピック別ポジティブ割合 ▼
        with col_radar:
            st.markdown("<h5 style='text-align: center;'>🎯 ③ トピック別 ポジティブ割合（満足度）</h5>", unsafe_allow_html=True)
            
            # CSVの「割合ぽじ」の文字列（例: "21%"）から "%" を削除して数値化
            scores = df_chart['割合ぽじ'].astype(str).str.replace('%', '').astype(float).tolist()
            categories_plot = df_chart['トピック'].tolist() + [df_chart['トピック'].iloc[0]]
            scores_plot = scores + [scores[0]]
            
            fig3 = go.Figure()
            fig3.add_trace(go.Scatterpolar(
                r=scores_plot, 
                theta=categories_plot, 
                fill='toself', 
                name='ポジティブ割合', 
                marker=dict(color='mediumpurple')
            ))
            fig3.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], angle=90),
                    angularaxis=dict(direction="clockwise", rotation=90)
                ),
                showlegend=False, 
                margin=dict(l=50, r=50, t=40, b=40),
                clickmode='event+select'
            )
            # クリックイベントの取得
            event_radar = st.plotly_chart(fig3, use_container_width=True, on_select="rerun", selection_mode="points")
            if not selected_topic and event_radar and event_radar.selection.points:
                if "theta" in event_radar.selection.points[0]:
                    selected_topic = event_radar.selection.points[0]["theta"]

    else:
        st.error("💡 グラフ表示用のCSVファイル（グラフ作成、全体入り.csv）が見つかりません。")

    st.divider()

    # --- トピック別 AI要約の表示 ---
    if df_report is None:
        st.error("⚠️ データファイル（output.csv）が見つかりません。")
    else:
        st.subheader("📑 トピック別 AI要約")
        st.write("確認したいトピックをクリックして詳細なAI要約を開いてください。")
        st.write("AI要約はワードクラウド＋高評価、低評価、総評の４点でまとめています")
        st.write("") 

        for index, row in df_report.iterrows():
            topic = row['topic']
            summary = row['summary']
            
            anchor_id = f"topic_{index}"
            st.markdown(f'<div id="{anchor_id}"></div>', unsafe_allow_html=True)
            
            is_expanded = (topic == selected_topic)
            with st.expander(f"📌 {topic}", expanded=is_expanded):
                
                # --- 画像表示部分 ---
                if topic in topic_images:
                    img_path = topic_images[topic]
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    else:
                        st.warning(f"⚠️ 画像ファイル '{img_path}' が見つかりません。")
                # -------------------------
                
                st.markdown(summary)
                
        st.divider()

        # クリックによる自動スクロール処理
        if selected_topic:
            target_index = df_report[df_report['topic'] == selected_topic].index
            if not target_index.empty:
                idx = target_index[0]
                scroll_js = f"""
                <script>
                    const element = window.parent.document.getElementById('topic_{idx}');
                    if (element) {{
                        element.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                    }}
                </script>
                """
                components.html(scroll_js, height=0, width=0)

else:
    st.title(f"🎮 {selected_game}")
    st.info("こちらのタイトルの分析データは現在準備中です。今後のアップデートをお待ちください！")
