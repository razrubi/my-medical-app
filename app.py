import streamlit as st
import json
import os
import random

# --- Page Config ---
st.set_page_config(page_title="Surviving Integrative Course", page_icon="🎓", layout="centered")

# --- Session State Initialization ---
if 'current_view' not in st.session_state: st.session_state.current_view = 'home'
if 'data_source' not in st.session_state: st.session_state.data_source = None 
if 'integrative_data' not in st.session_state: st.session_state.integrative_data = None

# Navigation State for Integrative Mode
if 'selected_cluster' not in st.session_state: st.session_state.selected_cluster = None
if 'selected_system' not in st.session_state: st.session_state.selected_system = None

# Quiz State
if 'active_questions' not in st.session_state: st.session_state.active_questions = []
if 'current_q_index' not in st.session_state: st.session_state.current_q_index = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'quiz_finished' not in st.session_state: st.session_state.quiz_finished = False
if 'question_answered' not in st.session_state: st.session_state.question_answered = False
if 'last_choice' not in st.session_state: st.session_state.last_choice = None

# --- CONSTANTS FOR AESTHETICS ---
# כאן הוספנו את החיידק 🦠
SYSTEM_CONFIG = {
    "Liver System": {"display_name": "Hepatology", "emoji": "🧪"},
    "Digestive System": {"display_name": "Digestive System", "emoji": "🥨"},
    "Infectious Diseases": {"display_name": "Infectious Diseases", "emoji": "🦠"}
}

def get_system_display(sys_key):
    """מחזיר שם ואימוג'י יפים, או ברירת מחדל אם לא מוגדר"""
    config = SYSTEM_CONFIG.get(sys_key, {"display_name": sys_key, "emoji": "🩺"})
    return config["emoji"], config["display_name"]

# --- Helper Functions ---

