import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ページの基本設定
st.set_page_config(page_title="モンハンワイルズ レビュー分析レポート", layout="wide")

st.title("🎮 モンスターハンターワイルズ レビュー分析レポート")
st.write("レビューデータから抽出された、各トピックごとの最終分析レポートと評価傾向をまとめたダッシュボードです。")

# --- 1. 総評レポート用データの読み込み ---
@st.cache_data
def load_report_data():
    try:
        return pd.read_csv("output.csv")
    except FileNotFoundError:
        return None

df_report = load_report_data()

# --- 2. 6つの項目（CSV）データの読み込みと集計 ---
@st.cache_data
def load_radar_data():
    # 6つのファイル名（トピック名）を定義
    categories = ['コンテンツ・更新', '表現・演出', '難易度・進行', '動作環境', '戦闘・アクション', 'システム・操作']
    total_counts = []
    recommended_counts = []
    
    for cat in categories:
        try:
            # 各カテゴリのCSVファイルを読み込む
            df = pd.read_csv(f"{cat}.csv")
            
            # 全体の言及数（行数）
            total = len(df)
            
            # おすすめ評価（voted_upがTrue）の数
            # ※文字列の'True'として保存されている場合も考慮
            rec = len(df[(df['voted_up'] == True) | (df['voted_up'] == 'True')])
            
            total_counts.append(total)
            recommended_counts.append(rec)
        except FileNotFoundError:
            # ファイルが見つからない場合は0として扱う
            total_counts.append(0)
            recommended_counts.append(0)
            
    return categories, total_counts, recommended_counts

categories, total_counts, recommended_counts = load_radar_data()

# --- 3. 分析結果の可視化（レーダーチャートを横並びで表示） ---
st.subheader("📊 分析結果の可視化")

# ファイルが1つでも読み込めていればグラフを描画する
if sum(total_counts) > 0:
    # 画面を左右に分割する (col1が左、col2が右)
    col1, col2 = st.columns(2)

    # グラフの線を繋ぐために、末尾に最初の要素を追加
    categories_plot = categories + [categories[0]]
    total_counts_plot = total_counts + [total_counts[0]]
    recommended_counts_plot = recommended_counts + [recommended_counts[0]]

    # ▼ 左側のカラム：言及数とおすすめ評価の比較 ▼
    with col1:
        st.markdown("##### 📈 6項目の言及数とおすすめ評価の比較")
        fig1 = go.Figure()
        # 言及された総数
        fig1.add_trace(go.Scatterpolar(
            r=total_counts_plot, theta=categories_plot, fill='toself', name='言及された総数', marker=dict(color='lightskyblue')
        ))
        # おすすめ評価
        fig1.add_trace(go.Scatterpolar(
            r=recommended_counts_plot, theta=categories_plot, fill='toself', name='おすすめ評価', marker=dict(color='coral')
        ))

        # グラフの最大値を自動調整
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
        
        # 各項目の「おすすめ率」を計算し、50点満点に換算する
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
        
        # 50点満点なので、最大値を50に固定する
        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 50])),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    # ファイルが見つからない場合の案内
    st.info("💡 レーダーチャートを表示するには、6つのCSVファイル（『コンテンツ・更新.csv』など）をGitHubにアップロードしてください。")

st.divider() # 区切り線

# --- 4. トピック別 分析レポート（総評）の表示 ---
if df_report is None:
    st.error("⚠️ データファイル（output.csv）が見つかりません。GitHubにアップロードされているか確認してください。")
else:
    st.subheader("📑 トピック別 分析レポート（総評）")
    
    st.write("確認したいトピックをクリックして詳細な総評レポートを開いてください。")
    st.write("") # 少し隙間を空ける

    # データをループして、トピックごとに折りたたみ（Expander）で表示
    for index, row in df_report.iterrows():
        topic = row['topic']
        summary = row['summary']
        
        # 📌 マークをつけてトピック名を見やすく表示
        with st.expander(f"📌 {topic}", expanded=False):
            # Markdown形式で改行などをそのまま綺麗に表示
            st.markdown(summary)
            
    st.divider() # ページの一番下に区切り線
