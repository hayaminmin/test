import json
from io import BytesIO
from xml.sax.saxutils import escape

import streamlit as st
from google import genai
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

st.set_page_config(page_title="AI食育だよりメーカー", page_icon="🍚", layout="centered")
st.title("🍚 AI食育だよりメーカー")
st.caption("給食を教材にして、児童が『なぜ？』と思える食育だよりをAIと一緒に作ります。")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("StreamlitのSecretsに GEMINI_API_KEY を設定してください。")
    st.stop()

client = genai.Client(api_key=api_key)

GEMINI_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]


def ask_ai(prompt):
    last_error = None
    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            if response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            error_text = str(e)
            if any(code in error_text for code in ["429", "500", "502", "503", "504", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]):
                continue
            raise
    raise RuntimeError("Geminiが一時的に混み合っています。少し時間をおいて、もう一度お試しください。") from last_error


pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))


def pdf_paragraph_text(text):
    return escape(text or "").replace("\n", "<br/>")


def create_pdf(title, hook, article, recipe_name, recipe_text, home_try):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
    )

    title_style = ParagraphStyle(
        "TitleJP", fontName="HeiseiKakuGo-W5", fontSize=18, leading=25,
        alignment=TA_CENTER, spaceAfter=10 * mm, wordWrap="CJK"
    )
    heading_style = ParagraphStyle(
        "HeadingJP", fontName="HeiseiKakuGo-W5", fontSize=12, leading=18,
        spaceBefore=5 * mm, spaceAfter=2 * mm, wordWrap="CJK"
    )
    body_style = ParagraphStyle(
        "BodyJP", fontName="HeiseiMin-W3", fontSize=10.5, leading=18,
        spaceAfter=4 * mm, wordWrap="CJK"
    )
    question_style = ParagraphStyle(
        "QuestionJP", fontName="HeiseiKakuGo-W5", fontSize=11, leading=18,
        leftIndent=4 * mm, rightIndent=4 * mm, spaceAfter=5 * mm, wordWrap="CJK"
    )

    story = [Paragraph(pdf_paragraph_text(title), title_style)]
    if hook:
        story.append(Paragraph("みんなに質問！", heading_style))
        story.append(Paragraph(pdf_paragraph_text(hook), question_style))
    story.append(Paragraph(pdf_paragraph_text(article), body_style))

    if recipe_text:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(pdf_paragraph_text(f"おうちで作ってみよう！『{recipe_name}』"), heading_style))
        story.append(Paragraph(pdf_paragraph_text(recipe_text), body_style))

    if home_try:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("おうちでTRY", heading_style))
        story.append(Paragraph(pdf_paragraph_text(home_try), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


st.subheader("① 給食から食育テーマを発掘")
grade = st.selectbox("対象学年", ["低学年", "中学年", "高学年"])
viewpoint = st.multiselect(
    "使いたい視点（複数選択可）",
    ["栄養", "旬・季節", "食文化", "地域・地産地消", "食品ロス", "調理の科学", "食べ方・味わい方", "給食室の工夫"],
    default=["調理の科学", "給食室の工夫"],
)
menu = st.text_area("今日・今月取り上げたい給食の献立", "麦ごはん、牛乳、さばの塩焼き、切干大根の煮物、みそ汁")
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
- 一般論だけにしない。
- 児童が給食を見たり食べたりしながら確かめたくなる切り口にする。
- 対象学年に合う言葉にする。
- 確信のない事実を作らない。
- 3案は互いに違う方向性にする。

次のJSONだけを返してください。説明文やMarkdownは不要です。
[
  {{"title":"短く印象的なテーマ名","hook":"児童への問いかけ","angle":"このテーマで何を伝えるかを80字程度"}},
  {{"title":"短く印象的なテーマ名","hook":"児童への問いかけ","angle":"このテーマで何を伝えるかを80字程度"}},
  {{"title":"短く印象的なテーマ名","hook":"児童への問いかけ","angle":"このテーマで何を伝えるかを80字程度"}}
]
"""
    try:
        result = ask_ai(prompt).replace("```json", "").replace("```", "").strip()
        st.session_state.ideas = json.loads(result)
    except Exception as e:
        st.error(f"AIの呼び出しに失敗しました：{e}")

if st.session_state.ideas:
    labels = [f"{i+1}. {idea['title']} — {idea['hook']}" for i, idea in enumerate(st.session_state.ideas)]
    selected_label = st.radio("使いたいテーマを選んでください", labels)
    selected = st.session_state.ideas[labels.index(selected_label)]
    st.info(f"**ねらい**：{selected['angle']}")
else:
    selected = None

st.divider()
st.subheader("② AIで児童向け本文を作る")
teacher_voice = st.text_area(
    "必ず入れたいあなた自身の言葉・経験",
    placeholder="例：給食時間に児童から『切干大根って大根なの？』と聞かれたことがあります。",
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
対象：{grade}
献立：{menu}
テーマ：{selected['title']}
問いかけ：{selected['hook']}
テーマのねらい：{selected['angle']}
学校・給食室ならではの情報：{real_point or '特になし'}
栄養教諭本人の言葉・経験：{teacher_voice or '特になし'}
文章量：{length}

児童が給食を食べながら『確かめてみたい』と思える本文を書いてください。
先生が児童に話しかける自然な日本語にし、説教調にせず、事実を勝手に作らないでください。
最後は短い問いかけで終え、本文だけを返してください。
"""
        try:
            st.session_state.article = ask_ai(prompt)
        except Exception as e:
            st.error(f"AIの呼び出しに失敗しました：{e}")

if st.session_state.article:
    article = st.text_area("AIが作った本文（ここで自由に直せます）", st.session_state.article, height=240, key="article_edit")
else:
    article = ""

st.divider()
st.subheader("③ 給食レシピを家庭向けに")
recipe_name = st.text_input("紹介する料理名", "切干大根の煮物")
original_servings = st.number_input("元のレシピの人数", min_value=1, value=1, step=1)
st.caption("材料は『材料名, 数量, 単位』の形で1行ずつ入力してください。例：切干大根, 12, g")
ingredients_text = st.text_area("材料", "切干大根, 12, g\nにんじん, 10, g\n油揚げ, 8, g")
steps = st.text_area("給食での作り方・調理手順", "1. 切干大根を水で戻す。\n2. 材料を食べやすい大きさに切る。\n3. 煮汁で煮て味を含ませる。")
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
            new_amount = int(new_amount) if new_amount.is_integer() else round(new_amount, 1)
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
給食での作り方：{steps}
給食ならではのコツ：{recipe_point or '特になし'}
入力されていない材料や分量を勝手に追加せず、材料、作り方、給食のプロのひとこと、の3項目で簡潔にまとめてください。
"""
    try:
        st.session_state.recipe_text = ask_ai(prompt)
    except Exception as e:
        st.error(f"AIの呼び出しに失敗しました：{e}")

if st.session_state.recipe_text:
    recipe_text = st.text_area("AIが整えた家庭向けレシピ（自由に修正できます）", st.session_state.recipe_text, height=260, key="recipe_edit")
else:
    recipe_text = ""

st.divider()
st.subheader("④ 家庭につなぐ")
home_try = st.text_input("おうちでTRY", "今日の給食で見つけた『へえ！』を、家の人に1つ話してみよう。")

st.divider()
st.subheader("⑤ 完成原稿・保存")
newsletter_title = st.text_input(
    "食育だよりのタイトル",
    selected['title'] if selected else "給食から見つける 食べもののひみつ",
)

if article:
    hook = selected["hook"] if selected else ""

    st.header(f"🥢 {newsletter_title}")
    if hook:
        st.info(f"💭 **みんなに質問！**\n\n{hook}")
    st.write(article)

    if recipe_text:
        st.markdown(f"### 🍳 おうちで作ってみよう！『{recipe_name}』")
        st.write(recipe_text)

    st.markdown("### 🏠 おうちでTRY")
    st.write(home_try)

    plain_text = f"""{newsletter_title}

{hook}

{article}

【おうちで作ってみよう！ {recipe_name}】
{recipe_text}

【おうちでTRY】
{home_try}
"""

    pdf_data = create_pdf(newsletter_title, hook, article, recipe_name, recipe_text, home_try)

    st.caption("上の内容を修正すると、下の保存データにもその内容が反映されます。")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📄 PDFで保存",
            data=pdf_data,
            file_name="食育だより.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "📝 テキストで保存",
            data=plain_text,
            file_name="食育だより原稿.txt",
            mime="text/plain",
            use_container_width=True,
        )
else:
    st.info("②で本文を作成すると、ここに完成原稿とPDF保存ボタンが表示されます。")

st.caption("AIの提案は下書きです。学校名、産地、栄養価、アレルギー情報などは必ず実際の資料で確認してから使用してください。")