def load_json_file(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def reset_to_home():
    st.session_state.current_view = 'home'
    st.session_state.data_source = None
    st.session_state.selected_cluster = None
    st.session_state.selected_system = None
    st.session_state.active_questions = []
    st.session_state.quiz_finished = False

def start_quiz(questions_list):
    if not questions_list:
        st.error("No questions available for this selection.")
        return
    st.session_state.active_questions = questions_list
    st.session_state.current_q_index = 0
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.question_answered = False
    st.session_state.last_choice = None
    st.session_state.current_view = 'quiz_mode'
    st.rerun()

# --- THE SHARED QUIZ ENGINE 🧠 ---
def run_quiz_interface():
    st.button("❌ Exit Quiz", on_click=reset_to_home)
    
    questions = st.session_state.active_questions
    current_idx = st.session_state.current_q_index
    
    if st.session_state.quiz_finished:
        st.balloons()
        st.success(f"🎉 Finished! Score: {st.session_state.score} / {len(questions)}")
        
        col1, col2 = st.columns(2)
        if col1.button("Practice Again 🔄", use_container_width=True):
            start_quiz(questions)
        if col2.button("Back to Home 🏠", use_container_width=True):
            st.session_state.current_view = 'home'
            st.rerun()
        return

    # Progress Bar
    progress = (current_idx + 1) / len(questions)
    st.progress(progress, text=f"Question {current_idx + 1} of {len(questions)}")
    
    # Get Question Data
    q_data = questions[current_idx]
    
    st.markdown(f"### {q_data['question']}")
    
    # Check Answer Logic
    if not st.session_state.question_answered:
        with st.form(key=f"q_form_{current_idx}"):
            choice = st.radio("Select an answer:", q_data['options'], index=None, key=f"radio_{current_idx}")
            submit = st.form_submit_button("Check Answer")
            
            if submit:
                if choice:
                    st.session_state.question_answered = True
                    st.session_state.last_choice = choice
                    correct_ans = q_data['options'][q_data['correct_index']]
                    if choice == correct_ans:
                        st.session_state.score += 1
                    st.rerun()
                else:
                    st.warning("Please select an option.")
    else:
        # Feedback Display
        correct_ans = q_data['options'][q_data['correct_index']]
        if st.session_state.last_choice == correct_ans:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer is: {correct_ans}")
            
        if 'explanation' in q_data:
            st.info(f"**Explanation:** {q_data['explanation']}")
            
        if st.button("Next Question ➡️", type="primary"):
            st.session_state.question_answered = False
            if current_idx + 1 < len(questions):
                st.session_state.current_q_index += 1
            else:
                st.session_state.quiz_finished = True
            st.rerun()

# --- LOGIC: CLASSIC MODE ---
def render_classic_mode():
    st.button("⬅️ Back", on_click=reset_to_home)
    st.subheader("Based on Harrison's")
    
    filename = "harrison_questions.json" if st.session_state.data_source == "harrison" else "summary_questions.json"
    data = load_json_file(filename)
    
    if not data:
        st.warning(f"File {filename} not found. Please create it first.")
        return

    systems = sorted(list(set([q['system'] for q in data])))
    selected_sys = st.selectbox("Select System:", systems)
    
    if st.button("Start Random Quiz"):
        relevant_qs = [q for q in data if q['system'] == selected_sys]
        random.shuffle(relevant_qs)
        start_quiz(relevant_qs)

# --- LOGIC: INTEGRATIVE MODE 🚀 ---
def render_integrative_mode():
    if st.session_state.integrative_data is None:
        st.session_state.integrative_data = load_json_file("integrative_questions.json")
    
    data = st.session_state.integrative_data
    if not data:
        st.error("Could not load 'integrative_questions.json'")
        st.button("Back", on_click=reset_to_home)
        return

    # -- Level 1: Clusters --
    if st.session_state.selected_cluster is None:
        st.button("⬅️ Back Home", on_click=reset_to_home)
        st.header("Select Cluster")
        
        st.caption("Digestive, Hepatology, Hematology, Infectious Diseases")
        if st.button("Cluster 2", use_container_width=True):
            st.session_state.selected_cluster = "Cluster 2"
            st.rerun()
            
        st.button("Cluster 1 (Coming Soon)", disabled=True)
        st.button("Cluster 3 (Coming Soon)", disabled=True)
        return

    # -- Level 2: Systems --
    if st.session_state.selected_system is None:
        st.button("⬅️ Back to Clusters", on_click=lambda: setattr(st.session_state, 'selected_cluster', None))
        st.header(f"Systems in {st.session_state.selected_cluster}")
        
        cluster_data = data.get(st.session_state.selected_cluster, {}).get("systems", {})
        
        cols = st.columns(2)
        for i, sys_key in enumerate(cluster_data.keys()):
            # כאן קורה הקסם של החלפת השמות והאימוג'ים
            emoji, display_name = get_system_display(sys_key)
            
            with cols[i % 2]:
                if st.button(f"{emoji} {display_name}", use_container_width=True):
                    st.session_state.selected_system = sys_key
                    st.rerun()
        return

    # -- Level 3: Drawers & Topics --
    st.button("⬅️ Back to Systems", on_click=lambda: setattr(st.session_state, 'selected_system', None))
    
    # שימוש בשם התצוגה היפה גם לכותרת
    sys_key = st.session_state.selected_system
    _, display_name = get_system_display(sys_key)
    st.header(f"Drill Down: {display_name}")
    
    drawers = data[st.session_state.selected_cluster]["systems"][sys_key].get("drawers", {})
    
    for drawer_name, drawer_content in drawers.items():
        with st.container(border=True):
            st.subheader(f"🗄️ {drawer_name}")
            st.caption(drawer_content.get("description", ""))
            
            all_qs = []
            topics = drawer_content.get("content", {})
            for t_name, subtopics in topics.items():
                for sub_name, qs in subtopics.items():
                    all_qs.extend(qs)
            
            if st.button(f"Practice Full Drawer ({len(all_qs)} Qs)", key=f"all_{drawer_name}"):
                start_quiz(all_qs)
            
            with st.expander("Or choose specific topic..."):
                for topic_name, subtopics in topics.items():
                    st.markdown(f"**{topic_name}**")
                    cols = st.columns(3)
                    for i, (sub_name, qs) in enumerate(subtopics.items()):
                        with cols[i%3]:
                            if st.button(f"{sub_name} ({len(qs)})", key=f"{drawer_name}_{sub_name}"):
                                start_quiz(qs)


# ==========================================
#               MAIN APP CONTROLLER
# ==========================================

if st.session_state.current_view == 'home':
    st.title("Surviving Integrative Course 🎓")
    st.write("Choose your study path:")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 Based on Harrison's", use_container_width=True):
            st.session_state.current_view = 'classic_mode'
            st.session_state.data_source = 'harrison' 
            st.rerun()
    with c2:
        if st.button("🔗 Integrative Course", use_container_width=True):
            st.session_state.current_view = 'integrative_mode'
            st.rerun()

elif st.session_state.current_view == 'classic_mode':
    render_classic_mode()

elif st.session_state.current_view == 'integrative_mode':
    render_integrative_mode()

elif st.session_state.current_view == 'quiz_mode':
    run_quiz_interface()
