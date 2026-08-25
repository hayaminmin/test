import streamlit as st

st.set_page_config(page_title="アイデア整理アプリ", page_icon="💡")

st.title("💡 アイデア整理アプリ")
st.write("思いついたアイデアを、シンプルに形にしてみましょう。")

idea = st.text_input("作りたいもの・やりたいこと")
target = st.text_input("誰のため？")
problem = st.text_area("どんな困りごとを解決したい？")

if st.button("まとめる"):
    if idea:
        st.subheader("あなたのアイデア")
        st.success(f"{target or '利用する人'}のために、{problem or '困りごと'}を解決する『{idea}』")
        st.write("この内容をもとに、次は機能や画面を少しずつ追加できます。")
    else:
        st.warning("まず『作りたいもの・やりたいこと』を入力してください。")
