import streamlit as st

st.set_page_config(page_title="食育だよりメーカー", page_icon="🍚", layout="centered")

st.title("🍚 児童向け 食育だよりメーカー")
st.caption("給食をきっかけに、子どもの『なぜ？』と家庭での食体験につなげる食育だよりを作ります。")

# --------------------
# 1. 基本設定
# --------------------
st.subheader("① だよりの基本設定")
grade = st.selectbox("対象学年", ["低学年", "中学年", "高学年"])
viewpoint = st.selectbox(
    "食育の視点",
    ["栄養", "旬・季節", "食文化", "地域・地産地消", "食品ロス", "調理の科学", "食べ方・味わい方"],
)
menu = st.text_input("給食の献立・料理名", "さつまいもごはん、みそ汁、焼き魚")

st.markdown("#### 💡 献立から食育テーマを3案")

question_words = {
    "低学年": "どうしてかな？",
    "中学年": "どんな工夫があると思う？",
    "高学年": "どんな理由や背景があると思う？",
}

if menu:
    ideas = [
        f"『{menu}』を、{viewpoint}の視点から見てみよう。いつもの給食にどんなひみつがある？",
        f"今日の『{menu}』は、食べる前と食べた後で印象が変わるかな？ {question_words[grade]}",
        f"給食室では『{menu}』をおいしく届けるために何を工夫している？ 家庭の料理との違いも考えてみよう。",
    ]
    for i, idea in enumerate(ideas, 1):
        st.write(f"**案{i}：** {idea}")

st.divider()

# --------------------
# 2. 本文
# --------------------
st.subheader("② 児童に届けたい内容")
title = st.text_input("だよりのタイトル", "今日の給食、どこがすごい？")
theme = st.text_input("今号のテーマ", f"{viewpoint}から給食を見てみよう")
question = st.text_input("児童への問いかけ", ideas[0] if menu else "今日の給食にはどんなひみつがある？")
teacher_voice = st.text_area(
    "栄養教諭からのひとこと",
    "給食は、栄養をとるだけの時間ではありません。食材、季節、地域、調理の工夫に気づくと、毎日の給食が少し違って見えてきます。",
)

st.divider()

# --------------------
# 3. レシピ
# --------------------
st.subheader("③ 給食レシピ")
recipe_name = st.text_input("紹介する料理名", "さつまいもごはん")
original_servings = st.number_input("元のレシピの人数", min_value=1, value=1, step=1)

st.caption("材料は『材料名, 数量, 単位』の形で1行ずつ入力してください。例：さつまいも, 80, g")
ingredients_text = st.text_area(
    "材料",
    "米, 75, g\nさつまいも, 50, g\n塩, 0.5, g",
)

steps = st.text_area(
    "作り方",
    "1. 米を洗う。\n2. さつまいもを食べやすい大きさに切る。\n3. 米、さつまいも、調味料を入れて炊く。",
)
recipe_point = st.text_input("給食らしく仕上げるコツ", "さつまいもを大きめに切ると、形と食感が残ります。")

# 4人分換算
converted_lines = []
for line in ingredients_text.splitlines():
    parts = [p.strip() for p in line.split(",")]
    if len(parts) == 3:
        name, amount, unit = parts
        try:
            new_amount = float(amount) * 4 / original_servings
            if new_amount.is_integer():
                new_amount = int(new_amount)
            converted_lines.append(f"{name}　{new_amount}{unit}")
        except ValueError:
            converted_lines.append(line)
    elif line.strip():
        converted_lines.append(line)

st.markdown("#### 🏠 家庭用4人分にすると")
for line in converted_lines:
    st.write(line)

st.divider()

# --------------------
# 4. 家庭につなぐ
# --------------------
st.subheader("④ おうちでTRY")
home_try = st.text_input("家庭でやってみてほしいこと", "今日の給食で気づいたことを、家の人に1つ話してみよう。")

# 学年別の言葉の雰囲気
closing = {
    "低学年": "きょうのきゅうしょくで、ひとつ『へえ！』を見つけてみよう。",
    "中学年": "いつもの給食の中にある工夫や理由を、自分の言葉で見つけてみよう。",
    "高学年": "食べものの背景まで考えると、毎日の選び方や食べ方が変わってきます。",
}[grade]

# --------------------
# 5. 完成版
# --------------------
if st.button("✨ A4食育だより原稿を作る", use_container_width=True):
    st.divider()
    st.header(f"🥢 {title}")
    st.caption(f"対象：{grade}　｜　視点：{viewpoint}")

    st.markdown(f"## 今日のテーマ：{theme}")
    st.info(f"💭 **みんなに質問！**\n\n{question}")

    st.markdown("### 👩‍🍳 給食室から")
    st.write(teacher_voice)

    st.markdown(f"### 🍳 おうちで作ってみよう！ 給食レシピ『{recipe_name}』")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**材料（4人分）**")
        for line in converted_lines:
            st.write(line)
    with col2:
        st.markdown("**作り方**")
        st.write(steps)

    st.success(f"⭐ **給食のコツ**：{recipe_point}")

    st.markdown("### 🏠 おうちでTRY")
    st.write(home_try)

    st.markdown("### 🌱 今日のひとこと")
    st.write(closing)

    st.divider()
    st.caption("知る → 食べる → 話す → 家でやってみる")

    plain_text = f"""{title}

対象：{grade}
視点：{viewpoint}

■ 今日のテーマ
{theme}

■ みんなに質問！
{question}

■ 給食室から
{teacher_voice}

■ 給食レシピ「{recipe_name}」
材料（4人分）
{chr(10).join(converted_lines)}

作り方
{steps}

給食のコツ
{recipe_point}

■ おうちでTRY
{home_try}

■ 今日のひとこと
{closing}
"""

    st.download_button(
        "📄 完成原稿をテキストで保存",
        data=plain_text,
        file_name="食育だより原稿.txt",
        mime="text/plain",
        use_container_width=True,
    )
