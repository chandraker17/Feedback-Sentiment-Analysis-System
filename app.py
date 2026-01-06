import streamlit as st
import pandas as pd
from textblob import TextBlob
from db_config import get_connection

# --------------------------------------------------
# PAGE CONFIG (ONLY VALID ARGUMENTS)
# --------------------------------------------------
st.set_page_config(
    page_title="Customer Feedback & Sentiment Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM COLOR THEME (CSS)
# --------------------------------------------------
st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #000000
}

/* Centered title */
h1 {
    text-align: center;
    color: #1f2937;
}
h4 {
    text-align: center;
    color: #4b5563;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}
[data-testid="stSidebar"] * {
    color: #ffffff;
}

/* Buttons */
.stButton > button {
    background-color: #6366f1;
    color: white;
    border-radius: 8px;
    border: none;
}
.stButton > button:hover {
    background-color: #4f46e5;
}

/* Metric cards spacing */
[data-testid="metric-container"] {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
}

/* Dataframe */
.stDataFrame {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.markdown("<h1 Customer Feedback & Sentiment Analysis System</h1>", unsafe_allow_html=True)
st.markdown("<h2>Customer Sentiment Analysis</h2>", unsafe_allow_html=True)
st.markdown("---")

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
menu = st.sidebar.radio(
    "Navigation",
    ["Add Feedback", "View Feedback", "Analytics"]
)

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
conn = get_connection()
cursor = conn.cursor()

# --------------------------------------------------
# ADD FEEDBACK SECTION
# --------------------------------------------------
if menu == "Add Feedback":
    st.subheader("Add Customer Feedback")

    with st.form("feedback_form"):
        user_id = st.number_input("User ID", min_value=1, step=1)
        product_name = st.text_input("Product Name")
        feedback_text = st.text_area("Customer Feedback")
        rating = st.slider("Rating", 1, 5)
        submit = st.form_submit_button("Submit Feedback")

    if submit:
        cursor.execute(
            """
            INSERT INTO feedback (user_id, product_name, feedback_text, rating)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, product_name, feedback_text, rating)
        )
        conn.commit()

        feedback_id = cursor.lastrowid

        polarity = TextBlob(feedback_text).sentiment.polarity
        if polarity > 0.1:
            label = "Positive"
        elif polarity < -0.1:
            label = "Negative"
        else:
            label = "Neutral"

        cursor.execute(
            """
            INSERT INTO sentiment_analysis (feedback_id, sentiment_label, sentiment_score)
            VALUES (%s, %s, %s)
            """,
            (feedback_id, label, polarity)
        )
        conn.commit()

        st.success("Feedback submitted and sentiment analyzed successfully")

# --------------------------------------------------
# VIEW FEEDBACK SECTION
# --------------------------------------------------
elif menu == "View Feedback":
    st.subheader("Feedback Records")

    query = """
    SELECT f.feedback_id,
           f.product_name,
           f.feedback_text,
           f.rating,
           s.sentiment_label,
           s.sentiment_score
    FROM feedback f
    JOIN sentiment_analysis s ON f.feedback_id = s.feedback_id
    ORDER BY f.created_at DESC
    """

    df = pd.read_sql(query, conn)
    st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# ANALYTICS SECTION
# --------------------------------------------------
elif menu == "Analytics":
    st.subheader("Analytics Dashboard")

    query = """
    SELECT f.product_name,
           f.rating,
           s.sentiment_label
    FROM feedback f
    JOIN sentiment_analysis s ON f.feedback_id = s.feedback_id
    """

    df = pd.read_sql(query, conn)

    # KPI METRICS
    total_feedback = len(df)
    positive = len(df[df["sentiment_label"] == "Positive"])
    negative = len(df[df["sentiment_label"] == "Negative"])
    avg_rating = round(df["rating"].mean(), 2) if total_feedback > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Feedback", total_feedback)
    col2.metric("Positive", positive)
    col3.metric("Negative", negative)
    col4.metric("Avg Rating", avg_rating)

    st.markdown("---")

    # Sentiment Distribution Chart
    st.markdown("### Sentiment Distribution")
    sentiment_count = df["sentiment_label"].value_counts()
    st.bar_chart(sentiment_count)

    # Product-wise Average Rating
    st.markdown("### Product-wise Average Rating")
    product_rating = df.groupby("product_name")["rating"].mean()
    st.line_chart(product_rating)
