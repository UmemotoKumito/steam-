import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ページの基本設定（タイトルや横幅を広くする設定）
st.set_page_config(page_title="モンハンワイルズ レビュー分析", layout="wide")

st.title("🎮 モンスターハンターワイルズ レビュー分析")
st.write("ColabのAI（Qwen）が要約・抽出したレビューデータを視覚化したダッシュボードです。")

# 1. データの読み込み
# st.cache_dataをつけることで、毎回読み込まずに動作をサクサクにします
@st.cache_data
def load_data():
    try:
        # Colabで出力したCSVファイルと同じ名前を指定します
        return pd.read_csv("mh_wilds_structured_summary.csv")
    except FileNotFoundError:
        return None

df = load_data()

# もしデータが見つからなかった場合のエラー表示
if df is None:
    st.error("⚠️ データファイル（mh_wilds_structured_summary.csv）が見つかりません。GitHubにアップロードされているか確認してください。")
else:
    # 2. レーダーチャートの作成
    st.subheader("📊 5項目の言及数とおすすめ評価の比較")
    
    categories = ['音楽', 'システム', 'ゲーム性', '映像', '登場人物']
    total_counts = []
    recommended_counts = []

    for cat in categories:
        mentioned = df[df[cat].astype(str) != 'なし']
        total_counts.append(len(mentioned))

        rec_count = len(mentioned[(mentioned['voted_up'] == True) | (mentioned['voted_up'] == 'True')])
        recommended_counts.append(rec_count)

    categories_plot = categories + [categories[0]]
    total_counts_plot = total_counts + [total_counts[0]]
    recommended_counts_plot = recommended_counts + [recommended_counts[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=total_counts_plot, theta=categories_plot, fill='toself', name='言及された総数', marker=dict(color='lightskyblue')
    ))
    fig.add_trace(go.Scatterpolar(
        r=recommended_counts_plot, theta=categories_plot, fill='toself', name='おすすめ評価', marker=dict(color='coral')
    ))

    max_val = max(total_counts) if total_counts else 10
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max_val + (max_val * 0.1)])),
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    # グラフを画面に表示
    st.plotly_chart(fig, use_container_width=True)

    st.divider() # 区切り線

    # 3. 項目別トップ3レビューの表示
    st.subheader("🌟 項目別：最も参考になったレビュー Top 3")

    for cat in categories:
        st.markdown(f"#### 【 {cat} 】に関する注目のレビュー")

        mentioned = df[df[cat].astype(str) != 'なし'].copy()
        mentioned['votes_up'] = pd.to_numeric(mentioned['votes_up'], errors='coerce').fillna(0)
        top3 = mentioned.sort_values('votes_up', ascending=False).head(3)

        if len(top3) == 0:
            st.info("この項目に関するレビューは見つかりませんでした。")
            continue

        # トップ3を折りたたみ形式（expander）ですっきり表示
        for i, (_, row) in enumerate(top3.iterrows(), 1):
            votes = int(row['votes_up'])
            is_recommended = row['voted_up'] == True or str(row['voted_up']).lower() == 'true'
            eval_str = "👍 おすすめ" if is_recommended else "👎 おすすめしない"

            summary = str(row[cat])
            full_text = str(row['review']).strip()

            # クリックで開閉できる箱を作ります
            with st.expander(f"{i}位 ｜ 役に立った: {votes}人 ｜ 評価: {eval_str}"):
                st.markdown(f"**🤖 AI要約:** {summary}")
                st.markdown(f"**💬 レビュー全文:** \n{full_text}")

        st.write("") # 少し隙間を空ける
