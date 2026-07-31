import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, timedelta
import math




# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

st.set_page_config(page_title="IITDH Attendance — My Dashboard", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp, .main { background-color: #000000 !important; font-family: 'Sora', sans-serif !important; }
.block-container { padding-top: 2.5rem !important; background-color: #000000 !important; }
h1, h2, h3, h4, h5, h6 { color: #f5f5f5 !important; font-family: 'Sora', sans-serif !important; }
.stMarkdown p, label, .stMarkdown li, .stMarkdown span { color: #e5e5e5 !important; }
[data-testid="stHeader"] { background-color: #000000 !important; }
hr { border-color: #2a2a2a !important; }

.stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #141414 !important; color: #f5f5f5 !important; border: 1px solid #2a2a2a !important;
}
[data-baseweb="popover"], [data-baseweb="menu"] { background-color: #141414 !important; }
[data-baseweb="menu"] li { color: #f5f5f5 !important; }

[data-testid="stMetric"] {
    background: #111111; border: 1px solid #2a2a2a; border-radius: 10px; padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: #999999 !important; font-size: 0.82rem !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.6rem !important; font-weight: 700 !important; }

.hero-wrap {
    background: #0d0d0d; border: 1px solid #2a2a2a; border-left: 6px solid #ffffff;
    border-radius: 12px; padding: 1.8rem 2.2rem; margin-bottom: 1.5rem; font-family: 'Sora', sans-serif;
}
.hero-title { font-size:1.7rem; font-weight:700; color:#ffffff; margin:0 0 0.3rem 0; }
.hero-sub   { font-size:0.88rem; color:#999999; margin:0; }
.hero-badge {
    display:inline-block; margin-top:0.6rem; background:#141414; color:#ffffff;
    border:1px solid #2a2a2a; border-radius:999px; padding:4px 14px; font-size:12px;
    font-family:'JetBrains Mono',monospace; letter-spacing:0.05em;
}

.sec-header {
    font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 700; color: #ffffff !important;
    border-bottom: 2px solid #ffffff; padding-bottom: 0.4rem; margin: 1.4rem 0 0.9rem 0;
    text-transform: uppercase; letter-spacing: 0.06em;
}

[data-testid="stExpander"] { background-color: #0d0d0d !important; border: 1px solid #2a2a2a !important; border-radius: 8px !important; margin-bottom: 0.5rem !important; }
[data-testid="stExpander"] summary { background-color: #0d0d0d !important; }
[data-testid="stExpander"] summary > span { font-family: 'JetBrains Mono', monospace !important; font-size: 0.83rem !important; color: #f5f5f5 !important; font-weight: 600 !important; }
[data-testid="stExpanderDetails"] { background-color: #0a0a0a !important; }
[data-testid="stDataFrame"] { background-color: #0d0d0d !important; }

.status-bar {
    position: fixed; bottom: 0; left: 0; right: 0; background: #111111; color: #ffffff;
    text-align: center; padding: 5px 0; font-size: 11px; font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.06em; z-index: 9999; border-top: 1px solid #333;
}

.not-found-box {
    background: #0d0d0d; border: 1.5px solid #2a2a2a; border-left: 5px solid #eab308;
    border-radius: 10px; padding: 1.4rem 1.6rem; margin: 1rem 0;
}
</style>
<div class="status-bar">IITDH ATTENDANCE PORTAL &nbsp;·&nbsp; MY DASHBOARD &nbsp;·&nbsp; IIT DHARWAD</div>
""", unsafe_allow_html=True)




# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
HIDDEN_COLS = {"template", "created_at", "password_hash", "password"}


def clean(df):
    drop = [c for c in df.columns if c in HIDDEN_COLS]
    return df.drop(columns=drop, errors="ignore")


@st.cache_data(ttl=60)
def fetch_table(table_name):
    try:
        r = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(r.data)
    except Exception as e:
        st.error(f"Error fetching {table_name}: {e}")
        return pd.DataFrame()


def detect_date_col(df):
    for c in ["session_date", "date", "class_date", "attendance_date", "timestamp", "created_at"]:
        if c in df.columns:
            return c
    return None


def detect_stu_id_col(df):
    for c in ["student_id", "roll_no", "roll", "id"]:
        if c in df.columns:
            return c
    return None


def activity_ring_html(attended, total, student_label=""):
    pct   = round((attended / total) * 100, 1) if total > 0 else 0
    color = "#22c55e" if pct >= 75 else ("#eab308" if pct >= 50 else "#ef4444")
    badge = "Eligible" if pct >= 75 else ("At Risk" if pct >= 50 else "Below Threshold")
    R, cx, cy, sw = 60, 80, 80, 14
    circ = 2 * math.pi * R
    dash = circ * pct / 100
    gap  = circ - dash
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:10px;padding:12px 0;font-family:'Sora',sans-serif;">
      <div style="font-size:0.8rem;color:#bbbbbb;font-weight:500;text-align:center;">{student_label}</div>
      <svg viewBox="0 0 160 160" width="170" height="170" xmlns="http://www.w3.org/2000/svg">
        <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#2a2a2a" stroke-width="{sw}"/>
        <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{color}" stroke-width="{sw}"
                stroke-linecap="round" stroke-dasharray="{dash:.2f} {gap:.2f}"
                transform="rotate(-90 {cx} {cy})">
          <animate attributeName="stroke-dasharray" from="0 {circ:.2f}" to="{dash:.2f} {gap:.2f}" dur="0.8s" fill="freeze"/>
        </circle>
        <text x="{cx}" y="{cy-7}" text-anchor="middle" dominant-baseline="middle"
              font-family="'JetBrains Mono',monospace" font-size="24" font-weight="700" fill="{color}">{pct}%</text>
        <text x="{cx}" y="{cy+16}" text-anchor="middle" dominant-baseline="middle"
              font-family="'Sora',sans-serif" font-size="10" fill="#999999">{attended} / {total} classes</text>
      </svg>
      <div style="background:#141414;color:{color};border:1.5px solid #2a2a2a;border-radius:999px;padding:5px 18px;font-size:13px;font-weight:600;">{badge}</div>
    </div>"""


def pct_badge_html(pct):
    color = "#22c55e" if pct >= 75 else ("#eab308" if pct >= 50 else "#ef4444")
    return f'<span style="color:{color};font-weight:700;font-family:JetBrains Mono,monospace;">{pct}%</span>'




# ─────────────────────────────────────────────────────────────────────────────
# LOGIN GATE
# ─────────────────────────────────────────────────────────────────────────────
if not st.user.is_logged_in:
    st.markdown("""
    <div class="hero-wrap" style="text-align:center;">
      <div class="hero-title">IITDH Attendance Portal</div>
      <div class="hero-sub">Sign in with your institute Google account to view your attendance dashboard.</div>
    </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("🔐 Sign in with Google", use_container_width=True, type="primary"):
            st.login("google")
    st.stop()


user_email = (st.user.email or "").strip().lower()
user_name  = st.user.name or user_email


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
students_df    = fetch_table("students")
profs_df        = fetch_table("profs")
courses_df      = fetch_table("courses")
attendance_df   = fetch_table("attendance")
enrollments_df  = fetch_table("course_enrollments")

stu_id_col_s = detect_stu_id_col(students_df)
stu_id_col_a = detect_stu_id_col(attendance_df)
date_col     = detect_date_col(attendance_df)

if not attendance_df.empty and date_col:
    attendance_df[date_col] = pd.to_datetime(attendance_df[date_col], errors="coerce")

name_col_c = next((c for c in ["course_name", "name", "title"] if c in courses_df.columns), None)


def top_bar():
    left, right = st.columns([4, 1])
    with left:
        st.markdown(f"""
        <div class="hero-wrap">
          <div class="hero-title">Welcome, {user_name}</div>
          <div class="hero-sub">{user_email}</div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            fetch_table.clear()
            st.rerun()
        if st.button("🚪 Log out", use_container_width=True):
            st.logout()


# ─────────────────────────────────────────────────────────────────────────────
# MATCH USER TO A STUDENT OR PROFESSOR RECORD
# ─────────────────────────────────────────────────────────────────────────────
matched_student = None
if not students_df.empty and "email" in students_df.columns:
    m = students_df[students_df["email"].astype(str).str.strip().str.lower() == user_email]
    if not m.empty:
        matched_student = m.iloc[0]

matched_prof = None
if not profs_df.empty and "email" in profs_df.columns:
    m = profs_df[profs_df["email"].astype(str).str.strip().str.lower() == user_email]
    if not m.empty:
        matched_prof = m.iloc[0]




# ══════════════════════════════════════════════════════════════════════════════
# STUDENT DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if matched_student is not None:
    top_bar()
    st.markdown(
        f'<div class="hero-badge">🎓 STUDENT &nbsp;·&nbsp; {matched_student.get(stu_id_col_s, "")}</div>',
        unsafe_allow_html=True
    )
    st.write("")

    my_id = str(matched_student.get(stu_id_col_s, ""))

    # Determine enrolled courses
    if not enrollments_df.empty and "student_id" in enrollments_df.columns and "course_code" in enrollments_df.columns:
        my_enrol = enrollments_df[enrollments_df["student_id"].astype(str) == my_id]
        if "status" in my_enrol.columns:
            my_enrol = my_enrol[my_enrol["status"].isin(["active", "Active"])]
        my_course_codes = my_enrol["course_code"].astype(str).unique().tolist()
    elif stu_id_col_a and not attendance_df.empty:
        my_course_codes = attendance_df[attendance_df[stu_id_col_a].astype(str) == my_id]["course_code"].unique().tolist()
    else:
        my_course_codes = []

    if not my_course_codes:
        st.info("You aren't enrolled in any courses yet. Contact the admin office if this looks wrong.")
    else:
        rows = []
        for code in my_course_codes:
            crow = courses_df[courses_df["course_code"].astype(str) == code]
            cname = str(crow.iloc[0][name_col_c]) if not crow.empty and name_col_c else code

            course_att = attendance_df[attendance_df["course_code"].astype(str) == code].copy() if not attendance_df.empty else pd.DataFrame()
            if date_col and not course_att.empty:
                total_classes = course_att[date_col].dt.date.nunique()
                my_att = course_att[course_att[stu_id_col_a].astype(str) == my_id] if stu_id_col_a else pd.DataFrame()
                attended = my_att[date_col].dt.date.nunique() if not my_att.empty else 0
            else:
                total_classes = len(course_att)
                attended = len(course_att[course_att[stu_id_col_a].astype(str) == my_id]) if stu_id_col_a and not course_att.empty else 0

            pct = round((attended / total_classes) * 100, 1) if total_classes > 0 else 0.0
            rows.append({"code": code, "name": cname, "attended": attended, "total": total_classes, "pct": pct})

        # Summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Enrolled Courses", len(rows))
        avg_pct = round(sum(r["pct"] for r in rows) / len(rows), 1) if rows else 0
        m2.metric("Average Attendance", f"{avg_pct}%")
        below = sum(1 for r in rows if r["pct"] < 75)
        m3.metric("Courses Below 75%", below)

        st.markdown('<div class="sec-header">Attendance by Course</div>', unsafe_allow_html=True)
        cols = st.columns(min(3, len(rows)))
        for i, r in enumerate(rows):
            with cols[i % len(cols)]:
                st.markdown(f"<div style='text-align:center;font-weight:600;color:#f5f5f5;'>{r['code']} — {r['name']}</div>", unsafe_allow_html=True)
                st.markdown(activity_ring_html(r["attended"], r["total"]), unsafe_allow_html=True)




# ══════════════════════════════════════════════════════════════════════════════
# PROFESSOR DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif matched_prof is not None:
    top_bar()
    pid_col = next((c for c in ["prof_id", "id"] if c in profs_df.columns), "prof_id")
    my_pid = str(matched_prof.get(pid_col, ""))
    st.markdown(
        f'<div class="hero-badge">🧑‍🏫 PROFESSOR &nbsp;·&nbsp; {my_pid}</div>',
        unsafe_allow_html=True
    )
    st.write("")

    my_courses = courses_df[courses_df["prof_id"].astype(str) == my_pid] if "prof_id" in courses_df.columns else pd.DataFrame()

    if my_courses.empty:
        st.info("No courses are assigned to you yet. Contact the admin office if this looks wrong.")
    else:
        m1, m2 = st.columns(2)
        m1.metric("Courses Taught", len(my_courses))

        name_col_s = next((c for c in ["name", "student_name", "full_name", "first_name"] if c in students_df.columns), None)

        all_pcts = []

        st.markdown('<div class="sec-header">My Courses</div>', unsafe_allow_html=True)
        for _, course_row in my_courses.iterrows():
            code  = str(course_row["course_code"])
            cname = str(course_row[name_col_c]) if name_col_c else code

            course_att = attendance_df[attendance_df["course_code"].astype(str) == code].copy() if not attendance_df.empty else pd.DataFrame()
            if date_col and not course_att.empty:
                total_classes = course_att[date_col].dt.date.nunique()
            else:
                total_classes = len(course_att)

            # Enrolled students for this course
            if not enrollments_df.empty and "course_code" in enrollments_df.columns and "student_id" in enrollments_df.columns:
                enrolled_ids = enrollments_df[enrollments_df["course_code"].astype(str) == code]
                if "status" in enrolled_ids.columns:
                    enrolled_ids = enrolled_ids[enrolled_ids["status"].isin(["active", "Active"])]
                enrolled_ids = enrolled_ids["student_id"].astype(str).tolist()
            elif stu_id_col_a and not course_att.empty:
                enrolled_ids = course_att[stu_id_col_a].astype(str).unique().tolist()
            else:
                enrolled_ids = []

            enrolled_students = students_df[students_df[stu_id_col_s].astype(str).isin(enrolled_ids)].copy() if stu_id_col_s and enrolled_ids else pd.DataFrame()

            if date_col and not course_att.empty and stu_id_col_a:
                course_att["_date"] = course_att[date_col].dt.date
                per_stu = course_att.groupby(stu_id_col_a)["_date"].nunique().reset_index(name="Classes Attended")
            elif stu_id_col_a and not course_att.empty:
                per_stu = course_att.groupby(stu_id_col_a).size().reset_index(name="Classes Attended")
            else:
                per_stu = pd.DataFrame(columns=[stu_id_col_a or "student_id", "Classes Attended"])

            if not enrolled_students.empty and stu_id_col_s:
                merged = enrolled_students.merge(
                    per_stu.rename(columns={(stu_id_col_a or "student_id"): stu_id_col_s}),
                    on=stu_id_col_s, how="left"
                )
                merged["Classes Attended"] = merged["Classes Attended"].fillna(0).astype(int)
                merged["Attendance %"] = merged["Classes Attended"].apply(
                    lambda a: round((a / total_classes) * 100, 1) if total_classes > 0 else 0.0
                )
                all_pcts.extend(merged["Attendance %"].tolist())
                below_count = int((merged["Attendance %"] < 75).sum())
            else:
                merged = pd.DataFrame()
                below_count = 0

            expander_label = (
                f"{code}  —  {cname}   |   Classes Held: {total_classes}"
                f"   |   Enrolled: {len(enrolled_students)}   |   Below 75%: {below_count}"
            )
            with st.expander(expander_label):
                if merged.empty:
                    st.info("No enrolled students or attendance data yet for this course.")
                else:
                    display_cols = [name_col_s, stu_id_col_s, "Classes Attended", "Attendance %"]
                    display_cols = [c for c in display_cols if c in merged.columns or c in ("Classes Attended", "Attendance %")]
                    show_df = merged[display_cols].sort_values("Attendance %", ascending=True).reset_index(drop=True)
                    st.dataframe(
                        show_df,
                        use_container_width=True,
                        column_config={
                            "Attendance %": st.column_config.ProgressColumn(
                                "Attendance %", min_value=0, max_value=100, format="%.1f%%"
                            )
                        }
                    )

        if all_pcts:
            st.markdown('<div class="sec-header">Overview</div>', unsafe_allow_html=True)
            m2.metric("Overall Avg. Attendance (all sections)", f"{round(sum(all_pcts)/len(all_pcts), 1)}%")




# ══════════════════════════════════════════════════════════════════════════════
# NO MATCHING RECORD
# ══════════════════════════════════════════════════════════════════════════════
else:
    top_bar()
    st.markdown(f"""
    <div class="not-found-box">
      <p style='color:#facc15;font-weight:700;margin:0 0 0.5rem 0;'>⚠ Account Not Recognized</p>
      <p style='color:#ddd;font-size:0.9rem;margin:0;'>
        We couldn't find a student or professor record matching <strong>{user_email}</strong>.
        Please contact the admin office to make sure this email is on file in the registry.
      </p>
    </div>
    """, unsafe_allow_html=True)
