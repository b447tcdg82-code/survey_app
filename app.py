import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
    else:
        KEY_PATH = os.getenv("FIREBASE_KEY", "serviceAccountKey.json")
        if not os.path.exists(KEY_PATH):
            st.error("Ошибка: файл serviceAccountKey.json не найден.")
            st.stop()
        cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Опрос: Геймификация в образовании", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0a0a1a;
        color: #e2e8f0;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0f0f2e 50%, #0a0a1a 100%);
    }

    h1 {
        color: #ffffff !important;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 30px rgba(168, 85, 247, 0.8), 0 0 60px rgba(168, 85, 247, 0.4);
        margin-bottom: 0.3rem !important;
    }

    h2, h3 {
        color: #c084fc !important;
        text-shadow: 0 0 15px rgba(168, 85, 247, 0.5);
    }

    p, label, .stMarkdown {
        color: #cbd5e1 !important;
    }

    /* Form container */
    .stForm {
        background: rgba(15, 15, 46, 0.8) !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 40px rgba(168, 85, 247, 0.15), inset 0 1px 0 rgba(255,255,255,0.05);
    }

    /* Submit button */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.5) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    .stFormSubmitButton > button:hover {
        box-shadow: 0 0 35px rgba(168, 85, 247, 0.8) !important;
        transform: translateY(-2px) !important;
    }

    /* Sliders */
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #a855f7 !important;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.8) !important;
    }

    .stSlider [data-baseweb="slider"] div {
        background-color: rgba(168, 85, 247, 0.3) !important;
    }

    /* Radio buttons */
    .stRadio label {
        color: #cbd5e1 !important;
    }

    /* Multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: rgba(124, 58, 237, 0.4) !important;
        border: 1px solid #a855f7 !important;
    }

    /* Number input */
    .stNumberInput input {
        background-color: rgba(15, 15, 46, 0.8) !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* Text area */
    .stTextArea textarea {
        background-color: rgba(15, 15, 46, 0.8) !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* Checkbox */
    .stCheckbox label {
        color: #c084fc !important;
    }

    /* Success/error messages */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 10px !important;
    }

    /* Divider */
    hr {
        border-color: rgba(168, 85, 247, 0.3) !important;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 10px !important;
    }

    /* Section header styling */
    .section-label {
        color: #a855f7;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="section-label">🎮 Учебное исследование · 2026</p>', unsafe_allow_html=True)
st.title("Геймификация в образовании")
st.markdown("Ответьте на вопросы о вашем опыте с игровыми элементами в учёбе. Данные анонимны и используются только в учебных целях.")

st.markdown("<br>", unsafe_allow_html=True)

with st.form("survey"):
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 👤 О вас")
        age = st.number_input("Ваш возраст", min_value=14, max_value=80, step=1, value=18)
        gender = st.radio("Пол", ["Мужской", "Женский", "Предпочитаю не указывать"])
        education = st.radio(
            "Уровень образования",
            ["Школьник", "Студент бакалавриата", "Студент магистратуры", "Аспирант", "Другое"]
        )

        st.markdown("#### 🎯 Опыт с геймификацией")
        encountered = st.radio(
            "Сталкивались ли вы с геймификацией в обучении?",
            ["Да", "Нет", "Не знаю, что это такое"]
        )
        frequency = st.radio(
            "Как часто вы встречаете геймификацию в учёбе?",
            ["Постоянно", "Иногда", "Редко", "Никогда", "Не знаю"]
        )
        platforms = st.multiselect(
            "Какие платформы с геймификацией вы использовали?",
            ["Duolingo", "Kahoot", "Quizlet", "Classcraft", "Учебная LMS с баллами", "Другое", "Ни одной"]
        )

    with col2:
        st.markdown("#### 📊 Оценка геймификации")
        engagement = st.slider(
            "Насколько вы вовлечены в учёбу, когда используется геймификация? (1–10)",
            1, 10, 5
        )
        elements = st.multiselect(
            "Какие элементы геймификации вам нравятся?",
            ["Баллы / очки", "Значки и ачивки", "Рейтинги / лидерборды", "Уровни сложности", "Награды", "Прогресс-бары", "Ничего из перечисленного"]
        )
        motivation = st.radio(
            "Как геймификация влияет на вашу мотивацию к учёбе?",
            ["Повышает мотивацию", "Снижает мотивацию", "Не влияет", "Не знаю"]
        )
        fairness = st.slider(
            "Насколько справедливой вы считаете систему баллов в геймификации? (1–10)",
            1, 10, 5
        )
        stress = st.radio(
            "Влияет ли рейтинг (лидерборд) на ваш уровень стресса?",
            ["Повышает стресс", "Снижает стресс", "Не влияет на стресс", "Не знаю"]
        )

        st.markdown("#### 🔮 Взгляд в будущее")
        preference = st.radio(
            "Что вы предпочитаете?",
            ["Геймифицированное обучение", "Традиционное обучение", "Без разницы", "Не знаю"]
        )
        rewards_meaningful = st.radio(
            "Кажутся ли вам награды в геймификации значимыми?",
            ["Да, мотивируют", "Нет, не важны", "Частично", "Не знаю"]
        )
        mandatory = st.radio(
            "Должна ли геймификация быть обязательной в образовании?",
            ["Да, везде", "Только для некоторых предметов", "Нет", "Не знаю"]
        )
        outcomes = st.radio(
            "Считаете ли вы, что геймификация улучшает результаты обучения?",
            ["Да", "Нет", "Не влияет", "Не знаю"]
        )
        comment = st.text_area("Дополнительные комментарии (необязательно)")

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚀 Отправить ответ")

if submitted:
    record = {
        "age": int(age),
        "gender": gender,
        "education": education,
        "encountered_gamification": encountered,
        "frequency": frequency,
        "platforms": platforms,
        "engagement": int(engagement),
        "liked_elements": elements,
        "motivation_effect": motivation,
        "fairness": int(fairness),
        "stress_effect": stress,
        "preference": preference,
        "rewards_meaningful": rewards_meaningful,
        "mandatory": mandatory,
        "outcomes": outcomes,
        "comment": comment,
        "timestamp": datetime.utcnow()
    }
    try:
        db.collection("responses").add(record)
        st.success("✅ Спасибо! Ваш ответ сохранён.")
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")

st.divider()

if st.checkbox("📈 Показать аналитику"):
    docs = db.collection("responses").stream()
    data = [doc.to_dict() for doc in docs]

    if not data:
        st.info("Пока нет ответов.")
    else:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        PURPLE = ["#a855f7", "#7c3aed", "#c084fc", "#6d28d9", "#d8b4fe", "#4c1d95", "#e9d5ff"]

        st.subheader(f"Всего ответов: {len(df)}")
        st.dataframe(df.drop(columns=["timestamp", "comment"], errors="ignore").head(20))

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.histogram(df, x="engagement", nbins=10,
                title="Вовлечённость при геймификации",
                labels={"engagement": "Оценка (1–10)"},
                color_discrete_sequence=["#a855f7"])
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.histogram(df, x="fairness", nbins=10,
                title="Справедливость системы баллов",
                labels={"fairness": "Оценка (1–10)"},
                color_discrete_sequence=["#7c3aed"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            mc = df["motivation_effect"].value_counts().reset_index()
            mc.columns = ["Ответ", "Количество"]
            fig3 = px.pie(mc, values="Количество", names="Ответ",
                title="Влияние на мотивацию", color_discrete_sequence=PURPLE)
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            sc = df["stress_effect"].value_counts().reset_index()
            sc.columns = ["Ответ", "Количество"]
            fig4 = px.pie(sc, values="Количество", names="Ответ",
                title="Влияние рейтинга на стресс", color_discrete_sequence=PURPLE)
            fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig4, use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            pc = df["preference"].value_counts().reset_index()
            pc.columns = ["Ответ", "Количество"]
            fig5 = px.bar(pc, x="Ответ", y="Количество",
                title="Геймификация vs Традиционное обучение",
                color_discrete_sequence=["#a855f7"])
            fig5.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig5, use_container_width=True)

        with col6:
            oc = df["outcomes"].value_counts().reset_index()
            oc.columns = ["Ответ", "Количество"]
            fig6 = px.bar(oc, x="Ответ", y="Количество",
                title="Улучшает ли геймификация результаты?",
                color_discrete_sequence=["#7c3aed"])
            fig6.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Популярные элементы геймификации")
        all_elements = [e for row in df["liked_elements"].dropna() for e in row]
        if all_elements:
            elem_series = pd.Series(all_elements).value_counts().reset_index()
            elem_series.columns = ["Элемент", "Количество"]
            fig7 = px.bar(elem_series, x="Элемент", y="Количество",
                title="Какие элементы нравятся респондентам",
                color_discrete_sequence=["#c084fc"])
            fig7.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig7, use_container_width=True)

        st.subheader("Использованные платформы")
        all_platforms = [p for row in df["platforms"].dropna() for p in row]
        if all_platforms:
            plat_series = pd.Series(all_platforms).value_counts().reset_index()
            plat_series.columns = ["Платформа", "Количество"]
            fig8 = px.bar(plat_series, x="Платформа", y="Количество",
                title="Какие платформы с геймификацией используют студенты",
                color_discrete_sequence=["#6d28d9"])
            fig8.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig8, use_container_width=True)
