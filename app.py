
import streamlit as st                   
import asyncio        
import datetime                       
from memory import remember, recall, improve, forget 
from dotenv import load_dotenv          

import os
st.write("DEBUG - Groq key ends with:", os.getenv("GROQ_API_KEY", "NOT SET")[-6:])

load_dotenv()
from memory import remember, recall, improve, forget, add_goal, check_due_reminders, mark_reminder_shown, delete_goal, load_goals, toggle_goal_completed, load_data, get_company_insight
due_reminders = check_due_reminders()
if due_reminders:
    for index, goal in due_reminders:
        st.warning(f"🔔 Reminder: **{goal['title']}** — started {goal['start_date']}. {goal['description']}")
        if st.button(f"Mark as seen", key=f"dismiss_{index}"):
            mark_reminder_shown(index)
            st.rerun()

st.set_page_config(
    page_title="Placement Pulse",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; }
    
    h1, h2, h3 { font-weight: 500 !important; letter-spacing: -0.02em; }
    
    .stButton button {
        border-radius: 8px;
        border: 0.5px solid #2c2c3a;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton button:hover { border-color: #7F77DD; color: #AFA9EC; }
    
    .stButton button[kind="primary"] {
        background-color: #534AB7;
        border: none;
    }
    .stButton button[kind="primary"]:hover { background-color: #7F77DD; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox > div, .stNumberInput input, .stDateInput input {
        border-radius: 8px !important;
        border: 0.5px solid #2c2c3a !important;
        background-color: #111118 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0d0d14;
        border-right: 0.5px solid #1e1e2e;
    }
    
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: 500; }
    [data-testid="stMetricLabel"] { font-size: 13px; color: #888780; }
    
    .stAlert { border-radius: 10px; }
    
    [data-testid="stExpander"] {
        border-radius: 10px;
        border: 0.5px solid #1e1e2e;
        background-color: #111118;
    }
 .hero-card {
        background: linear-gradient(135deg, #15151f 0%, #1a1a2e 100%);
        border: 0.5px solid #2c2c3a;
        border-radius: 16px;
        padding: 64px 32px;
        margin-bottom: 24px;
        text-align: center;
    }
    .hero-title {
        font-family: 'Georgia', 'Times New Roman', serif !important;
        font-size: 56px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        margin: 0 !important;
        letter-spacing: 0.03em !important;
        line-height: 1.1 !important;
    }
    .hero-sub {
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 1px;
        font-style: italic;
        color: #AFA9EC;
        margin-top: 10px;
    }
    .section-label {
        font-size: 11px;
        color: #5F5E5A;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <p class="hero-title">Placement Pulse</p>
    <p class="hero-sub">An AI that never forgets your placement journey</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Go to",
    ["📝 Log Application", "💬 Ask Anything", "📊 Dashboard", "🎯 Goals", "🗑️ Archive"],
    label_visibility="collapsed",
    key="main_navigation"
)

if page == "📝 Log Application":
    st.header("Enter a new placement details")
    st.write("Fill in the details below and save to memory.")

    company = st.text_input("Company name" )
    round_name = st.text_input("Round" )
    date = st.date_input("Date of round")   
    questions = st.text_area(
        "Questions asked",
        height=150                     
    )

    outcome = st.selectbox(
        "Outcome",
        ["Cleared ", "Rejected ", "Waiting ", "No Response "]
    )

    # st.button() creates a clickable button, returns True when clicked
    if st.button("💾 Save to memory", type="primary"):
        # type="primary" makes it blue/highlighted

        if company and round_name and questions:
            
            entry = (
                f"Company: {company}. "
                f"Round: {round_name}. "
                f"Date: {date}. "
                f"Questions asked: {questions}. "
                f"Outcome: {outcome}."
            )
    

            with st.spinner("Saving ... (this take 20-30 seconds on first save)"):
               
                asyncio.run(remember(entry))
                
            st.success(f"✅ Saved {company} -> {round_name} ->{outcome}")

        else:
            st.warning("Please fill in Company, Round and Questions at minimum.")
 


elif page == "💬 Ask Anything":
    st.header("Ask your memory anything")
    st.write("This AI remembers every application you logged — even from past sessions.")

    st.info("""
    Try asking:
    - What did TCS ask me in the technical round?
    - Which topic did I fail at?
    - Which companies rejected me?
    - What was the outcome of my Infosys interview?
    """)
  

    question = st.text_input(
        "Your question"
    )

    if st.button("🔍 Ask", type="primary"):
        if question:
            with st.spinner("Searching..."):
                answers = asyncio.run(recall(question))

            st.subheader("Answer:")
            
            if answers:
                cols = st.columns(len(answers))
                for i, (col, entry) in enumerate(zip(cols, answers), 1):
                    with col:
                        company = entry.split("Company:")[1].split(".")[0].strip() if "Company:" in entry else "Unknown"
                        round_name = entry.split("Round:")[1].split(".")[0].strip() if "Round:" in entry else ""
                        date = entry.split("Date:")[1].split(".")[0].strip() if "Date:" in entry else ""
                        questions = entry.split("Questions asked:")[1].split("Outcome:")[0].strip() if "Questions asked:" in entry else ""
                        outcome = entry.split("Outcome:")[1].strip().rstrip(".") if "Outcome:" in entry else ""
                        
                        st.markdown(f"""
                        <div style="background: #111118; border: 0.5px solid #2c2c3a; border-radius: 12px; padding: 16px; height: 100%;">
                            <p style="font-size: 16px; font-weight: 500; color: #ffffff; margin: 0 0 4px 0;">{i}. {company}</p>
                            <p style="font-size: 12px; color: #888780; margin: 0 0 12px 0;">{round_name} · {date}</p>
                            <p style="font-size: 13px; color: #c2c0b6; margin: 0 0 8px 0;">{questions}</p>
                            <p style="font-size: 13px; color: #AFA9EC; font-weight: 500; margin: 0;">→ {outcome}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No matching entries found for that question.")
        else:
            st.warning("Please type a question first.")

elif page == "📊 Dashboard":
    st.markdown('<p class="section-label">Overview</p>', unsafe_allow_html=True)
    st.subheader("My placement dashboard")

    entries = load_data()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total applications", len(entries))
    with col2:
        cleared = sum(1 for e in entries if "Outcome: Cleared" in e)
        st.metric("Cleared", cleared)
    with col3:
        rejected = sum(1 for e in entries if "Outcome: Rejected" in e)
        st.metric("Rejected", rejected)
    with col4:
        waiting = sum(1 for e in entries if "Outcome: Waiting" in e)
        st.metric("Waiting", waiting)

    st.divider()
    st.markdown('<p class="section-label">Quick queries</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("All companies", use_container_width=True):
            entries = load_data()
            if entries:
                companies = []
                for e in entries:
                    if "Company:" in e:
                        company_name = e.split("Company:")[1].split(".")[0].strip()
                        companies.append(company_name)
                unique_companies = list(set(companies))
                st.write("Companies you've applied to:")
                for c in unique_companies:
                    st.write(f"• {c}")
            else:
                st.info("No applications logged yet.")

    with col2:
        if st.button("Cleared", use_container_width=True):
            entries = load_data()
            cleared = [e for e in entries if "Outcome: Cleared" in e]
            if cleared:
                companies = []
                for e in cleared:
                    if "Company:" in e:
                        company_name = e.split("Company:")[1].split(".")[0].strip()
                        companies.append(company_name)
                unique_companies = list(set(companies))
                st.write(f"You cleared {len(unique_companies)} companies:")
                for c in unique_companies:
                    st.write(f"• {c}")
            else:
                st.info("No cleared rounds yet.")

    with col3:
        if st.button("Weakest topics", use_container_width=True):
            entries = load_data()
            rejected = [e for e in entries if "Outcome: Rejected" in e]
            if rejected:
                topics = []
                for e in rejected:
                    if "Questions asked:" in e:
                        # extract text between "Questions asked:" and "Outcome:"
                        q = e.split("Questions asked:")[1].split("Outcome:")[0].strip()
                        topics.append(q)
                st.write("Topics asked in rounds you didn't clear:")
                for t in topics:
                    st.write(f"• {t}")
            else:
                st.info("No rejections logged yet — nothing to analyze.")

    with col4:
        if st.button("All rejections", use_container_width=True):
            entries = load_data()
            rejected = [e for e in entries if "Outcome: Rejected" in e]
            if rejected:
                companies = []
                for e in rejected:
                    if "Company:" in e:
                        company_name = e.split("Company:")[1].split(".")[0].strip()
                        companies.append(company_name)
                unique_companies = list(set(companies))
                st.write("Companies that rejected you:")
                for c in unique_companies:
                    st.write(f"• {c}")
            else:
                st.info("No rejections logged yet.")

    col1, col2, col3, col4, col5 = st.columns(5)
    # (update your existing col1-col4 line to include col5)
    
    with col5:
        company_for_insight = st.session_state.get("insight_company", "")
        insight_company = st.text_input("Company for AI insight", placeholder="e.g. TCS", key="insight_input")
        if st.button("Get AI insight", use_container_width=True):
            if insight_company:
                with st.spinner("Analyzing your history with this company..."):
                    insight = get_company_insight(insight_company)
                if insight:
                    st.markdown(f"""
                    <div style="background: #0f1620; border-left: 3px solid #4FC3F7; border-radius: 0 8px 8px 0; padding: 14px 18px; margin-top: 12px;">
                        <p style="font-size: 12px; color: #4FC3F7; font-weight: 500; margin: 0 0 6px 0;">AI MEMORY INSIGHT</p>
                        <p style="font-size: 14px; color: #c2c0b6; margin: 0;">{insight}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No graph data yet — graph builds in the background after you save entries. Try again in a moment.")
            else:
                st.warning("Enter a company name first")

elif page == "🎯 Goals":
    st.markdown('<p class="section-label">Stay accountable</p>', unsafe_allow_html=True)
    st.subheader("Set a goal reminder")
    st.write("Enter a goal — the app will remind you after a set number of days.")

    goal_title = st.text_input("Goal title")
    goal_desc = st.text_area("Why this goal matters")
    goal_date = st.date_input("Start date", value=datetime.date.today())
    remind_days = st.number_input("Remind me after how many days?", min_value=1, value=30)

    if st.button("Save goal", type="primary"):
        if goal_title:
            add_goal(goal_title, goal_desc, str(goal_date), remind_days)
            st.success(f"Goal saved! You'll be reminded on {goal_date + datetime.timedelta(days=remind_days)}")
        else:
            st.warning("Please enter a goal title")

    st.divider()
    st.subheader("Your active goals")

    goals = load_goals()
    if goals:
        for i, g in enumerate(goals):
            status_icon = "✅" if g.get("completed", False) else "🎯"
            with st.expander(f"{status_icon} {g['title']} — started {g['start_date']}"):
                st.write(g['description'])
                remind_date = datetime.datetime.strptime(g['start_date'], "%Y-%m-%d").date() + datetime.timedelta(days=g['remind_after_days'])
                st.caption(f"Reminder date: {remind_date}")

                completed = st.checkbox("Mark as completed", value=g.get("completed", False), key=f"complete_{i}")
                if completed != g.get("completed", False):
                    toggle_goal_completed(i, completed)
                    st.rerun()

                if st.button("Delete goal", key=f"del_{i}"):
                    delete_goal(i)
                    st.rerun()
    else:
        st.info("No goals set yet.")

    
elif page == "🗑️ Archive":
    st.header("Archive / Reset memory")
    st.write("This will permanently delete all saved placement data from memory.")

    st.warning("⚠️ This action cannot be undone. All your logged applications will be erased.")

    # two-step confirmation to prevent accidental deletion
    confirm = st.checkbox("Yes, I understand and want to clear all memory")
    # st.checkbox() shows a tick box — confirm is True if ticked, False if not

    if confirm:                                # only show button if checkbox is ticked
        if st.button("🗑️ Clear all memory", type="primary"):
            with st.spinner("Clearing memory..."):
                asyncio.run(forget("placement_data"))
            st.success("Memory cleared! You can start fresh now.")