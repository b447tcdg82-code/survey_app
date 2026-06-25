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
st.title("Опрос: Отношение к геймификации в образовании")
st.markdown("Ответьте на несколько вопросов о вашем опыте с игровыми элементами в учёбе. Данные анонимны и используются только в учебных целях.")

with st.form("survey"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Ваш возраст", min_value=14, max_value=80, step=1, value=18)
        gender = st.radio("Пол", ["Мужской", "Женский", "Предпочитаю не указывать"])
        education = st.radio(
            "Уровень образования",
            ["Школьник", "Студент бакалавриата", "Студент магистратуры", "Аспирант", "Другое"]
        )
        encountered = st.radio(
            "Сталкивались ли вы с геймификацией в обучении?",
            ["Да", "Нет", "Не знаю, что это такое"]
        )

    with col2:
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
            ["Повышает мотивацию", "Снижает мотивацию", "Не влияет"]
        )
        fairness = st.slider(
            "Насколько справедливой вы считаете систему баллов в геймификации? (1–10)",
            1, 10, 5
        )
        stress = st.radio(
            "Влияет ли рейтинг (лидерборд) на ваш уровень стресса?",
            ["Повышает стресс", "Снижает стресс", "Не влияет на стресс"]
        )
        comment = st.text_area("Дополнительные комментарии (необязательно)")

    submitted = st.form_submit_button("Отправить ответ")

if submitted:
    record = {
        "age": int(age),
        "gender": gender,
        "education": education,
        "encountered_gamification": encountered,
        "engagement": int(engagement),
        "liked_elements": elements,
        "motivation_effect": motivation,
        "fairness": int(fairness),
        "stress_effect": stress,
        "comment": comment,
        "timestamp": datetime.utcnow()
    }
    try:
        db.collection("responses").add(record)
        st.success("Спасибо! Ваш ответ сохранён.")
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")

st.divider()

if st.checkbox("Показать аналитику (просмотр данных)"):
    docs = db.collection("responses").stream()
    data = [doc.to_dict() for doc in docs]

    if not data:
        st.info("Пока нет ответов.")
    else:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.subheader(f"Всего ответов: {len(df)}")
        st.dataframe(df.drop(columns=["timestamp", "comment"], errors="ignore").head(20))

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Вовлечённость в учёбу")
            fig1 = px.histogram(
                df, x="engagement", nbins=10,
                title="Распределение оценок вовлечённости",
                labels={"engagement": "Вовлечённость (1–10)", "count": "Количество"},
                color_discrete_sequence=["#636EFA"]
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Справедливость системы баллов")
            fig2 = px.histogram(
                df, x="fairness", nbins=10,
                title="Распределение оценок справедливости",
                labels={"fairness": "Справедливость (1–10)", "count": "Количество"},
                color_discrete_sequence=["#EF553B"]
            )
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Влияние на мотивацию")
            motivation_counts = df["motivation_effect"].value_counts().reset_index()
            motivation_counts.columns = ["Ответ", "Количество"]
            fig3 = px.pie(
                motivation_counts, values="Количество", names="Ответ",
                title="Как геймификация влияет на мотивацию?"
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("Влияние рейтинга на стресс")
            stress_counts = df["stress_effect"].value_counts().reset_index()
            stress_counts.columns = ["Ответ", "Количество"]
            fig4 = px.pie(
                stress_counts, values="Количество", names="Ответ",
                title="Влияние рейтинга на стресс"
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Популярные элементы геймификации")
        all_elements = [e for row in df["liked_elements"].dropna() for e in row]
        if all_elements:
            elem_series = pd.Series(all_elements).value_counts().reset_index()
            elem_series.columns = ["Элемент", "Количество"]
            fig5 = px.bar(
                elem_series, x="Элемент", y="Количество",
                title="Какие элементы геймификации нравятся респондентам",
                color_discrete_sequence=["#00CC96"]
            )
            st.plotly_chart(fig5, use_container_width=True)
