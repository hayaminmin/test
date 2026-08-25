import json
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI食育だよりメーカー", page_icon="🍚", layout="centered")

st.title("🍚 AI食育だよりメーカー")
st.caption("給食を教材にして、児童が『なぜ？』と思える食育だよりをAIと一緒に作ります。")

# --------------------
# APIキー
# --------------------
try:
    saved_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    saved_key = ""

with st.sidebar:
    st.header("AI設定")
    api_key = saved_key or st.text_input("OpenAI APIキー", type="password")
    st.caption("公開するときはStreamlitのSecretsに保存するのがおすすめです。GitHubにはAPIキーを書きません。")


def get_client():
    if not api_key:
        st.error("OpenAI APIキーを設定してください。")
        st.stop()
    return OpenAI(api_key=api_key)


def ask_ai(prompt):
    client = get_client()
    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
    )
    return response.output_text.strip()


# --------------------
# 1. 給食からテーマを発掘
# --------------------
st.subheader("① 給食から食育テーマを発掘")

grade = st.selectbox("対象学年", ["低学年", "中学年", "高学年"])
viewpoint = st.multiselect(
    "使いたい視点（複数選択可）",
    ["栄養", "旬・季節", "食文化", "地域・地産地消", "食品ロス", "調理の科学", "食べ方・味わい方", "給食室の工夫"],
    default=["調理の科学", "給食室の工夫"],
)
menu = st.text_area(
    "今日・今月取り上げたい給食の献立",
    "麦ごはん、牛乳、さばの塩焼き、切干大根の煮物、みそ汁",
)
real_point = st.text_area(
    "あなたの学校・給食室ならではの情報",
    placeholder="例：切干大根は煮崩れないよう、調味料を入れる順番を工夫している／地元産の○○を使っている など",
)

if "ideas" not in st.session_state:
    st.session_state.ideas = []

if st.button("✨ AIに食育テーマを3案考えてもらう", use_container_width=True):
    prompt = f"""
あなたは、学校給食を教材に変えることが得意な栄養教諭の編集パートナーです。
次の献立から、児童向け食育だよりに使える『ありきたりではない食育テーマ』を3案考えてください。

対象：{grade}
献立：{menu}
重視する視点：{', '.join(viewpoint) if viewpoint else '特に指定なし'}
学校・給食室ならではの情報：{real_point or '特になし'}

条件：
- 『○○には栄養があります』『好き嫌いせず食べましょう』だけの一般論にしない。
- 児童が実際の給食を見たり、食べたりしながら確かめたくなる切り口にする。
- 栄養、調理科学、食文化、保存の知恵、地域、給食室の工夫などを必要に応じて組み合わせる。
- 対象学年に合う言葉にする。
- 栄養素・歴史・健康効果など、確信のない事実を作らない。
- 3案は互いに違う方向性にする。

次のJSONだけを返してください。説明文やMarkdownは不要です。
[
  {{"title":"短く印象的なテーマ名","hook":"児童への問いかけ","angle":"このテーマで何を伝えるかを80字程度"}},
  {{"title":"短く印象的なテーマ名","hook":"児童への問いかけ","angle":"このテーマで何を伝えるかを80字程度"}},
  {{"title":"短く印象的なテーマ名","hook":"児童への問いかけ","angle":"このテーマで何を伝えるかを80字程度"}}
]
"""
    try:
        result = ask_ai(prompt)
        st.session_state.ideas = json.loads(result)
    except Exception as e:
        st.error(f"AIの呼び出しに失敗しました：{e}")

if st.session_state.ideas:
    labels = [f"{i+1}. {idea['title']} — {idea['hook']}" for i, idea in enumerate(st.session_state.ideas)]
    selected_label = st.radio("使いたいテーマを選んでください", labels)
    selected_index = labels.index(selected_label)
    selected = st.session_state.ideas[selected_index]
    st.info(f"**ねらい**：{selected['angle']}")
else:
    selected = None

st.divider()

# --------------------
# 2. AIで本文を作る
# --------------------
st.subheader("② AIで児童向け本文を作る")
teacher_voice = st.text_area(
    "必ず入れたいあなた自身の言葉・経験",
    placeholder="例：給食時間に児童から『切干大根って大根なの？』と聞かれたことがあります。そこから…",
)
length = st.select_slider("本文の長さ", options=["短め", "標準", "しっかり"], value="標準")

if "article" not in st.session_state:
    st.session_state.article = ""

if st.button("✍️ 選んだテーマから本文を作る", use_container_width=True):
    if not selected:
        st.warning("先にAIでテーマを3案作り、1つ選んでください。")
    else:
        prompt = f"""
あなたは小学校の栄養教諭と一緒に食育だよりを作る編集者です。
次の条件で、児童が給食を食べながら『確かめてみたい』と思える食育だより本文を書いてください。

対象：{grade}
献立：{menu}
テーマ：{selected['title']}
問いかけ：{selected['hook']}
テーマのねらい：{selected['angle']}
学校・給食室ならではの情報：{real_point or '特になし'}
栄養教諭本人の言葉・経験：{teacher_voice or '特になし'}
文章量：{length}

条件：
- 先生が児童に話しかけるような自然な日本語。
- 説教調にしない。
- 『栄養があるから食べよう』だけで終わらない。
- 最初の1〜2文で児童の興味を引く。
- 実際の給食を観察したり味わったりできるポイントを1つ入れる。
- 学校・給食室ならではの情報がある場合は、それを中心に据える。
- 事実を勝手に作らない。入力にない固有の産地・数値・歴史的事実は断定しない。
- 最後は短い問いかけで終える。
- 見出しは不要。本文だけを返す。
"""
        try:
            st.session_state.article = ask_ai(prompt)
        except Exception as e:
            st.error(f"AIの呼び出しに失敗しました：{e}")

