import streamlit as st
from pymongo import MongoClient
from datetime import datetime, date, time, timedelta
from textwrap import dedent
import base64
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FitGraph",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


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
                linear-gradient(rgba(5,5,5,0.85), rgba(5,5,5,0.85)),
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
# MONGODB CONNECTION
# ============================================================

MONGO_URI = (
    "mongodb+srv://soumyadeepdas2511:"
    "dxRsCQDq7YQSc1vh"
    "@cluster0.zmm4k.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0"
)


@st.cache_resource
def connect_to_mongodb():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client


try:
    client = connect_to_mongodb()
    db = client["gym_tracker"]
    daily_logs_collection = db["daily_logs"]
    mongo_connected = True
except Exception as error:
    mongo_connected = False
    mongo_error = str(error)


# ============================================================
# CSS — DARK PREMIUM THEME
# ============================================================

st.markdown(
    """
<style>
.stApp { color: #f5f5f5; }

header[data-testid="stHeader"] { background: transparent; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
    max-width: 1500px;
}

.main-header { margin-bottom: 25px; }

.main-title {
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #ffffff, #9db8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.main-subtitle {
    font-size: 15px;
    color: #777777;
    margin-top: 5px;
}

.blue-line {
    height: 1px;
    background: linear-gradient(90deg, #168cff, rgba(22,140,255,0.05));
    margin-top: 20px;
}

.database-online {
    display: inline-block;
    background: rgba(35, 190, 100, 0.08);
    border: 1px solid rgba(35, 190, 100, 0.30);
    color: #40d17d;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
}

.database-offline {
    display: inline-block;
    background: rgba(220, 50, 50, 0.08);
    border: 1px solid rgba(220, 50, 50, 0.30);
    color: #ff5c5c;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
}

.section-header { margin-top: 26px; margin-bottom: 12px; }

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-description {
    font-size: 13px;
    color: #707070;
    margin-top: 3px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #101010;
    border: 1px solid #242424;
    border-radius: 14px;
}

.stNumberInput input,
.stTextInput input,
.stTextArea textarea {
    background-color: #080808 !important;
    color: #ffffff !important;
    border: 1px solid #303030 !important;
    border-radius: 8px !important;
}

div[data-baseweb="select"] > div {
    background-color: #080808 !important;
    border-color: #303030 !important;
    color: #ffffff !important;
}

label { color: #bdbdbd !important; }

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #1266f1, #304fc2);
    color: #ffffff;
    border: none;
    border-radius: 9px;
    padding: 12px;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.5px;
    transition: 0.2s;
}

.stButton > button:hover {
    color: #ffffff;
    border: none;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(18, 102, 241, 0.35);
}

.calculated-box {
    background: #080808;
    border: 1px solid #242424;
    border-radius: 10px;
    padding: 18px;
    margin-top: 10px;
}

.calculated-label {
    font-size: 11px;
    color: #777777;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.calculated-value {
    font-size: 28px;
    font-weight: 700;
    color: #168cff;
    margin-top: 5px;
}

div[data-testid="stCheckbox"] {
    background: #080808;
    border: 1px solid #242424;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
}

.app-footer {
    text-align: center;
    color: #444444;
    font-size: 12px;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #181818;
}
</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def section_header(title, description):
    html = f"""
<div class="section-header">
    <div class="section-title">{title}</div>
    <div class="section-description">{description}</div>
</div>
"""
    st.markdown(dedent(html).strip(), unsafe_allow_html=True)


def calculate_sleep_hours(sleep_time_value, wake_time_value):
    sleep_datetime = datetime.combine(date.today(), sleep_time_value)
    wake_datetime = datetime.combine(date.today(), wake_time_value)

    if wake_datetime <= sleep_datetime:
        wake_datetime += timedelta(days=1)

    duration = wake_datetime - sleep_datetime
    return round(duration.total_seconds() / 3600, 2)


def g(d, *keys, default=None):
    """Safe nested dict getter: g(existing_log, 'body', 'weight', default=91.0)"""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


# ============================================================
# HEADER
# ============================================================

header_left, header_center, header_right = st.columns([4, 1, 1])

with header_left:
    header_html = """
<div class="main-header">
    <div class="main-title">Daily Fitness Log</div>
    <div class="main-subtitle">Track health, training and lifestyle performance.</div>
    <div class="blue-line"></div>
</div>
"""
    st.markdown(dedent(header_html).strip(), unsafe_allow_html=True)

with header_center:
    st.write("")
    st.write("")
    st.page_link("pages/home.py", label="🏠 Home", use_container_width=True)

with header_right:
    st.write("")
    if mongo_connected:
        st.markdown(
            '<div style="text-align: right; padding-top: 10px;">'
            '<span class="database-online">● DATABASE ONLINE</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align: right; padding-top: 10px;">'
            '<span class="database-offline">● DATABASE OFFLINE</span></div>',
            unsafe_allow_html=True,
        )

if not mongo_connected:
    st.error(f"MongoDB Connection Error: {mongo_error}")


# ============================================================
# DATE — pick, log, or edit any day
# ============================================================

section_header("📅 Log Date", "Select the date this fitness log belongs to. Pick a past date to edit it.")

with st.container(border=True):
    selected_date = st.date_input(
        "Select Date",
        value=date.today(),
        max_value=date.today(),
    )

log_date = datetime.combine(selected_date, datetime.min.time())

existing_log = None
if mongo_connected:
    existing_log = daily_logs_collection.find_one({"date": log_date})

if existing_log:
    st.info(f"Editing existing log for {selected_date.strftime('%d %B %Y')}.")


# ============================================================
# SLEEP + BODY / MENTAL
# ============================================================

left, right = st.columns(2, gap="medium")

with left:
    section_header("😴 Sleep & Recovery", "Track sleep schedule and recovery quality.")

    with st.container(border=True):
        sleep_col, wake_col = st.columns(2)

        default_sleep_time = time(1, 30)
        default_wake_time = time(8, 30)
        if existing_log:
            try:
                default_sleep_time = datetime.strptime(
                    g(existing_log, "sleep", "sleep_time", default="01:30"), "%H:%M"
                ).time()
                default_wake_time = datetime.strptime(
                    g(existing_log, "sleep", "wake_time", default="08:30"), "%H:%M"
                ).time()
            except ValueError:
                pass

        with sleep_col:
            sleep_time = st.time_input("Sleep Time", value=default_sleep_time)
        with wake_col:
            wake_time = st.time_input("Wake Up Time", value=default_wake_time)

        sleep_quality = st.slider(
            "Sleep Quality", min_value=1, max_value=10,
            value=g(existing_log, "sleep", "sleep_quality", default=7),
        )

        sleep_hours = calculate_sleep_hours(sleep_time, wake_time)

        sleep_html = f"""
<div class="calculated-box">
    <div class="calculated-label">Calculated Sleep Duration</div>
    <div class="calculated-value">{sleep_hours} Hours</div>
</div>
"""
        st.markdown(dedent(sleep_html).strip(), unsafe_allow_html=True)

with right:
    section_header("⚖️ Body & Mind", "Record your physical and mental state.")

    with st.container(border=True):
        weight = st.number_input(
            "Body Weight (KG)", min_value=30.0, max_value=250.0,
            value=float(g(existing_log, "body", "weight", default=89.0)), step=0.1,
        )

        mood_col, happiness_col = st.columns(2)
        with mood_col:
            mood = st.slider("Mood", 1, 10, g(existing_log, "mental", "mood", default=7))
        with happiness_col:
            happiness = st.slider("Happiness", 1, 10, g(existing_log, "mental", "happiness", default=8))

        energy_col, stress_col = st.columns(2)
        with energy_col:
            energy = st.slider("Energy", 1, 10, g(existing_log, "mental", "energy", default=6))
        with stress_col:
            stress = st.slider("Stress", 1, 10, g(existing_log, "mental", "stress", default=4))


# ============================================================
# DAILY ACTIVITY
# ============================================================

section_header("🚶 Daily Activity", "Track steps, walking distance, exercise time and hydration.")

with st.container(border=True):
    act_col1, act_col2, act_col3, act_col4 = st.columns(4)

    with act_col1:
        steps = st.number_input(
            "Steps", min_value=0,
            value=int(g(existing_log, "activity", "steps", default=8000)), step=100,
        )
    with act_col2:
        walking_km = st.number_input(
            "Walking Distance (KM)", min_value=0.0,
            value=float(g(existing_log, "activity", "walking_km", default=5.0)), step=0.1,
        )
    with act_col3:
        exercise_minutes = st.number_input(
            "Exercise Minutes", min_value=0,
            value=int(g(existing_log, "activity", "exercise_minutes", default=60)), step=5,
        )
    with act_col4:
        water = st.number_input(
            "Water Intake (Litres)", min_value=0.0,
            value=float(g(existing_log, "activity", "water_litres", default=3.0)), step=0.1,
        )


# ============================================================
# WORKOUT — free-form
# ============================================================

section_header("🏋️ Today's Workout", "Free typing. No dropdowns — describe your session however you like.")

with st.container(border=True):
    workout_title = st.text_input(
        "Workout Title",
        value=g(existing_log, "workout", "title", default=""),
        placeholder="Chest + Triceps",
    )

    workout_notes = st.text_area(
        "Workout Notes",
        value=g(existing_log, "workout", "notes", default=""),
        height=320,
        placeholder=(
            "Bench Press\n\n"
            "40 x 12\n50 x 10\n60 x 8\n\n"
            "Incline DB Press\n\n"
            "20 x 12\n22.5 x 10\n25 x 8\n\n"
            "Cable Fly\n\n"
            "15 x 15\n20 x 12\n\n"
            "Felt stronger today."
        ),
    )

    dur_col, rating_col = st.columns(2)
    with dur_col:
        workout_duration = st.number_input(
            "Workout Duration (Minutes)", min_value=0,
            value=int(g(existing_log, "workout", "duration_minutes", default=75)), step=5,
        )
    with rating_col:
        workout_rating = st.slider(
            "Workout Rating", min_value=1, max_value=10,
            value=g(existing_log, "workout", "rating", default=8),
        )


# ============================================================
# DAILY NOTES
# ============================================================

section_header("📝 Daily Notes", "Anything else worth remembering about today.")

with st.container(border=True):
    daily_notes = st.text_area(
        "Notes",
        value=g(existing_log, "daily_notes", default=""),
        height=160,
        placeholder="Busy day.\n\nShoulder slightly sore.\n\nNeed more sleep.\n\nGood pump.",
        label_visibility="collapsed",
    )


# ============================================================
# HABITS
# ============================================================

section_header("✅ Habits", "Daily checklist.")

with st.container(border=True):
    habit_col1, habit_col2 = st.columns(2)

    existing_habits = g(existing_log, "habits", default={}) or {}

    with habit_col1:
        gym_habit = st.checkbox("Gym Completed", value=existing_habits.get("gym", False))
        creatine_habit = st.checkbox("Creatine", value=existing_habits.get("creatine", False))
        whey_habit = st.checkbox("Whey Protein", value=existing_habits.get("whey", False))
        flaxseed_habit = st.checkbox("Flaxseed", value=existing_habits.get("flaxseed", False))

    with habit_col2:
        steps_habit = st.checkbox("8,000 Steps", value=existing_habits.get("steps_8000", False))
        sleep_habit = st.checkbox("Sleep Before 1 AM", value=existing_habits.get("sleep_before_1", False))
        water_habit = st.checkbox("3L Water", value=existing_habits.get("water_3l", False))
        junk_habit = st.checkbox("No Junk Food", value=existing_habits.get("no_junk_food", False))


# ============================================================
# SAVE
# ============================================================

st.write("")
st.write("")

save_left, save_center, save_right = st.columns([1, 2, 1])
with save_center:
    save = st.button("SAVE DAILY LOG", use_container_width=True)


# ============================================================
# SAVE TO MONGODB
# ============================================================

if save:
    if not mongo_connected:
        st.error("Cannot save because MongoDB is offline.")
    else:
        log_date = datetime.combine(selected_date, datetime.min.time())

        daily_data = {
            "date": log_date,

            "sleep": {
                "sleep_time": sleep_time.strftime("%H:%M"),
                "wake_time": wake_time.strftime("%H:%M"),
                "sleep_hours": sleep_hours,
                "sleep_quality": sleep_quality,
            },

            "body": {
                "weight": weight,
            },

            "mental": {
                "mood": mood,
                "happiness": happiness,
                "energy": energy,
                "stress": stress,
            },

            "activity": {
                "steps": steps,
                "walking_km": walking_km,
                "exercise_minutes": exercise_minutes,
                "water_litres": water,
            },

            "workout": {
                "title": workout_title,
                "notes": workout_notes,
                "duration_minutes": workout_duration,
                "rating": workout_rating,
            },

            "daily_notes": daily_notes,

            "habits": {
                "gym": gym_habit,
                "whey": whey_habit,
                "steps_8000": steps_habit,
                "sleep_before_1": sleep_habit,
                "creatine": creatine_habit,
                "flaxseed": flaxseed_habit,
                "water_3l": water_habit,
                "no_junk_food": junk_habit,
            },

            "updated_at": datetime.now(),
        }

        try:
            result = daily_logs_collection.update_one(
                {"date": log_date},
                {
                    "$set": daily_data,
                    "$setOnInsert": {"created_at": datetime.now()},
                },
                upsert=True,
            )

            if result.upserted_id:
                st.success(f"New fitness log created for {selected_date.strftime('%d %B %Y')}")
            else:
                st.success(f"Fitness log updated for {selected_date.strftime('%d %B %Y')}")

        except Exception as error:
            st.error(f"MongoDB Save Error: {error}")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="app-footer">FITGRAPH · PERSONAL FITNESS INTELLIGENCE SYSTEM</div>',
    unsafe_allow_html=True,
)