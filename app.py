import streamlit as st

st.set_page_config(page_title="食育だよりメーカー", page_icon="🍚", layout="centered")

st.title("🍚 児童向け 食育だよりメーカー")
st.caption("給食をきっかけに、子どもの『なぜ？』と家庭での食体験につなげる食育だよりを作ります。")

st.subheader("① 今月のテーマ")
title = st.text_input("だよりのタイトル", "給食から見つける 食べもののひみつ")
theme = st.text_input("伝えたいテーマ", "旬の食べもの")
question = st.text_input("児童への問いかけ", "今日の給食の中で、今がいちばんおいしい食べものはどれでしょう？")

st.subheader("② あなたらしい一言")
teacher_voice = st.text_area(
    "栄養教諭として伝えたいこと",
    "給食は、おなかをいっぱいにするだけではありません。季節や地域、人の工夫を見つけながら食べてみてください。",
)

st.subheader("③ 給食レシピ")
recipe_name = st.text_input("料理名", "給食の○○")
ingredients = st.text_area(
    "材料（家庭用）",
    "例）\n材料A　100g\n材料B　1個\n調味料　適量",
)
steps = st.text_area(
    "作り方",
    "例）\n1. 材料を切る\n2. 加熱する\n3. 味をととのえる",
)
recipe_point = st.text_input("給食らしく仕上げるコツ", "給食では、食材の食感が残るように加熱しています。")

st.subheader("④ おうちでTRY")
home_try = st.text_input("家庭でやってみてほしいこと", "旬の食べものを1つ見つけて、家の人に教えてみよう。")

if st.button("✨ 食育だよりを作る", use_container_width=True):
    st.divider()
    st.header(f"🥢 {title}")
    st.markdown(f"### 今月のテーマ：{theme}")

    st.info(f"💭 **みんなに質問！**\n\n{question}")

    st.markdown("### 👩‍🍳 給食室から伝えたいこと")
    st.write(teacher_voice)

    st.markdown(f"### 🍳 おうちで作ってみよう！ 給食レシピ『{recipe_name}』")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**材料**")
        st.write(ingredients)
    with col2:
        st.markdown("**作り方**")
        st.write(steps)

    st.success(f"⭐ **給食のコツ**：{recipe_point}")

    st.markdown("### 🏠 おうちでTRY")
    st.write(home_try)

    st.divider()
    st.caption("『知る → 食べる → 話す → 家でやってみる』につながる食育だより")