if st.session_state.article:
    article = st.text_area("AIが作った本文（ここで自由に直せます）", st.session_state.article, height=240)
else:
    article = ""

st.divider()

# --------------------
# 3. 給食レシピ
# --------------------
st.subheader("③ 給食レシピを家庭向けに")
recipe_name = st.text_input("紹介する料理名", "切干大根の煮物")
original_servings = st.number_input("元のレシピの人数", min_value=1, value=1, step=1)
st.caption("材料は『材料名, 数量, 単位』の形で1行ずつ入力してください。例：切干大根, 12, g")
ingredients_text = st.text_area(
    "材料",
    "切干大根, 12, g\nにんじん, 10, g\n油揚げ, 8, g",
)
steps = st.text_area(
    "給食での作り方・調理手順",
    "1. 切干大根を水で戻す。\n2. 材料を食べやすい大きさに切る。\n3. 煮汁で煮て味を含ませる。",
)
recipe_point = st.text_area(
    "給食ならではのコツ・家庭に伝えたいこと",
    placeholder="例：大量調理では仕上がり時間から逆算して、食感が残るように加熱しています。",
)

converted_lines = []
for line in ingredients_text.splitlines():
    parts = [p.strip() for p in line.split(",")]
    if len(parts) == 3:
        name, amount, unit = parts
        try:
            new_amount = float(amount) * 4 / original_servings
            if new_amount.is_integer():
                new_amount = int(new_amount)
            else:
                new_amount = round(new_amount, 1)
            converted_lines.append(f"{name}　{new_amount}{unit}")
        except ValueError:
            converted_lines.append(line)
    elif line.strip():
        converted_lines.append(line)

st.markdown("#### 🏠 家庭用4人分")
for line in converted_lines:
    st.write(line)

if "recipe_text" not in st.session_state:
    st.session_state.recipe_text = ""

if st.button("🍳 AIに家庭向けレシピ文へ整えてもらう", use_container_width=True):
    prompt = f"""
学校給食のレシピを、家庭で4人分作りやすい形に整えてください。

料理名：{recipe_name}
材料（4人分）：
{chr(10).join(converted_lines)}

給食での作り方：
{steps}

給食ならではのコツ：
{recipe_point or '特になし'}

条件：
- 入力されていない材料や分量を勝手に追加しない。
- 家庭で分かりやすい手順にする。
- 給食と家庭で調理条件が違う場合は、断定せず『家庭では〜すると作りやすい』と提案する。
- 材料、作り方、給食のプロのひとこと、の3項目で簡潔にまとめる。
"""
    try:
        st.session_state.recipe_text = ask_ai(prompt)
    except Exception as e:
        st.error(f"AIの呼び出しに失敗しました：{e}")

if st.session_state.recipe_text:
    recipe_text = st.text_area("AIが整えた家庭向けレシピ（自由に修正できます）", st.session_state.recipe_text, height=260)
else:
    recipe_text = ""

st.divider()

# --------------------
# 4. 家庭につなぐ
# --------------------
st.subheader("④ 家庭につなぐ")
home_try = st.text_input("おうちでTRY", "今日の給食で見つけた『へえ！』を、家の人に1つ話してみよう。")

# --------------------
# 5. 完成原稿
# --------------------
st.subheader("⑤ 完成原稿")
newsletter_title = st.text_input("食育だよりのタイトル", selected['title'] if selected else "給食から見つける 食べもののひみつ")

if st.button("📄 A4食育だより原稿をまとめる", use_container_width=True):
    if not article:
        st.warning("本文を作成してからまとめてください。")
    else:
        st.header(f"🥢 {newsletter_title}")
        if selected:
            st.info(f"💭 **みんなに質問！**\n\n{selected['hook']}")
        st.write(article)

        if recipe_text:
            st.markdown(f"### 🍳 おうちで作ってみよう！『{recipe_name}』")
            st.write(recipe_text)

        st.markdown("### 🏠 おうちでTRY")
        st.write(home_try)

        plain_text = f"""{newsletter_title}

{selected['hook'] if selected else ''}

{article}

【おうちで作ってみよう！ {recipe_name}】
{recipe_text}

【おうちでTRY】
{home_try}
"""
        st.download_button(
            "完成原稿をテキストで保存",
            data=plain_text,
            file_name="食育だより原稿.txt",
            mime="text/plain",
            use_container_width=True,
        )

st.caption("AIの提案は下書きです。学校名、産地、栄養価、アレルギー情報などは必ず実際の資料で確認してから使用してください。")
