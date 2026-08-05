import streamlit as st
from supabase import create_client
import pandas as pd
import datetime
from datetime import datetime, date, timedelta, timezone  # <--- Added datetime class here
import math
import re
from io import BytesIO



# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)
st.set_page_config(page_title="IITDH Attendance Portal", page_icon="🎓", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Base / background ────────────────────────────────────── */
.stApp, .main { background-color: #000000 !important; font-family: 'Sora', sans-serif !important; }
.block-container { padding-top: 2.5rem !important; background-color: #000000 !important; }
h1, h2, h3, h4, h5, h6 { color: #f5f5f5 !important; font-family: 'Sora', sans-serif !important; }
.stMarkdown p, label, .stMarkdown li, .stMarkdown span { color: #e5e5e5 !important; }
[data-testid="stHeader"] { background-color: #000000 !important; }
[data-testid="stSidebar"] { background-color: #0a0a0a !important; }
hr { border-color: #2a2a2a !important; }

/* ── Inputs / widgets ─────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div, .stTextArea textarea {
    background-color: #141414 !important;
    color: #f5f5f5 !important;
    border: 1px solid #2a2a2a !important;
}
[data-baseweb="popover"] { background-color: #141414 !important; }
[data-baseweb="menu"] { background-color: #141414 !important; }
[data-baseweb="menu"] li { color: #f5f5f5 !important; }
.stCheckbox label span { color: #e5e5e5 !important; }

/* ── Nav buttons ──────────────────────────────────────────── */
.nav-btn button {
    width: 100% !important;
    border: none !important;
    border-bottom: 3px solid #2a2a2a !important;
    border-radius: 0 !important;
    background: #0d0d0d !important;
    color: #999999 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 0.2rem !important;
    font-family: 'Sora', sans-serif !important;
    white-space: nowrap !important;
}
.nav-btn button:hover {
    background: #1a1a1a !important;
    color: #ffffff !important;
}
.nav-btn-active button {
    width: 100% !important;
    border: none !important;
    border-bottom: 3px solid #ffffff !important;
    border-radius: 0 !important;
    background: #000000 !important;
    color: #ffffff !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    padding: 0.65rem 0.2rem !important;
    font-family: 'Sora', sans-serif !important;
    white-space: nowrap !important;
}

/* ── Tabs ─────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { background-color: #0d0d0d !important; color: #999999 !important; border-radius: 6px 6px 0 0 !important; }
.stTabs [aria-selected="true"] { background-color: #1a1a1a !important; color: #ffffff !important; }

/* ── Metrics ──────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #111111; border: 1px solid #2a2a2a;
    border-radius: 10px; padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: #999999 !important; font-size: 0.82rem !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.6rem !important; font-weight: 700 !important; }


/* ── Session card ─────────────────────────────────────────── */
.sess-card {
    background: #111111; border: 1px solid #2a2a2a;
    border-left: 4px solid #ffffff; border-radius: 10px;
    padding: 1rem 1.2rem; margin-bottom: 0.75rem;
    transition: box-shadow 0.15s; font-family: 'Sora', sans-serif;
}
.sess-card:hover { box-shadow: 0 4px 14px rgba(255,255,255,0.06); }
.sess-card-code { font-family:'JetBrains Mono',monospace; font-size:0.75rem;
                  font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                  color:#ffffff; margin-bottom:0.3rem; }
.sess-card-name { font-size:0.95rem; font-weight:600; color:#f5f5f5; margin-bottom:0.3rem; }
.sess-card-prof { font-size:0.8rem; color:#999999; }
.sess-card-meta { font-family:'JetBrains Mono',monospace; font-size:0.75rem;
                  color:#777777; margin-top:0.3rem; }


/* ── Hero banner ──────────────────────────────────────────── */
.hero-wrap {
    background: #0d0d0d; border: 1px solid #2a2a2a;
    border-left: 6px solid #ffffff; border-radius: 12px;
    padding: 1.8rem 2.2rem; margin-bottom: 1.5rem;
    font-family: 'Sora', sans-serif;
}
.hero-title { font-size:1.9rem; font-weight:700; color:#ffffff; margin:0 0 0.3rem 0; }
.hero-sub   { font-size:0.88rem; color:#999999; margin:0; }
.hero-date  { font-family:'JetBrains Mono',monospace; font-size:0.82rem; color:#dddddd; margin-top:0.5rem; }


/* ── Section headers ──────────────────────────────────────── */
.sec-header {
    font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 700;
    color: #ffffff !important; border-bottom: 2px solid #ffffff;
    padding-bottom: 0.4rem; margin: 1.4rem 0 0.9rem 0;
    text-transform: uppercase; letter-spacing: 0.06em;
}


/* ── Expander ─────────────────────────────────────────────── */
[data-testid="stExpander"] { background-color: #0d0d0d !important; border: 1px solid #2a2a2a !important; border-radius: 8px !important; margin-bottom: 0.5rem !important; }
[data-testid="stExpander"] summary { background-color: #0d0d0d !important; }
[data-testid="stExpander"] summary > span { font-family: 'JetBrains Mono', monospace !important; font-size: 0.83rem !important; color: #f5f5f5 !important; font-weight: 600 !important; }
[data-testid="stExpanderDetails"] { background-color: #0a0a0a !important; }


/* ── Status bar ───────────────────────────────────────────── */
.status-bar {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #111111; color: #ffffff; text-align: center;
    padding: 5px 0; font-size: 11px; font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.06em; z-index: 9999; border-top: 1px solid #333;
}


/* ── Click hint ───────────────────────────────────────────── */
.click-hint {
    font-size: 0.8rem; color: #999999; margin-bottom: 0.4rem;
    padding: 6px 10px; background: #111111;
    border-left: 3px solid #444444; border-radius: 4px;
}


/* ── Edit panel ───────────────────────────────────────────── */
.edit-panel {
    background: #0d0d0d; border: 1.5px solid #2a2a2a;
    border-left: 5px solid #ffffff; border-radius: 10px;
    padding: 1.4rem 1.6rem; margin: 1rem 0;
    font-family: 'Sora', sans-serif;
}
.edit-panel-title {
    font-size: 0.9rem; font-weight: 700; color: #ffffff;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;
}
.danger-zone {
    background: #1a0d0d; border: 1.5px solid #5c1f1f;
    border-left: 5px solid #dc2626; border-radius: 10px;
    padding: 1.4rem 1.6rem; margin: 1rem 0;
}

/* ── Dataframes / tables ──────────────────────────────────── */
[data-testid="stDataFrame"] { background-color: #0d0d0d !important; }
</style>
<div class="status-bar">IITDH ATTENDANCE PORTAL &nbsp;·&nbsp; SYSTEM ONLINE &nbsp;·&nbsp; IIT DHARWAD</div>
""", unsafe_allow_html=True)




# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────


HIDDEN_COLS = {"template", "created_at", "password_hash", "password"}


# ── Reference mapping (source of truth for dept / program codes) ───────────
DEPT_MAP = {
    "CE": "Civil Engineering",
    "CH": "Chemical Engineering",
    "CS": "Computer Science and Engineering",
    "EC": "Electronics and Communication Engineering",
    "EE": "Electronics and Electrical Engineering",
    "EP": "Engineering Physics",
    "IS": "Interdisciplinary Sciences",
    "MC": "Mathematics and Computing",
    "ME": "Mechanical Engineering",
}

PROGRAM_MAP = {
    "BT": "B.Tech",
    "BM": "B.Sc.",
    "MT": "M.Tech",
    "MR": "M.S. Research",
}

# Roll No format: EE 23 BT 003  ->  dept(2 letters) + year(2 digits) + program(2 letters) + seq
ROLL_NO_REGEX = re.compile(r'^([A-Za-z]{2})(\d{2})([A-Za-z]{2})(\d+)$')


def parse_roll_no(roll_no):
    """Extract dept, program, admission year, and email from a roll number like EE23BT003."""
    if not roll_no or not isinstance(roll_no, str):
        return None
    m = ROLL_NO_REGEX.match(roll_no.strip())
    if not m:
        return None
    dept, yy, prog, _seq = m.groups()
    dept = dept.upper()
    prog = prog.upper()
    year = 2000 + int(yy)
    email = f"{roll_no.strip().lower()}@iitdh.ac.in"
    return {"dept": dept, "program": prog, "year": year, "email": email}


def find_col(df, candidates):
    """Case/whitespace-insensitive column lookup."""
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    return None


def make_excel_template(columns, sheet_name="Sheet1", sample_row=None):
    buf = BytesIO()
    df = pd.DataFrame([sample_row] if sample_row else [], columns=columns)
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buf.seek(0)
    return buf




def clean(df):
    drop = [c for c in df.columns if c in HIDDEN_COLS]
    return df.drop(columns=drop, errors="ignore")




def fingerprint_status(val):
    """
    Returns 'sync' if the fingerprint template is missing/empty (not yet
    enrolled on the scanner), otherwise returns None so the cell renders
    blank for students whose fingerprint has already been captured.
    """
    if val is None:
        return "sync"
    try:
        if isinstance(val, float) and pd.isna(val):
            return "sync"
    except TypeError:
        pass
    if isinstance(val, (bytes, bytearray)) and len(val) == 0:
        return "sync"
    if isinstance(val, str) and val.strip() == "":
        return "sync"
    return None


def add_fingerprint_column(df, template_col="template", new_col="Fingerprint"):
    """Adds a derived Fingerprint column (values: 'sync' or blank) based on
    the raw `template` bytea column coming from Supabase. Safe no-op if the
    template column isn't present in the given dataframe."""
    if df is None or df.empty or template_col not in df.columns:
        if df is not None and not df.empty and new_col not in df.columns:
            df = df.copy()
            df[new_col] = "sync"
        return df
    df = df.copy()
    df[new_col] = df[template_col].apply(fingerprint_status)
    return df




@st.cache_data(ttl=60)
def fetch_table(table_name):
    try:
        r = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(r.data)
    except Exception as e:
        st.error(f"Error fetching {table_name}: {e}")
        return pd.DataFrame()




def refresh_all():
    fetch_table.clear()
    st.rerun()




def detect_date_col(df):
    for c in ["date", "class_date", "attendance_date", "timestamp", "created_at", "session_date"]:
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
      <svg viewBox="0 0 160 160" width="190" height="190" xmlns="http://www.w3.org/2000/svg">
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
      <div style="display:flex;gap:16px;font-size:11px;color:#bbbbbb;">
        <span style="display:flex;align-items:center;gap:5px;">
          <span style="width:10px;height:10px;border-radius:50%;background:{color};display:inline-block;"></span>Attended
        </span>
        <span style="display:flex;align-items:center;gap:5px;">
          <span style="width:10px;height:10px;border-radius:50%;background:#2a2a2a;border:1px solid #444444;display:inline-block;"></span>Absent
        </span>
      </div>
      <div style="background:#141414;color:{color};border:1.5px solid #2a2a2a;border-radius:999px;padding:5px 18px;font-size:13px;font-weight:600;">{badge}</div>
    </div>"""




# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
attendance_df    = fetch_table("attendance")
students_df      = fetch_table("students")
courses_df       = fetch_table("courses")
profs_df         = fetch_table("profs")
enrollments_df   = fetch_table("course_enrollments")
programs_df      = fetch_table("programs")
departments_df   = fetch_table("departments")


date_col     = detect_date_col(attendance_df)
stu_id_col_a = detect_stu_id_col(attendance_df)
stu_id_col_s = detect_stu_id_col(students_df)


# Use session_date if present, else timestamp for attendance
if not attendance_df.empty:
    if "session_date" in attendance_df.columns:
        date_col = "session_date"
    elif "timestamp" in attendance_df.columns:
        date_col = "timestamp"


if not attendance_df.empty and date_col:
    attendance_df[date_col] = pd.to_datetime(attendance_df[date_col], errors="coerce")




def build_course_lookup():
    lookup = {}
    if courses_df.empty:
        return lookup
    name_c = next((c for c in ["course_name", "name", "title"] if c in courses_df.columns), None)
    prof_map = {}
    if not profs_df.empty:
        pid = next((c for c in ["prof_id", "id"] if c in profs_df.columns), None)
        pnm = next((c for c in ["prof_name", "name", "full_name"] if c in profs_df.columns), None)
        if pid and pnm:
            for _, r in profs_df.iterrows():
                prof_map[str(r[pid])] = str(r[pnm])
    for _, row in courses_df.iterrows():
        code  = str(row.get("course_code", ""))
        cname = str(row.get(name_c, code)) if name_c else code
        # courses table links via prof_id -> profs table
        prof_id_val = str(row.get("prof_id", ""))
        resolved_prof = prof_map.get(prof_id_val, prof_id_val)
        lookup[code] = {"name": cname, "prof": resolved_prof, "prof_id": prof_id_val}
    return lookup




course_lookup = build_course_lookup()




# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
NAV_LABELS = ["Home", "Attendance", "Students", "Professors", "Courses", "Att. Log", "⚙ Manage"]


if "page" not in st.session_state:
    st.session_state.page = "Home"


nav_cols = st.columns(len(NAV_LABELS))
for i, label in enumerate(NAV_LABELS):
    css_class = "nav-btn-active" if st.session_state.page == label else "nav-btn"
    with nav_cols[i]:
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


page = st.session_state.page
st.markdown("<hr style='margin:0 0 1.2rem 0; border-color:#2a2a2a;'>", unsafe_allow_html=True)




# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":
    today     = date.today()
    today_str = today.strftime("%A, %d %B %Y")


    st.markdown(f"""
    <div class="hero-wrap">
      <div class="hero-title">IITDH Attendance Portal</div>
      <div class="hero-sub">Indian Institute of Technology Dharwad — Academic Attendance System</div>
      <div class="hero-date">{today_str}</div>
    </div>""", unsafe_allow_html=True)


    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students",     len(students_df)   if not students_df.empty   else 0)
    c2.metric("Courses",      len(courses_df)    if not courses_df.empty    else 0)
    c3.metric("Faculty",      len(profs_df)      if not profs_df.empty      else 0)
    c4.metric("Total Swipes", len(attendance_df) if not attendance_df.empty else 0)


    st.markdown('<div class="sec-header">Sessions Today</div>', unsafe_allow_html=True)
    if attendance_df.empty or not date_col:
        st.info("No attendance data available.")
    else:
        today_att = attendance_df[attendance_df[date_col].dt.date == today]
        if today_att.empty:
            st.info("No sessions recorded for today yet.")
        else:
            grouped = list(today_att.groupby("course_code"))
            cols = st.columns(min(3, len(grouped)))
            for i, (code, grp) in enumerate(grouped):
                info = course_lookup.get(code, {"name": code, "prof": "—"})
                with cols[i % len(cols)]:
                    st.markdown(f"""
                    <div class="sess-card">
                      <div class="sess-card-code">{code}</div>
                      <div class="sess-card-name">{info['name']}</div>
                      <div class="sess-card-prof">Prof: {info['prof'] or '—'}</div>
                      <div class="sess-card-meta">{len(grp)} swipe(s) recorded</div>
                    </div>""", unsafe_allow_html=True)


    st.markdown('<div class="sec-header">Recent Sessions — Last 7 Days</div>', unsafe_allow_html=True)
    if not attendance_df.empty and date_col:
        week_ago = pd.Timestamp(today) - timedelta(days=7)
        recent   = attendance_df[attendance_df[date_col] >= week_ago].copy()
        recent["_date"] = recent[date_col].dt.date
        if recent.empty:
            st.info("No sessions in the last 7 days.")
        else:
            sessions = (recent.groupby(["_date", "course_code"])
                        .size().reset_index(name="swipes")
                        .sort_values("_date", ascending=False))
            cols = st.columns(3)
            for i, row in sessions.iterrows():
                info = course_lookup.get(row["course_code"], {"name": row["course_code"], "prof": "—"})
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="sess-card">
                      <div class="sess-card-code">{row['course_code']}</div>
                      <div class="sess-card-name">{info['name']}</div>
                      <div class="sess-card-prof">Prof: {info['prof'] or '—'}</div>
                      <div class="sess-card-meta">{row['_date'].strftime('%d %b %Y')} · {row['swipes']} swipe(s)</div>
                    </div>""", unsafe_allow_html=True)
    else:
        st.info("No attendance data available.")




# ══════════════════════════════════════════════════════════════════════════════
# ATTENDANCE LOGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Attendance":
    st.header("Attendance Records")
    if attendance_df.empty:
        st.info("No attendance records found.")
    else:
        all_courses = sorted(attendance_df["course_code"].dropna().unique().tolist())
        sel_courses = st.multiselect("Filter by Course", options=all_courses, default=all_courses)
        filt = attendance_df[attendance_df["course_code"].isin(sel_courses)]
        st.metric("Total Swipes Shown", len(filt))


        if date_col:
            filt = filt.copy()
            filt["_date"] = filt[date_col].dt.date
            grouped     = filt.groupby(["_date", "course_code"])
            sorted_keys = sorted(grouped.groups.keys(), reverse=True)
            for (sess_date, code) in sorted_keys:
                grp  = grouped.get_group((sess_date, code))
                info = course_lookup.get(code, {"name": code, "prof": "—"})
                with st.expander(
                    f"{code} — {info['name']}  |  "
                    f"{sess_date.strftime('%d %b %Y')}  |  "
                    f"Prof: {info['prof'] or '—'}  |  "
                    f"{len(grp)} swipe(s)"
                ):
                    st.dataframe(clean(grp.drop(columns=["_date"], errors="ignore").reset_index(drop=True)), use_container_width=True)
        else:
            for code in sel_courses:
                grp  = filt[filt["course_code"] == code]
                info = course_lookup.get(code, {"name": code, "prof": "—"})
                with st.expander(f"{code} — {info['name']}  |  {len(grp)} swipe(s)"):
                    st.dataframe(clean(grp.reset_index(drop=True)), use_container_width=True)




# ══════════════════════════════════════════════════════════════════════════════
# STUDENT DIRECTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Students":
    st.header("Registered Students")
    df = add_fingerprint_column(students_df.copy())
    if not df.empty:
        search = st.text_input("Search by Name or ID")
        if search:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        st.dataframe(clean(df), use_container_width=True)
    else:
        st.info("No students enrolled yet.")




# ══════════════════════════════════════════════════════════════════════════════
# PROFESSOR LIST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Professors":
    st.header("Faculty Members")
    if not profs_df.empty:
        st.table(clean(add_fingerprint_column(profs_df.copy())))
    else:
        st.info("No professor records found.")




# ══════════════════════════════════════════════════════════════════════════════
# COURSE CATALOG
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Courses":
    st.header("Course Catalog")
    df = courses_df.copy()
    if not df.empty:
        col_type, col_query = st.columns([1, 3])
        with col_type:
            search_type = st.selectbox("Search by", ["Course Code", "Course Name", "Professor Name"])
        with col_query:
            search_query = st.text_input("Search term", placeholder=f"Type {search_type.lower()}...")
        if search_query:
            col_map = {
                "Course Code":    ["course_code", "code"],
                "Course Name":    ["course_name", "name", "title"],
                "Professor Name": ["prof_name", "professor_name", "instructor", "faculty"],
            }
            mc = next((c for c in col_map[search_type] if c in df.columns), None)
            if mc:
                df = df[df[mc].astype(str).str.contains(search_query, case=False, na=False)]
            else:
                st.warning(f"Column for '{search_type}' not found. Available: {list(df.columns)}")
        st.write(f"Showing **{len(df)}** course(s):")
        st.dataframe(clean(df), use_container_width=True)
    else:
        st.info("No courses created in database.")




# ══════════════════════════════════════════════════════════════════════════════
# STUDENT ATTENDANCE LOG
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Att. Log":
    st.header("Student Attendance Log")
    st.markdown('<div class="click-hint">Click any row in the table to see that student\'s attendance ring</div>', unsafe_allow_html=True)


    if courses_df.empty or attendance_df.empty or students_df.empty:
        st.info("Requires data in courses, attendance, and students tables.")
    else:
        name_col_c = next((c for c in ["course_name", "name", "title"] if c in courses_df.columns), None)
        id_col     = stu_id_col_s or (students_df.columns[0] if not students_df.empty else "id")
        name_col_s = next((c for c in ["name", "student_name", "full_name", "first_name"] if c in students_df.columns), None)


        # ── Search Bar ────────────────────────────────────────────────────────
        st.markdown('<div class="sec-header">Search</div>', unsafe_allow_html=True)
        search_col1, search_col2 = st.columns([1, 3])
        with search_col1:
            search_type = st.selectbox(
                "Search by",
                ["Course Code", "Course Name", "Professor Name", "Student Name", "Student ID"],
                key="att_log_search_type"
            )
        with search_col2:
            search_query = st.text_input(
                "Search term",
                placeholder=f"Type {search_type.lower()}...",
                key="att_log_search_query"
            )


        filtered_courses = courses_df.copy()


        if search_query:
            q = search_query.strip().lower()
            if search_type == "Course Code":
                filtered_courses = filtered_courses[
                    filtered_courses["course_code"].astype(str).str.lower().str.contains(q, na=False)
                ]
            elif search_type == "Course Name":
                if name_col_c:
                    filtered_courses = filtered_courses[
                        filtered_courses[name_col_c].astype(str).str.lower().str.contains(q, na=False)
                    ]
                else:
                    filtered_courses = filtered_courses.iloc[0:0]
            elif search_type == "Professor Name":
                def get_prof_name(code):
                    return course_lookup.get(str(code), {}).get("prof", "").lower()
                mask = filtered_courses["course_code"].apply(get_prof_name).str.contains(q, na=False)
                filtered_courses = filtered_courses[mask]
            elif search_type in ("Student Name", "Student ID"):
                stu_search_df = students_df.copy()
                if search_type == "Student Name" and name_col_s:
                    stu_search_df = stu_search_df[
                        stu_search_df[name_col_s].astype(str).str.lower().str.contains(q, na=False)
                    ]
                elif search_type == "Student ID" and stu_id_col_s:
                    stu_search_df = stu_search_df[
                        stu_search_df[stu_id_col_s].astype(str).str.lower().str.contains(q, na=False)
                    ]
                matching_ids = stu_search_df[stu_id_col_s].tolist() if stu_id_col_s else []
                if matching_ids and stu_id_col_a:
                    relevant_codes = attendance_df[
                        attendance_df[stu_id_col_a].isin(matching_ids)
                    ]["course_code"].unique().tolist()
                    filtered_courses = filtered_courses[filtered_courses["course_code"].isin(relevant_codes)]
                else:
                    filtered_courses = filtered_courses.iloc[0:0]


        if filtered_courses.empty:
            st.info("No courses match your search." if search_query else "No courses found.")
        else:
            st.markdown(
                f"<p style='color:#999;font-size:0.85rem;margin-bottom:0.5rem;'>Showing <strong>{len(filtered_courses)}</strong> course(s)</p>",
                unsafe_allow_html=True
            )


        for _, course_row in filtered_courses.iterrows():
            code        = str(course_row.get("course_code", ""))
            course_name = str(course_row.get(name_col_c, code)) if name_col_c else code
            info        = course_lookup.get(code, {"name": course_name, "prof": "—"})
            prof_name   = info.get("prof", "—") or "—"
            course_att  = attendance_df[attendance_df["course_code"] == code].copy()


            if date_col:
                total_classes = course_att[date_col].dt.date.nunique()
            else:
                total_classes = len(course_att)


            if not enrollments_df.empty and "course_code" in enrollments_df.columns and "student_id" in enrollments_df.columns:
                enrolled_ids = enrollments_df[
                    (enrollments_df["course_code"] == code) &
                    (enrollments_df.get("status", pd.Series(["active"] * len(enrollments_df))).isin(["active", "Active"]) if "status" in enrollments_df.columns else True)
                ]["student_id"].tolist()
                enrolled_students_df = students_df[students_df[stu_id_col_s].isin(enrolled_ids)].copy() if stu_id_col_s else students_df.copy()
            else:
                enrolled_ids = course_att[stu_id_col_a].unique().tolist() if stu_id_col_a and not course_att.empty else []
                enrolled_students_df = students_df[students_df[stu_id_col_s].isin(enrolled_ids)].copy() if stu_id_col_s and enrolled_ids else students_df.copy()


            total_enrolled = len(enrolled_students_df)


            if stu_id_col_a and stu_id_col_s:
                enrolled_students_df = add_fingerprint_column(enrolled_students_df)

                if date_col:
                    course_att["_date"] = course_att[date_col].dt.date
                    per_stu = (course_att.groupby(stu_id_col_a)["_date"]
                               .nunique().reset_index(name="Classes Attended"))
                else:
                    per_stu = (course_att.groupby(stu_id_col_a)
                               .size().reset_index(name="Classes Attended"))


                merged = enrolled_students_df.merge(
                    per_stu.rename(columns={stu_id_col_a: stu_id_col_s}),
                    on=stu_id_col_s, how="left"
                )
                merged["Classes Attended"] = merged["Classes Attended"].fillna(0).astype(int)


                if search_query and search_type in ("Student Name", "Student ID"):
                    q = search_query.strip().lower()
                    if search_type == "Student Name" and name_col_s:
                        merged = merged[
                            merged[name_col_s].astype(str).str.lower().str.contains(q, na=False)
                        ]
                    elif search_type == "Student ID" and stu_id_col_s:
                        merged = merged[
                            merged[stu_id_col_s].astype(str).str.lower().str.contains(q, na=False)
                        ]


                orig_cols  = [c for c in students_df.columns if c not in HIDDEN_COLS] + ["Fingerprint"]
                display_df = merged[orig_cols + ["Classes Attended"]].reset_index(drop=True)
            else:
                display_df = clean(add_fingerprint_column(enrolled_students_df.copy())).reset_index(drop=True)


            expander_label = (
                f"{code}  —  {course_name}"
                f"   |   Prof: {prof_name}"
                f"   |   Classes Held: {total_classes}"
                f"   |   Enrolled Students: {total_enrolled}"
            )
            with st.expander(expander_label, expanded=bool(search_query)):
                ci1, ci2, ci3, ci4 = st.columns(4)
                ci1.markdown(f"**Course Code:** `{code}`")
                ci2.markdown(f"**Professor:** {prof_name}")
                ci3.markdown(f"**Classes Held:** {total_classes}")
                ci4.markdown(f"**Enrolled Students:** {total_enrolled}")
                extra_course_cols = [
                    c for c in courses_df.columns
                    if c not in HIDDEN_COLS
                    and c not in {"course_code", "course_name", "name", "title",
                                  "prof_name", "professor_name", "instructor", "faculty", "prof_id"}
                ]
                if extra_course_cols:
                    extra_vals = {c: course_row.get(c, "") for c in extra_course_cols if pd.notna(course_row.get(c, ""))}
                    if extra_vals:
                        ex_cols = st.columns(min(4, len(extra_vals)))
                        for i, (k, v) in enumerate(extra_vals.items()):
                            ex_cols[i % len(ex_cols)].markdown(f"**{k.replace('_',' ').title()}:** {v}")
                st.markdown("---")
                if display_df.empty:
                    st.info("No students match your search for this course." if search_query else "No students enrolled.")
                    continue
                event = st.dataframe(
                    display_df,
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key=f"sel_{code}",
                )
                selected_rows = event.selection.rows if event and hasattr(event, "selection") else []
                if selected_rows:
                    stu_row  = display_df.iloc[selected_rows[0]]
                    attended = int(stu_row.get("Classes Attended", 0))
                    pct      = round((attended / total_classes) * 100, 1) if total_classes > 0 else 0
                    stu_id   = stu_row.get(id_col, "—")
                    stu_name = stu_row.get(name_col_s, "") if name_col_s else ""
                    label    = f"{stu_id}  ·  {stu_name}" if stu_name else str(stu_id)
                    st.markdown("---")
                    ring_col, info_col = st.columns([1, 1])
                    with ring_col:
                        st.markdown(activity_ring_html(attended, total_classes, label), unsafe_allow_html=True)
                    with info_col:
                        st.markdown(f"**Student ID:** `{stu_id}`")
                        if name_col_s:
                            st.markdown(f"**Name:** {stu_name}")
                        skip_cols = {id_col, name_col_s, "Classes Attended"} | HIDDEN_COLS
                        for col in stu_row.index:
                            if col not in skip_cols and pd.notna(stu_row[col]) and str(stu_row[col]).strip():
                                st.markdown(f"**{col.replace('_',' ').title()}:** {stu_row[col]}")
                        st.markdown(f"**Attended:** {attended} / {total_classes} classes")
                        if pct >= 75:
                            st.success(f"**{pct}%** — Eligible")
                        elif pct >= 50:
                            st.warning(f"**{pct}%** — At Risk")
                        else:
                            st.error(f"**{pct}%** — Below Threshold")




# ══════════════════════════════════════════════════════════════════════════════
# MANAGE — Edit / Admin Panel
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙ Manage":
    st.header("⚙ Manage — Admin Operations")
    st.markdown(
        "<p style='color:#999;font-size:0.88rem;margin-bottom:1.5rem;'>"
        "Use this panel to register students & professors, add courses, enrol students in courses "
        "(one at a time or in bulk via Excel), remove enrolments, or delete students from the registry."
        "</p>",
        unsafe_allow_html=True
    )

    with st.expander("🧬  Reference Data — Departments & Programs", expanded=False):
        st.markdown(
            "<p style='color:#999;font-size:0.83rem;'>"
            "These are the canonical department/program codes used to auto-derive fields from roll numbers. "
            "If your <code>departments</code> or <code>programs</code> tables are empty, seed them here so course "
            "and student forms have proper dropdowns.</p>",
            unsafe_allow_html=True
        )
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("**Departments**")
            st.dataframe(pd.DataFrame(list(DEPT_MAP.items()), columns=["dept_code", "dept_name"]),
                         use_container_width=True, hide_index=True)
            existing_depts = set(departments_df["dept_code"].astype(str)) if not departments_df.empty and "dept_code" in departments_df.columns else set()
            missing_depts = [k for k in DEPT_MAP if k not in existing_depts]
            if missing_depts:
                if st.button(f"➕ Seed {len(missing_depts)} missing department(s)", key="seed_depts"):
                    try:
                        payload = [{"dept_code": k, "dept_name": v} for k, v in DEPT_MAP.items() if k in missing_depts]
                        supabase.table("departments").insert(payload).execute()
                        st.success(f"✅ Seeded {len(payload)} department(s).")
                        fetch_table.clear()
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error seeding departments: {ex}")
            else:
                st.caption("All reference departments already present in the database.")
        with rc2:
            st.markdown("**Programs**")
            st.dataframe(pd.DataFrame(list(PROGRAM_MAP.items()), columns=["program_code", "program_name"]),
                         use_container_width=True, hide_index=True)
            existing_progs = set(programs_df["program_code"].astype(str)) if not programs_df.empty and "program_code" in programs_df.columns else set()
            missing_progs = [k for k in PROGRAM_MAP if k not in existing_progs]
            if missing_progs:
                if st.button(f"➕ Seed {len(missing_progs)} missing program(s)", key="seed_progs"):
                    try:
                        payload = [{"program_code": k, "program_name": v} for k, v in PROGRAM_MAP.items() if k in missing_progs]
                        supabase.table("programs").insert(payload).execute()
                        st.success(f"✅ Seeded {len(payload)} program(s).")
                        fetch_table.clear()
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error seeding programs: {ex}")
            else:
                st.caption("All reference programs already present in the database.")


    tab_new, tab_bulk_stu, tab_prof, tab1, tab2, tab_bulk_enrol, tab3, tab4 = st.tabs([
        "🎓  Add Student",
        "📥  Bulk Add Students",
        "🧑‍🏫  Add Professor",
        "➕  Add Course",
        "📋  Enrol Student",
        "📥  Bulk Enrol (Excel)",
        "🗑  Remove Enrolment",
        "❌  Delete Student",
    ])


    # ──────────────────────────────────────────────────────────────────────────
    # TAB NEW — REGISTER NEW STUDENT
    # ──────────────────────────────────────────────────────────────────────────
    with tab_new:
        st.markdown('<div class="sec-header">Register New Student</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#999;font-size:0.85rem;margin-bottom:1rem;'>"
            "Only <strong>Name</strong> and <strong>Roll No</strong> are required. Department, Program, "
            "Admission Year, and Email are auto-derived from the roll number "
            "(e.g. <code>EE23BT003</code> → dept <code>EE</code>, program <code>BT</code>, year <code>2023</code>, "
            "email <code>ee23bt003@iitdh.ac.in</code>).</p>",
            unsafe_allow_html=True
        )

        sid_col_new = stu_id_col_s or "student_id"

        with st.form("add_student_form", clear_on_submit=True):
            sc1, sc2 = st.columns(2)
            with sc1:
                new_stu_roll = st.text_input(
                    "Roll No *",
                    placeholder="e.g. EE23BT003",
                    help="Format: <Dept><Year><Program><Seq>, e.g. EE23BT003"
                )
                new_stu_name = st.text_input(
                    "Full Name *",
                    placeholder="e.g. Aditi Sharma"
                )
            with sc2:
                st.caption("Optional overrides — leave blank to auto-derive from the roll number above.")
                ov_dept = st.text_input("Department code override", placeholder="auto")
                ov_program = st.text_input("Program code override", placeholder="auto")
                ov_year = st.text_input("Admission year override", placeholder="auto")
                ov_email = st.text_input("Email override", placeholder="auto")

            stu_submitted = st.form_submit_button("🎓 Add Student", use_container_width=True, type="primary")

        if stu_submitted:
            errors = []
            roll_clean = new_stu_roll.strip().upper()
            if not roll_clean:
                errors.append("Roll No is required.")
            if not new_stu_name.strip():
                errors.append("Full Name is required.")

            parsed = parse_roll_no(roll_clean) if roll_clean else None

            has_full_override = ov_dept.strip() and ov_program.strip() and ov_year.strip()
            if roll_clean and parsed is None and not has_full_override:
                errors.append(
                    f"Roll No **{roll_clean}** doesn't match the expected format (e.g. EE23BT003). "
                    "Provide Department, Program, and Admission Year overrides to proceed anyway."
                )

            if not students_df.empty and sid_col_new in students_df.columns and \
               roll_clean in students_df[sid_col_new].astype(str).str.upper().values:
                errors.append(f"Roll No **{roll_clean}** already exists.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                dept_val = ov_dept.strip().upper() if ov_dept.strip() else parsed["dept"]
                program_val = ov_program.strip().upper() if ov_program.strip() else parsed["program"]
                year_val = int(ov_year.strip()) if ov_year.strip() else parsed["year"]
                email_val = ov_email.strip() if ov_email.strip() else parsed["email"]

                if dept_val not in DEPT_MAP:
                    st.warning(f"⚠ Department code **{dept_val}** isn't in the known reference list — saving anyway.")
                if program_val not in PROGRAM_MAP:
                    st.warning(f"⚠ Program code **{program_val}** isn't in the known reference list — saving anyway.")

                payload = {
                    sid_col_new: roll_clean,
                    "name": new_stu_name.strip(),
                    "dept": dept_val,
                    "program": program_val,
                    "admission_year": year_val,
                    "email": email_val,
                }
                try:
                    result = supabase.table("students").insert(payload).execute()
                    if result.data:
                        st.success(f"✅ Student **{new_stu_name.strip()} ({roll_clean})** added successfully!")
                        fetch_table.clear()
                    else:
                        st.error("Insert failed. No data returned from Supabase.")
                except Exception as ex:
                    st.error(f"Error adding student: {ex}")

        st.markdown('<div class="sec-header">Existing Students</div>', unsafe_allow_html=True)
        if not students_df.empty:
            st.dataframe(clean(add_fingerprint_column(students_df.copy())), use_container_width=True)
        else:
            st.info("No students in database yet.")


    # ──────────────────────────────────────────────────────────────────────────
    # TAB BULK STU — BULK REGISTER STUDENTS VIA EXCEL
    # ──────────────────────────────────────────────────────────────────────────
    with tab_bulk_stu:
        st.markdown('<div class="sec-header">Bulk Register Students via Excel</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#999;font-size:0.85rem;margin-bottom:0.8rem;'>"
            "Upload an Excel file with just two columns: <strong>Name</strong> and <strong>Roll No</strong>. "
            "Department, Program, Admission Year, and Email are all auto-derived from each roll number.</p>",
            unsafe_allow_html=True
        )

        tmpl_buf = make_excel_template(["Name", "Roll No"], sample_row={"Name": "Aditi Sharma", "Roll No": "EE23BT003"})
        st.download_button(
            "⬇ Download Excel Template",
            data=tmpl_buf,
            file_name="student_bulk_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        bulk_stu_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"], key="bulk_stu_upload")

        if bulk_stu_file is not None:
            try:
                raw_df = pd.read_excel(bulk_stu_file)
            except Exception as ex:
                st.error(f"Could not read the Excel file: {ex}")
                raw_df = None

            if raw_df is not None:
                name_col = find_col(raw_df, ["name", "student name", "student_name", "full name", "full_name"])
                roll_col = find_col(raw_df, ["roll no", "roll_no", "rollno", "roll number", "student id", "student_id"])

                if not name_col or not roll_col:
                    st.error(
                        f"Couldn't detect the required columns. Found: {list(raw_df.columns)}. "
                        "Expecting a 'Name' column and a 'Roll No' column."
                    )
                else:
                    existing_ids = set(students_df[sid_col_new].astype(str).str.upper()) \
                        if not students_df.empty and sid_col_new in students_df.columns else set()
                    file_seen = set()
                    parsed_rows = []
                    for idx, row in raw_df.iterrows():
                        roll_raw = str(row[roll_col]).strip() if pd.notna(row[roll_col]) else ""
                        name_raw = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
                        roll_up = roll_raw.upper()
                        rec = {"Row": idx + 2, "Name": name_raw, "Roll No": roll_up}

                        if not roll_raw:
                            rec["Status"] = "Skipped — empty Roll No"
                        elif not name_raw:
                            rec["Status"] = "Skipped — empty Name"
                        else:
                            parsed = parse_roll_no(roll_up)
                            if parsed is None:
                                rec["Status"] = "Error — unrecognized Roll No format"
                            elif roll_up in existing_ids:
                                rec["Status"] = "Skipped — already exists in database"
                            elif roll_up in file_seen:
                                rec["Status"] = "Skipped — duplicate in file"
                            else:
                                rec.update({
                                    "Dept": parsed["dept"],
                                    "Program": parsed["program"],
                                    "Admission Year": parsed["year"],
                                    "Email": parsed["email"],
                                })
                                rec["Status"] = "Ready"
                                file_seen.add(roll_up)
                        parsed_rows.append(rec)

                    preview_df = pd.DataFrame(parsed_rows)
                    st.dataframe(preview_df, use_container_width=True)

                    ready_count = int((preview_df["Status"] == "Ready").sum())
                    st.write(f"**{ready_count}** of **{len(preview_df)}** row(s) ready to insert.")

                    if ready_count > 0 and st.button(f"📥 Insert {ready_count} Student(s)", type="primary", key="bulk_stu_insert"):
                        to_insert = [
                            {
                                sid_col_new: rec["Roll No"],
                                "name": rec["Name"],
                                "dept": rec["Dept"],
                                "program": rec["Program"],
                                "admission_year": int(rec["Admission Year"]),
                                "email": rec["Email"],
                            }
                            for rec in parsed_rows if rec["Status"] == "Ready"
                        ]
                        try:
                            result = supabase.table("students").insert(to_insert).execute()
                            if result.data:
                                st.success(f"✅ Inserted {len(result.data)} student(s) successfully.")
                                fetch_table.clear()
                                st.rerun()
                            else:
                                st.error("Insert failed. No data returned from Supabase.")
                        except Exception as ex:
                            st.error(f"Error inserting students: {ex}")


    # ──────────────────────────────────────────────────────────────────────────
    # TAB PROF — REGISTER NEW PROFESSOR
    # ──────────────────────────────────────────────────────────────────────────
    with tab_prof:
        st.markdown('<div class="sec-header">Register New Professor</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#999;font-size:0.85rem;margin-bottom:1rem;'>"
            "Fill in the details below to add a faculty member. Professor ID must be unique.</p>",
            unsafe_allow_html=True
        )

        pid_col_new = next((c for c in ["prof_id", "id"] if c in profs_df.columns), "prof_id") if not profs_df.empty else "prof_id"

        with st.form("add_prof_form", clear_on_submit=True):
            pc1, pc2 = st.columns(2)
            with pc1:
                new_prof_id = st.text_input("Professor ID *", placeholder="e.g. PROF001")
                new_prof_name = st.text_input("Full Name *", placeholder="e.g. Dr. Rohan Mehta")
            with pc2:
                dept_options_p = {}
                if not departments_df.empty and "dept_code" in departments_df.columns:
                    dnm_col_p = next((c for c in ["dept_name", "name"] if c in departments_df.columns), None)
                    for _, dr in departments_df.iterrows():
                        label = f"{dr[dnm_col_p]} ({dr['dept_code']})" if dnm_col_p else str(dr["dept_code"])
                        dept_options_p[label] = str(dr["dept_code"])
                if not dept_options_p:
                    dept_options_p = {f"{v} ({k})": k for k, v in DEPT_MAP.items()}
                new_prof_dept_label = st.selectbox("Department *", options=list(dept_options_p.keys()))
                new_prof_dept = dept_options_p[new_prof_dept_label]
                new_prof_email = st.text_input("Email (optional)", placeholder="e.g. rohan.mehta@iitdh.ac.in")

            prof_submitted = st.form_submit_button("🧑‍🏫 Add Professor", use_container_width=True, type="primary")

        if prof_submitted:
            errors = []
            if not new_prof_id.strip():
                errors.append("Professor ID is required.")
            if not new_prof_name.strip():
                errors.append("Full Name is required.")
            if not profs_df.empty and pid_col_new in profs_df.columns and \
               new_prof_id.strip() in profs_df[pid_col_new].astype(str).values:
                errors.append(f"Professor ID **{new_prof_id.strip()}** already exists.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                payload = {
                    pid_col_new: new_prof_id.strip(),
                    "name": new_prof_name.strip(),
                    "dept": new_prof_dept,
                }
                if new_prof_email.strip():
                    payload["email"] = new_prof_email.strip()
                try:
                    result = supabase.table("profs").insert(payload).execute()
                    if result.data:
                        st.success(f"✅ Professor **{new_prof_name.strip()} ({new_prof_id.strip()})** added successfully!")
                        fetch_table.clear()
                    else:
                        st.error("Insert failed. No data returned from Supabase.")
                except Exception as ex:
                    st.error(f"Error adding professor: {ex}")

        st.markdown('<div class="sec-header">Existing Professors</div>', unsafe_allow_html=True)
        if not profs_df.empty:
            st.dataframe(clean(add_fingerprint_column(profs_df.copy())), use_container_width=True)
        else:
            st.info("No professors in database yet.")


    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1 — ADD COURSE
    # ──────────────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="sec-header">Add New Course</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#999;font-size:0.85rem;margin-bottom:1rem;'>"
            "Fill in the details below. Course Code must be unique.</p>",
            unsafe_allow_html=True
        )
    
        with st.form("add_course_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                new_code = st.text_input(
                    "Course Code *",
                    placeholder="e.g. CS301",
                    help="Unique identifier like CS301, EE202"
                )
                new_name = st.text_input(
                    "Course Name *",
                    placeholder="e.g. Data Structures & Algorithms"
                )
            with fc2:
                # Build prof options from profs table
                prof_options = {}
                if not profs_df.empty:
                    pid_col = next((c for c in ["prof_id", "id"] if c in profs_df.columns), None)
                    pnm_col = next((c for c in ["name", "prof_name", "full_name"] if c in profs_df.columns), None)
                    if pid_col and pnm_col:
                        for _, pr in profs_df.iterrows():
                            prof_options[f"{pr[pnm_col]} ({pr[pid_col]})"] = str(pr[pid_col])
    
                if prof_options:
                    selected_prof_label = st.selectbox(
                        "Professor *",
                        options=list(prof_options.keys()),
                        help="Select the professor who will teach this course"
                    )
                    selected_prof_id = prof_options[selected_prof_label]
                else:
                    st.warning("No professors found in the database. Please add professors first.")
                    selected_prof_id = st.text_input("Professor ID (manual)", placeholder="e.g. PROF001")
                    selected_prof_label = selected_prof_id
    
                # Department field
                dept_options2 = ["CS", "EE", "MC", "ME", "CH", "CE", ""]
                new_dept = st.selectbox("Department (optional)", options=dept_options2, index=len(dept_options2)-1)
    
            submitted = st.form_submit_button("➕ Add Course", use_container_width=True, type="primary")
    
        if submitted:
            # Validate required fields
            errors = []
            if not new_code.strip():
                errors.append("Course Code is required.")
            if not new_name.strip():
                errors.append("Course Name is required.")
            if not selected_prof_id or not selected_prof_id.strip():
                errors.append("Professor is required.")
    
            # Check duplicate course code
            if not courses_df.empty and new_code.strip() in courses_df["course_code"].astype(str).values:
                errors.append(f"Course Code **{new_code.strip()}** already exists.")
    
            if errors:
                for e in errors:
                    st.error(e)
            else:
                now_str = datetime.now().isoformat()
                payload = {  
                    "course_code": new_code.strip().upper(),
                    "course_name": new_name.strip(),
                    "prof_id":     selected_prof_id.strip(),
                    "created_at":  now_str, # Fixes missing timestamp constraint
                    "updated_at":  now_str,
                }
                if new_dept:
                    payload["dept"] = new_dept
    
                try:
                    result = supabase.table("courses").insert(payload).execute()
                    if result.data:
                        st.success(
                            f"✅ Course **{new_code.strip().upper()} — {new_name.strip()}** "
                            f"added successfully with Prof. {selected_prof_label}!"
                        )
                        fetch_table.clear()
                    else:
                        st.error("Insert failed. No data returned from Supabase.")
                except Exception as ex:
                    st.error(f"Error adding course: {ex}")
    
        # Show current courses
        st.markdown('<div class="sec-header">Existing Courses</div>', unsafe_allow_html=True)
        if not courses_df.empty:
            display_courses = clean(courses_df.copy())
            # Resolve prof_id to name for display
            if not profs_df.empty:
                pid_col = next((c for c in ["prof_id", "id"] if c in profs_df.columns), None)
                pnm_col = next((c for c in ["name", "prof_name", "full_name"] if c in profs_df.columns), None)
                if pid_col and pnm_col and "prof_id" in display_courses.columns:
                    prof_id_to_name = dict(zip(profs_df[pid_col].astype(str), profs_df[pnm_col].astype(str)))
                    display_courses["professor"] = display_courses["prof_id"].astype(str).map(prof_id_to_name).fillna(display_courses["prof_id"])
            st.dataframe(display_courses, use_container_width=True)
        else:
            st.info("No courses in database yet.")


    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2 — ENROL STUDENT IN COURSE
    # ──────────────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="sec-header">Enrol Student in Course</div>', unsafe_allow_html=True)


        if students_df.empty:
            st.warning("No students found in the database.")
        elif courses_df.empty:
            st.warning("No courses found in the database.")
        else:
            # Build student options
            stu_options = {}
            name_col_s2 = next((c for c in ["first_name", "name", "student_name", "full_name"] if c in students_df.columns), None)
            last_col    = next((c for c in ["last_name"] if c in students_df.columns), None)
            sid_col     = stu_id_col_s or students_df.columns[0]


            for _, sr in students_df.iterrows():
                sid  = str(sr[sid_col])
                if name_col_s2 and last_col:
                    sname = f"{sr[name_col_s2]} {sr[last_col]}"
                elif name_col_s2:
                    sname = str(sr[name_col_s2])
                else:
                    sname = sid
                stu_options[f"{sname} ({sid})"] = sid


            # Build course options
            crs_options = {}
            name_col_c2 = next((c for c in ["course_name", "name", "title"] if c in courses_df.columns), None)
            for _, cr in courses_df.iterrows():
                ccode = str(cr["course_code"])
                cname = str(cr[name_col_c2]) if name_col_c2 else ccode
                crs_options[f"{ccode} — {cname}"] = ccode


            with st.form("enrol_student_form", clear_on_submit=True):
                enrol_stu_label = st.selectbox("Select Student *", options=list(stu_options.keys()))
                enrol_crs_label = st.selectbox("Select Course *",  options=list(crs_options.keys()))
                enrol_submitted = st.form_submit_button("📋 Enrol Student", use_container_width=True, type="primary")


            if enrol_submitted:
                enrol_stu_id  = stu_options[enrol_stu_label]
                enrol_crs_code = crs_options[enrol_crs_label]


                # Check if already enrolled
                already = False
                if not enrollments_df.empty and "student_id" in enrollments_df.columns and "course_code" in enrollments_df.columns:
                    already = (
                        (enrollments_df["student_id"].astype(str) == enrol_stu_id) &
                        (enrollments_df["course_code"].astype(str) == enrol_crs_code)
                    ).any()


                if already:
                    st.warning(f"⚠ **{enrol_stu_label}** is already enrolled in **{enrol_crs_label}**.")
                else:
                    try:
                        result = supabase.table("course_enrollments").insert({
                            "student_id":  enrol_stu_id,
                            "course_code": enrol_crs_code,
                            "status":      "active"
                        }).execute()
                        if result.data:
                            st.success(f"✅ **{enrol_stu_label}** successfully enrolled in **{enrol_crs_label}**!")
                            fetch_table.clear()
                        else:
                            st.error("Enrolment failed. No data returned.")
                    except Exception as ex:
                        st.error(f"Error enrolling student: {ex}")


            # Show current enrollments
            st.markdown('<div class="sec-header">Current Enrolments</div>', unsafe_allow_html=True)
            if not enrollments_df.empty:
                enrol_display = enrollments_df.copy()
                # Merge student names
                if not students_df.empty and sid_col in students_df.columns:
                    if name_col_s2 and last_col:
                        students_df["_display_name"] = students_df[name_col_s2].astype(str) + " " + students_df[last_col].astype(str)
                    elif name_col_s2:
                        students_df["_display_name"] = students_df[name_col_s2].astype(str)
                    else:
                        students_df["_display_name"] = students_df[sid_col].astype(str)
                    name_map = dict(zip(students_df[sid_col].astype(str), students_df["_display_name"]))
                    enrol_display["student_name"] = enrol_display["student_id"].astype(str).map(name_map)
                # Merge course names
                if not courses_df.empty and name_col_c2:
                    cname_map = dict(zip(courses_df["course_code"].astype(str), courses_df[name_col_c2].astype(str)))
                    enrol_display["course_name"] = enrol_display["course_code"].astype(str).map(cname_map)
                show_cols = [c for c in ["enrollment_id", "student_id", "student_name", "course_code", "course_name", "status", "enrolled_date"]
                             if c in enrol_display.columns]
                st.dataframe(enrol_display[show_cols], use_container_width=True)
            else:
                st.info("No enrolment records found.")


    # ──────────────────────────────────────────────────────────────────────────
    # TAB BULK ENROL — BULK COURSE ENROLLMENT VIA EXCEL
    # ──────────────────────────────────────────────────────────────────────────
    with tab_bulk_enrol:
        st.markdown('<div class="sec-header">Bulk Course Enrollment via Excel</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#999;font-size:0.85rem;margin-bottom:0.8rem;'>"
            "Pick a course, then upload an Excel file with a single <strong>Roll No</strong> column "
            "(a Name column is optional, shown only for reference). Students must already be registered.</p>",
            unsafe_allow_html=True
        )

        if courses_df.empty:
            st.warning("No courses found in the database. Add a course first.")
        elif students_df.empty:
            st.warning("No students found in the database. Register students first.")
        else:
            name_col_cb = next((c for c in ["course_name", "name", "title"] if c in courses_df.columns), None)
            crs_options_bulk = {}
            for _, cr in courses_df.iterrows():
                ccode = str(cr["course_code"])
                cname = str(cr[name_col_cb]) if name_col_cb else ccode
                crs_options_bulk[f"{ccode} — {cname}"] = ccode

            bulk_crs_label = st.selectbox("Select Course *", options=list(crs_options_bulk.keys()), key="bulk_enrol_course")
            bulk_crs_code = crs_options_bulk[bulk_crs_label]

            tmpl_buf2 = make_excel_template(["Name", "Roll No"], sample_row={"Name": "Aditi Sharma", "Roll No": "EE23BT003"})
            st.download_button(
                "⬇ Download Excel Template",
                data=tmpl_buf2,
                file_name="enrollment_bulk_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="bulk_enrol_tmpl"
            )

            bulk_enrol_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"], key="bulk_enrol_upload")

            if bulk_enrol_file is not None:
                try:
                    raw_df2 = pd.read_excel(bulk_enrol_file)
                except Exception as ex:
                    st.error(f"Could not read the Excel file: {ex}")
                    raw_df2 = None

                if raw_df2 is not None:
                    roll_col2 = find_col(raw_df2, ["roll no", "roll_no", "rollno", "roll number", "student id", "student_id"])
                    name_col2 = find_col(raw_df2, ["name", "student name", "student_name", "full name", "full_name"])

                    if not roll_col2:
                        st.error(f"Couldn't detect a Roll No column. Found: {list(raw_df2.columns)}")
                    else:
                        student_lookup = {
                            str(v).upper(): str(v) for v in students_df[stu_id_col_s].astype(str)
                        } if stu_id_col_s else {}
                        already_enrolled_ids = set()
                        if not enrollments_df.empty and "student_id" in enrollments_df.columns and "course_code" in enrollments_df.columns:
                            already_enrolled_ids = set(
                                enrollments_df[enrollments_df["course_code"].astype(str) == bulk_crs_code]["student_id"].astype(str).str.upper()
                            )

                        file_seen2 = set()
                        parsed_rows2 = []
                        for idx, row in raw_df2.iterrows():
                            roll_raw2 = str(row[roll_col2]).strip() if pd.notna(row[roll_col2]) else ""
                            roll_up2 = roll_raw2.upper()
                            disp_name = str(row[name_col2]).strip() if name_col2 and pd.notna(row[name_col2]) else ""
                            rec = {"Row": idx + 2, "Name": disp_name, "Roll No": roll_up2}

                            if not roll_raw2:
                                rec["Status"] = "Skipped — empty Roll No"
                            elif roll_up2 not in student_lookup:
                                rec["Status"] = "Error — student not found (register first)"
                            elif roll_up2 in already_enrolled_ids:
                                rec["Status"] = "Skipped — already enrolled"
                            elif roll_up2 in file_seen2:
                                rec["Status"] = "Skipped — duplicate in file"
                            else:
                                rec["Status"] = "Ready"
                                file_seen2.add(roll_up2)
                            parsed_rows2.append(rec)

                        preview_df2 = pd.DataFrame(parsed_rows2)
                        st.dataframe(preview_df2, use_container_width=True)

                        ready_count2 = int((preview_df2["Status"] == "Ready").sum())
                        st.write(f"**{ready_count2}** of **{len(preview_df2)}** row(s) ready to enrol into **{bulk_crs_code}**.")

                        if ready_count2 > 0 and st.button(f"📥 Enrol {ready_count2} Student(s)", type="primary", key="bulk_enrol_insert"):
                            to_insert2 = [
                                {
                                    "student_id": student_lookup[rec["Roll No"]],
                                    "course_code": bulk_crs_code,
                                    "status": "active",
                                }
                                for rec in parsed_rows2 if rec["Status"] == "Ready"
                            ]
                            try:
                                result2 = supabase.table("course_enrollments").insert(to_insert2).execute()
                                if result2.data:
                                    st.success(f"✅ Enrolled {len(result2.data)} student(s) into {bulk_crs_code}.")
                                    fetch_table.clear()
                                    st.rerun()
                                else:
                                    st.error("Enrolment failed. No data returned.")
                            except Exception as ex:
                                st.error(f"Error bulk enrolling students: {ex}")


    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3 — REMOVE STUDENT FROM COURSE
    # ──────────────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="sec-header">Remove Student from Course</div>', unsafe_allow_html=True)


        if enrollments_df.empty:
            st.info("No enrolment records found.")
        else:
            # Build searchable enrollment list
            enrol_display3 = enrollments_df.copy()
            sid_col3    = stu_id_col_s or students_df.columns[0] if not students_df.empty else "student_id"
            name_col_s3 = next((c for c in ["first_name", "name", "student_name"] if c in students_df.columns), None)
            last_col3   = next((c for c in ["last_name"] if c in students_df.columns), None)
            name_col_c3 = next((c for c in ["course_name", "name", "title"] if c in courses_df.columns), None)


            if not students_df.empty:
                if name_col_s3 and last_col3:
                    students_df["_dn3"] = students_df[name_col_s3].astype(str) + " " + students_df[last_col3].astype(str)
                elif name_col_s3:
                    students_df["_dn3"] = students_df[name_col_s3].astype(str)
                else:
                    students_df["_dn3"] = students_df[sid_col3].astype(str)
                nm3 = dict(zip(students_df[sid_col3].astype(str), students_df["_dn3"]))
                enrol_display3["student_name"] = enrol_display3["student_id"].astype(str).map(nm3).fillna(enrol_display3["student_id"])


            if not courses_df.empty and name_col_c3:
                cn3 = dict(zip(courses_df["course_code"].astype(str), courses_df[name_col_c3].astype(str)))
                enrol_display3["course_name"] = enrol_display3["course_code"].astype(str).map(cn3).fillna(enrol_display3["course_code"])


            # Search within enrollments
            rem_search = st.text_input("🔍 Filter by student name, student ID, or course code", key="rem_search")
            filtered_enrol = enrol_display3.copy()
            if rem_search:
                q3 = rem_search.lower()
                filtered_enrol = filtered_enrol[
                    filtered_enrol.astype(str).apply(lambda x: x.str.lower().str.contains(q3)).any(axis=1)
                ]


            show_cols3 = [c for c in ["enrollment_id", "student_id", "student_name", "course_code", "course_name", "status"]
                          if c in filtered_enrol.columns]


            st.markdown(
                f"<p style='color:#999;font-size:0.85rem;margin-bottom:0.4rem;'>"
                f"Showing <strong>{len(filtered_enrol)}</strong> enrolment(s). Select a row to remove.</p>",
                unsafe_allow_html=True
            )


            rem_event = st.dataframe(
                filtered_enrol[show_cols3].reset_index(drop=True),
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row",
                key="rem_enrol_table"
            )


            rem_selected = rem_event.selection.rows if rem_event and hasattr(rem_event, "selection") else []


            if rem_selected:
                sel_enrol_row = filtered_enrol[show_cols3].reset_index(drop=True).iloc[rem_selected[0]]
                eid      = sel_enrol_row.get("enrollment_id", None)
                rem_sid  = sel_enrol_row.get("student_id", "—")
                rem_sname= sel_enrol_row.get("student_name", rem_sid)
                rem_ccode= sel_enrol_row.get("course_code", "—")
                rem_cname= sel_enrol_row.get("course_name", rem_ccode)


                st.markdown(f"""
                <div class="edit-panel">
                  <div class="edit-panel-title">🗑 Remove Enrolment</div>
                  <p style='color:#ddd;font-size:0.9rem;'>
                    You are about to remove <strong>{rem_sname}</strong> ({rem_sid})
                    from <strong>{rem_ccode} — {rem_cname}</strong>.
                  </p>
                  <p style='color:#999;font-size:0.82rem;'>
                    This only removes the course enrolment. The student's attendance history
                    for this course will remain in the attendance log. The student will NOT
                    be deleted from the registry.
                  </p>
                </div>
                """, unsafe_allow_html=True)


                confirm_col1, confirm_col2 = st.columns([1, 3])
                with confirm_col1:
                    if st.button(
                        f"🗑 Remove from {rem_ccode}",
                        key="confirm_remove_enrolment",
                        type="primary",
                        use_container_width=True
                    ):
                        try:
                            if eid is not None:
                                supabase.table("course_enrollments").delete().eq("enrollment_id", int(eid)).execute()
                            else:
                                supabase.table("course_enrollments").delete()\
                                    .eq("student_id", rem_sid)\
                                    .eq("course_code", rem_ccode)\
                                    .execute()
                            st.success(
                                f"✅ **{rem_sname}** has been removed from **{rem_ccode} — {rem_cname}**."
                            )
                            fetch_table.clear()
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error removing enrolment: {ex}")


    # ──────────────────────────────────────────────────────────────────────────
    # TAB 4 — DELETE STUDENT FROM REGISTRY (double confirmation)
    # ──────────────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="sec-header">Delete Student from Registry</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="danger-zone">
          <p style='color:#f87171;font-size:0.9rem;font-weight:700;margin:0 0 0.5rem 0;'>
            ⚠ DANGER ZONE — Irreversible Action
          </p>
          <p style='color:#fca5a5;font-size:0.84rem;margin:0;'>
            Deleting a student will permanently remove them from the student registry,
            all course enrolments, and all attendance records. This action cannot be undone.
            You will be asked to confirm <strong>twice</strong>.
          </p>
        </div>
        """, unsafe_allow_html=True)


        if students_df.empty:
            st.info("No students found in the database.")
        else:
            # Step 1: Search and select student
            del_search = st.text_input("🔍 Search student by name or ID", key="del_search")
            del_df = students_df.copy()
            if del_search:
                del_df = del_df[
                    del_df.astype(str).apply(lambda x: x.str.lower().str.contains(del_search.lower())).any(axis=1)
                ]


            sid_col4    = stu_id_col_s or students_df.columns[0]
            name_col_s4 = next((c for c in ["first_name", "name", "student_name"] if c in students_df.columns), None)
            last_col4   = next((c for c in ["last_name"] if c in students_df.columns), None)


            del_display = clean(add_fingerprint_column(del_df.copy())).reset_index(drop=True)
            st.markdown(
                f"<p style='color:#999;font-size:0.85rem;margin-bottom:0.4rem;'>"
                f"Showing <strong>{len(del_display)}</strong> student(s). Select a row to delete.</p>",
                unsafe_allow_html=True
            )


            del_event = st.dataframe(
                del_display,
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row",
                key="del_stu_table"
            )


            del_selected = del_event.selection.rows if del_event and hasattr(del_event, "selection") else []


            if del_selected:
                del_row   = del_display.iloc[del_selected[0]]
                del_sid   = str(del_row.get(sid_col4, "—"))
                if name_col_s4 and last_col4:
                    del_name = f"{del_row.get(name_col_s4, '')} {del_row.get(last_col4, '')}".strip()
                elif name_col_s4:
                    del_name = str(del_row.get(name_col_s4, del_sid))
                else:
                    del_name = del_sid


                # Count courses enrolled and attendance records
                enrolled_count = 0
                att_count      = 0
                if not enrollments_df.empty and "student_id" in enrollments_df.columns:
                    enrolled_count = len(enrollments_df[enrollments_df["student_id"].astype(str) == del_sid])
                if not attendance_df.empty and stu_id_col_a and stu_id_col_a in attendance_df.columns:
                    att_count = len(attendance_df[attendance_df[stu_id_col_a].astype(str) == del_sid])


                st.markdown(f"""
                <div class="danger-zone">
                  <p style='color:#f87171;font-size:0.92rem;font-weight:700;margin:0 0 0.6rem 0;'>
                    Selected Student for Deletion
                  </p>
                  <p style='color:#ddd;font-size:0.9rem;margin:0 0 0.3rem 0;'>
                    <strong>Name:</strong> {del_name} &nbsp;|&nbsp;
                    <strong>ID:</strong> <code>{del_sid}</code>
                  </p>
                  <p style='color:#fca5a5;font-size:0.83rem;margin:0;'>
                    This will delete: <strong>{enrolled_count}</strong> course enrolment(s)
                    and <strong>{att_count}</strong> attendance record(s).
                  </p>
                </div>
                """, unsafe_allow_html=True)


                # ── CONFIRMATION 1 ────────────────────────────────────────────
                st.markdown("**Confirmation 1 of 2**")
                confirm1 = st.checkbox(
                    f"I understand that **{del_name} ({del_sid})** will be permanently removed from all courses and the registry.",
                    key="del_confirm1"
                )


                if confirm1:
                    # ── CONFIRMATION 2 ────────────────────────────────────────
                    st.markdown("**Confirmation 2 of 2**")
                    type_confirm = st.text_input(
                        f'Type the Student ID **{del_sid}** below to confirm deletion:',
                        key="del_confirm2_input",
                        placeholder=f"Type {del_sid} here"
                    )
                    confirm2_match = type_confirm.strip() == del_sid


                    if type_confirm and not confirm2_match:
                        st.warning("Student ID does not match. Please type it exactly.")


                    del_btn_disabled = not (confirm1 and confirm2_match)
                    if st.button(
                        f"❌ Permanently Delete {del_name}",
                        key="final_delete_btn",
                        type="primary",
                        disabled=del_btn_disabled,
                        use_container_width=True
                    ):
                        try:
                            # Delete from attendance (if no cascade)
                            try:
                                supabase.table("attendance").delete().eq("student_id", del_sid).execute()
                            except Exception:
                                pass  # cascade may handle it


                            # Delete from course_enrollments (if no cascade)
                            try:
                                supabase.table("course_enrollments").delete().eq("student_id", del_sid).execute()
                            except Exception:
                                pass  # cascade may handle it


                            # Delete the student record
                            supabase.table("students").delete().eq(sid_col4, del_sid).execute()


                            st.success(
                                f"✅ Student **{del_name} ({del_sid})** has been permanently deleted "
                                f"from the registry, all course enrolments, and all attendance records."
                            )
                            fetch_table.clear()
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error deleting student: {ex}")
