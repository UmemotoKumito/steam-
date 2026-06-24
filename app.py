import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ページの基本設定
st.set_page_config(page_title="モンハンワイルズ 分析レポート", layout="wide")

st.title("🎮 モンスターハンターワイルズ 分析レポート")
st.write("抽出されたトピック別の分析データを視覚化したダッシュボードです。")

# 1. データの読み込み
@st.cache_data
def load_data():
    try:
        # 先ほどのCSVファイルを読み込む
        return pd.read_csv("output.csv")
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("⚠️ データファイル（output.csv）が見つかりません。同じフォルダにあるか確認してください。")
else:
    # --- データの前処理 ---
    # CSVにはテキスト（topic, summary）しか無いため、レーダーチャート用にダミーの評価スコアを追加します。
    # ※実際の分析でスコアデータがある場合は、その列を読み込むように変更してください。
    if len(df) == 6:
        # トピック: 難易度・進行, コンテンツ・更新, 戦闘・アクション, システム・操作, 動作環境, 表現・演出
        df['score'] = [3.5, 3.0, 4.2, 2.5, 1.5, 4.0] 
    else:
        # 万が一行数が違う場合のためのフォールバック
        df['score'] = [3.0] * len(df)

    # 2. レーダーチャートの作成 (Plotly)
    st.subheader("📊 トピック別 評価レーダーチャート（ダミーデータ）")

    categories = df['topic'].tolist()
    scores = df['score'].tolist()

    # レーダーチャートの線を繋いで閉じるために、最初の要素を最後にも追加
    categories_plot = categories + [categories[0]]
    scores_plot = scores + [scores[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores_plot, 
        theta=categories_plot, 
        fill='toself', 
        name='評価スコア', 
        marker=dict(color='lightskyblue')
    ))

    # グラフのレイアウト調整（0〜5の範囲に設定）
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    # グラフを画面に表示
    st.plotly_chart(fig, use_container_width=True)

    st.divider() # 区切り線

    # 3. 項目別 分析要約レポートの表示
    st.subheader("📝 項目別 分析レポート")
    st.write("各トピックの分析結果をクリックして展開できます。")

    # データフレームの行ごとにループして表示
    for index, row in df.iterrows():
        topic_name = row['topic']
        summary_text = str(row['summary']).replace('\\n', '\n') # 改行文字を実際の改行に変換

        # クリックで開閉できる箱（expander）を作成
        with st.expander(f"📂 【 {topic_name} 】 に関する分析レポート"):
            st.markdown(summary_text)
