import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
import io
import base64
from pathlib import Path
from datetime import date

st.set_page_config(page_title="Fitness Dashboard", page_icon="📊", layout="wide")

# ============================================================
# BACKGROUND IMAGE
# ============================================================
def set_background(image_path):
    path = Path(image_path)
    if not path.exists():
        return
    encoded = base64.b64encode(path.read_bytes()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(5,5,10,0.82), rgba(5,5,10,0.82)),
                url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_background("pages/images/appbgpic.jpg")

# ============================================================
# CONFIG / DB
# ============================================================
MONGO_URI = "mongodb+srv://soumyadeepdas2511:dxRsCQDq7YQSc1vh@cluster0.zmm4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

@st.cache_resource
def get_db():
    client = MongoClient(MONGO_URI)
    return client["gym_tracker"]

@st.cache_data(ttl=300)
def load_data():
    db = get_db()
    docs = list(db["daily_logs"].find({}, {"_id": 0}))
    rows = []
    for d in docs:
        sleep = d.get("sleep", {}) or {}
        body = d.get("body", {}) or {}
        mental = d.get("mental", {}) or {}
        activity = d.get("activity", {}) or {}
        workout = d.get("workout", {}) or {}
        habits = d.get("habits", {}) or {}

        rows.append({
            "Date": pd.to_datetime(d.get("date")),

            # Sleep & Recovery
            "Sleep Time": sleep.get("sleep_time"),
            "Wake Time": sleep.get("wake_time"),
            "Sleep Hours": sleep.get("sleep_hours"),
            "Sleep Quality": sleep.get("sleep_quality"),

            # Body
            "Weight": body.get("weight"),

            # Mental Health
            "Mood": mental.get("mood"),
            "Happiness": mental.get("happiness"),
            "Energy": mental.get("energy"),
            "Stress": mental.get("stress"),

            # Daily Activity
            "Steps": activity.get("steps"),
            "Walking KM": activity.get("walking_km"),
            "Exercise Minutes": activity.get("exercise_minutes"),
            "Water Litres": activity.get("water_litres"),

            # Workout
            "Workout": workout.get("title"),
            "Workout Notes": workout.get("notes"),
            "Workout Duration (min)": workout.get("duration_minutes"),
            "Workout Rating": workout.get("rating"),

            # Daily Notes
            "Daily Notes": d.get("daily_notes", ""),

            # Habits
            "Gym Completed": habits.get("gym", False),
            "Creatine": habits.get("creatine", False),
            "Whey Protein": habits.get("whey", False),
            "Flaxseed": habits.get("flaxseed", False),
            "8000 Steps": habits.get("steps_8000", False),
            "Sleep Before 1 AM": habits.get("sleep_before_1", False),
            "3L Water": habits.get("water_3l", False),
            "No Junk Food": habits.get("no_junk_food", False),
        })
    return pd.DataFrame(rows).sort_values("Date")

# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1a1d29, #14161f);
        border: 1px solid #2a2d3a;
        border-radius: 14px;
        padding: 18px 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }
    [data-testid="stMetricLabel"] { color: #9aa0ac; font-size: 0.85rem; }
    [data-testid="stMetricValue"] { color: #f5f6fa; font-weight: 700; }

    .dash-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7c9eff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .dash-sub { color: #9aa0ac; margin-top: -6px; margin-bottom: 18px; }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1d29;
        border-radius: 10px 10px 0 0;
        padding: 8px 18px;
        color: #9aa0ac;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262a3a;
        color: #f5f6fa !important;
    }

    div[data-testid="stExpander"] {
        background-color: #14161f;
        border: 1px solid #262a3a;
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] {
        background-color: #0a0c12;
        border-right: 1px solid #21242f;
    }

    .countdown-box {
        background: linear-gradient(145deg, #1a1d29, #14161f);
        border: 1px solid #2a2d3a;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }
    .countdown-label {
        color: #9aa0ac;
        font-size: 0.9rem;
    }
    .countdown-value {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7c9eff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

CHART_TEMPLATE = "plotly_dark"
ACCENT = "#7c9eff"
ACCENT2 = "#a78bfa"

def style_fig(fig):
    fig.update_layout(
        template=CHART_TEMPLATE,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(color="#e5e7eb"),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#20222e")
    return fig

# ============================================================
# LOAD DATA
# ============================================================
df = load_data()

if not df.empty:
    full_range = pd.date_range(df["Date"].min(), df["Date"].max(), freq="D")
    df = df.set_index("Date").reindex(full_range).rename_axis("Date").reset_index()
    df["Workout"] = df["Workout"].fillna("Rest Day")
    habit_cols_all = [
        "Gym Completed", "Creatine", "Whey Protein", "Flaxseed",
        "8000 Steps", "Sleep Before 1 AM", "3L Water", "No Junk Food",
    ]
    for col in habit_cols_all:
        df[col] = df[col].fillna(False)

st.markdown('<div class="dash-title">📊 Fitness Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">Weight · Sleep · Steps · Mood · Workout log</div>', unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    # Home screen
    if st.button("Go to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

elif st.session_state.page == "dashboard":
    # Dashboard screen
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# ============================================================
# COUNTDOWN — TRAVEL DATE
# ============================================================
today = date.today()
target_date = date(today.year, 9, 26)
if target_date < today:
    target_date = date(today.year + 1, 9, 26)

days_left = (target_date - today).days

if days_left == 0:
    countdown_text = "Today! ✈️"
elif days_left == 1:
    countdown_text = "1 day left"
else:
    countdown_text = f"{days_left} days left"

st.markdown(
    f"""
    <div class="countdown-box">
        <div class="countdown-label">✈️ Countdown to {target_date.strftime('%d %B %Y')}</div>
        <div class="countdown-value">{countdown_text}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("No data found.")
    st.stop()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.header("Filters")
    min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
    date_range = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    workouts = sorted(df["Workout"].dropna().unique().tolist())
    selected_workouts = st.multiselect("Workout type", options=workouts, default=workouts)

    st.markdown("---")
    st.caption(f"{len(df)} total logged days")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df = df[(df["Date"] >= start) & (df["Date"] <= end)]

if selected_workouts:
    df = df[df["Workout"].isin(selected_workouts) | df["Workout"].isna()]

if df.empty:
    st.info("No data in the selected range/filters.")
    st.stop()

df = df.sort_values("Date")

# ============================================================
# METRICS
# ============================================================
def delta(series):
    s = series.dropna()
    if len(s) < 2:
        return None
    return round(s.iloc[-1] - s.iloc[-2], 2)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Weight", f"{df['Weight'].dropna().iloc[-1]:.1f} kg", delta=delta(df["Weight"]))
c2.metric("Avg Sleep", f"{df['Sleep Hours'].mean():.2f} hrs", delta=delta(df["Sleep Hours"]))
c3.metric("Avg Steps", f"{df['Steps'].mean():,.0f}", delta=delta(df["Steps"]))
c4.metric("Avg Mood", f"{df['Mood'].mean():.1f}/10", delta=delta(df["Mood"]))

st.write("")

# ============================================================
# TABS
# ============================================================
tab_weight, tab_sleep, tab_steps, tab_mood, tab_habits, tab_history = st.tabs(
    ["⚖️ Weight", "😴 Sleep", "👟 Steps", "🙂 Mood", "✅ Habits & Extras", "🏋️ History"]
)

with tab_weight:
    fig = px.line(df, x="Date", y="Weight", markers=True, color_discrete_sequence=[ACCENT])
    fig.update_traces(fill="tozeroy", fillcolor="rgba(124,158,255,0.08)")
    st.plotly_chart(style_fig(fig), use_container_width=True)

with tab_sleep:
    fig = px.line(df, x="Date", y="Sleep Hours", markers=True, color_discrete_sequence=[ACCENT2])
    fig.add_hline(y=8, line_dash="dot", line_color="#4b5563", annotation_text="target: 8h")
    st.plotly_chart(style_fig(fig), use_container_width=True)

with tab_steps:
    fig = px.bar(df, x="Date", y="Steps", color_discrete_sequence=[ACCENT])
    st.plotly_chart(style_fig(fig), use_container_width=True)

with tab_mood:
    fig = px.line(df, x="Date", y="Mood", markers=True, color_discrete_sequence=["#34d399"])
    fig.update_yaxes(range=[0, 10])
    st.plotly_chart(style_fig(fig), use_container_width=True)

with tab_habits:
    habit_cols = [
        "Gym Completed", "Creatine", "Whey Protein", "Flaxseed",
        "8000 Steps", "Sleep Before 1 AM", "3L Water", "No Junk Food",
    ]

    st.markdown("**Habit completion rate**")
    rates = (df[habit_cols].fillna(False).mean() * 100).round(0).sort_values(ascending=False)
    fig = px.bar(
        x=rates.values, y=rates.index, orientation="h",
        labels={"x": "% of days completed", "y": ""},
        color_discrete_sequence=[ACCENT],
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)

    st.markdown("**Mental health & activity extras**")
    extra_cols = [
        "Happiness", "Energy", "Stress", "Sleep Quality",
        "Walking KM", "Exercise Minutes", "Water Litres",
        "Workout Duration (min)", "Workout Rating",
    ]
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Avg Happiness", f"{df['Happiness'].mean():.1f}/10")
    e2.metric("Avg Energy", f"{df['Energy'].mean():.1f}/10")
    e3.metric("Avg Stress", f"{df['Stress'].mean():.1f}/10")
    e4.metric("Avg Sleep Quality", f"{df['Sleep Quality'].mean():.1f}/10")

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Avg Walking", f"{df['Walking KM'].mean():.1f} km")
    f2.metric("Avg Exercise", f"{df['Exercise Minutes'].mean():.0f} min")
    f3.metric("Avg Water", f"{df['Water Litres'].mean():.1f} L")
    f4.metric("Avg Workout Rating", f"{df['Workout Rating'].mean():.1f}/10")

    st.markdown("**Daily habit log**")
    st.dataframe(
        df[["Date"] + habit_cols].sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tab_history:
    for _, r in df.sort_values("Date", ascending=False).iterrows():
        title = r["Workout"] if pd.notna(r["Workout"]) else "Rest Day"
        with st.expander(f"{r['Date'].strftime('%d %b %Y')} — {title}"):
            if title == "Rest Day" and pd.isna(r.get("Weight")):
                st.caption("No log entry for this day.")
                continue
            meta_bits = []
            if pd.notna(r["Workout Duration (min)"]):
                meta_bits.append(f"⏱ {r['Workout Duration (min)']:.0f} min")
            if pd.notna(r["Workout Rating"]):
                meta_bits.append(f"⭐ {r['Workout Rating']:.0f}/10")
            if meta_bits:
                st.caption(" · ".join(meta_bits))
            if r["Workout Notes"]:
                st.code(r["Workout Notes"])
            if r["Daily Notes"]:
                st.write(r["Daily Notes"])

# ============================================================
# EXPORT
# ============================================================
st.markdown("---")
st.subheader("📥 Export Data")

output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Daily Logs")

st.download_button(
    label="⬇ Export to Excel",
    data=output.getvalue(),
    file_name="fitness_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
