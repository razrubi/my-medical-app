import streamlit as st
import json
import os
import random

# --- הגדרות עמוד ---
st.set_page_config(page_title="Medical Prep App", page_icon="🏥", layout="centered")

# --- אתחול משתנים (Session State) ---
# משתנה למקור הנתונים (האריסון או סיכומים)
if 'data_source' not in st.session_state: st.session_state.data_source = None 

# משתני ניווט ולוגיקה
if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'quiz_finished' not in st.session_state: st.session_state.quiz_finished = False
if 'question_answered' not in st.session_state: st.session_state.question_answered = False
if 'last_choice' not in st.session_state: st.session_state.last_choice = None
if 'selected_system' not in st.session_state: st.session_state.selected_system = None
if 'selected_sub_system' not in st.session_state: st.session_state.selected_sub_system = None
if 'active_questions' not in st.session_state: st.session_state.active_questions = []

# --- פונקציה לטעינת נתונים לפי הבחירה ---
def load_data(source):
    if source == "harrison":
        filename = "harrison_questions.json"
    else:
        filename = "summary_questions.json"
        
    if not os.path.exists(filename):
        st.error(f"Error: File {filename} not found!")
        return []
        
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- פונקציית איפוס מלא (חזרה למסך הראשי) ---
def reset_app():
    st.session_state.data_source = None
    st.session_state.selected_system = None
    st.session_state.selected_sub_system = None
    st.session_state.score = 0
    st.session_state.current_q = 0
    st.session_state.quiz_finished = False
    st.session_state.question_answered = False
    st.rerun()

# --- פונקציה להתחלת מבחן ---
def start_quiz(questions_list):
    st.session_state.active_questions = questions_list
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.question_answered = False
    st.session_state.last_choice = None

# ==========================================
#              M A I N   A P P
# ==========================================

# כפתור חזרה לתפריט ראשי (מופיע תמיד למעלה אם נבחר משהו)
if st.session_state.data_source:
    col1, col2 = st.columns([4, 1])
    with col1:
        # כותרת דינמית לפי המקור
        title = "📘 Harrison's Prep" if st.session_state.data_source == "harrison" else "📝 My Summary Prep"
        st.title(title)
    with col2:
        if st.button("🏠 Main Menu"):
            reset_app()
else:
    st.title("🏥 Medical Prep Center")

st.markdown("---")

# ------------------------------------------
# שלב 0: מסך הכניסה הראשי (בחירת מקור)
# ------------------------------------------
if st.session_state.data_source is None:
    st.subheader("Choose your study material:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📘 Based on\nHarrison's", use_container_width=True):
            st.session_state.data_source = "harrison"
            st.rerun()
            
    with col2:
        if st.button("📝 Based on\nMy Summaries", use_container_width=True):
            st.session_state.data_source = "summary"
            st.rerun()

# ------------------------------------------
# מכאן והלאה - הלוגיקה פועלת על בסיס המקור שנבחר
# ------------------------------------------
else:
    # טעינת השאלות מהקובץ המתאים
    all_questions = load_data(st.session_state.data_source)
    
    # ------------------------------------------
    # שלב 1: בחירת מערכת (System)
    # ------------------------------------------
    if st.session_state.selected_system is None:
        if not all_questions:
            st.warning("No questions found in this file.")
            st.stop()
            
        st.subheader("Select a System:")
        systems = sorted(list(set([q['system'] for q in all_questions])))
        
        cols = st.columns(2)
        for i, system in enumerate(systems):
            if cols[i % 2].button(f"📂 {system}", use_container_width=True):
                st.session_state.selected_system = system
                st.rerun()

    # ------------------------------------------
    # שלב 2: בחירת תת-נושא (Sub-System) או Random Mix
    # ------------------------------------------
    elif st.session_state.selected_sub_system is None:
        # כפתור חזרה לבחירת מערכות
        if st.button("🔙 Back to Systems"):
            st.session_state.selected_system = None
            st.rerun()
            
        st.subheader(f"System: {st.session_state.selected_system}")
        st.write("Choose a mode:")
        
        # סינון שאלות לנושא הנוכחי
        system_qs = [q for q in all_questions if q['system'] == st.session_state.selected_system]
        
        # כפתור המיקס הגדול
        if st.button("🎲 Random Mix (All Topics)", use_container_width=True, type="primary"):
            mixed_qs = system_qs.copy()
            random.shuffle(mixed_qs)
            st.session_state.selected_sub_system = "Random Mix"
            start_quiz(mixed_qs)
            st.rerun()

        st.write("**Or select a specific sub-topic:**")
        
        # רשימת תתי-נושאים (אם אין תת-נושא בקובץ, נקרא לזה General)
        sub_systems = sorted(list(set([q.get('sub_system', 'General Topics') for q in system_qs])))
        
        for sub in sub_systems:
            if st.button(f"📑 {sub}", use_container_width=True):
                sub_qs = [q for q in system_qs if q.get('sub_system', 'General Topics') == sub]
                st.session_state.selected_sub_system = sub
                start_quiz(sub_qs)
                st.rerun()

    # ------------------------------------------
    # שלב 3: המבחן עצמו (Quiz Interface)
    # ------------------------------------------
    else:
        questions = st.session_state.active_questions
        
        if not questions:
            st.error("No questions found.")
        elif st.session_state.quiz_finished:
            st.balloons()
            st.success(f"🎉 Finished! Score: {st.session_state.score} / {len(questions)}")
            
            col_end1, col_end2 = st.columns(2)
            with col_end1:
                if st.button("Practice Again 🔄", use_container_width=True):
                    start_quiz(questions) # איפוס לאותו סט שאלות
                    st.rerun()
            with col_end2:
                if st.button("Back to Menu 🔙", use_container_width=True):
                    st.session_state.selected_sub_system = None
                    st.rerun()
        else:
            # שליפת השאלה
            q_data = questions[st.session_state.current_q]
            
            # כותרת קטנה עם המיקום
            sub_title = st.session_state.selected_sub_system
            st.caption(f"{st.session_state.selected_system} > {sub_title} | Q {st.session_state.current_q + 1}/{len(questions)}")
            st.progress((st.session_state.current_q) / len(questions))
            
            st.subheader(q_data['question'])

            # --- טופס תשובה ---
            if not st.session_state.question_answered:
                with st.form(key=f'quiz_form_{st.session_state.current_q}'):
                    user_choice = st.radio("Choose answer:", q_data['options'], index=None)
                    submit = st.form_submit_button("Check Answer")
                    
                    if submit:
                        if user_choice:
                            st.session_state.question_answered = True
                            st.session_state.last_choice = user_choice
                            if user_choice == q_data['options'][q_data['correct_index']]:
                                st.session_state.score += 1
                            st.rerun()
                        else:
                            st.warning("Please select an option.")
            else:
                # --- אחרי מענה ---
                correct_ans = q_data['options'][q_data['correct_index']]
                
                # הצגת בחירת המשתמש
                if st.session_state.last_choice == correct_ans:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {correct_ans}")
                
                # הצגת הסבר
                st.info(f"**Explanation:**\n\n{q_data['explanation']}")
                
                # הצגת מקור (אם קיים בקובץ)
                if 'source_page' in q_data:
                    st.caption(f"📖 Source: {q_data['source_page']}")

                # כפתור הבא
                if st.button("Next Question ➡️", type="primary"):
                    st.session_state.question_answered = False
                    if st.session_state.current_q + 1 < len(questions):
                        st.session_state.current_q += 1
                    else:
                        st.session_state.quiz_finished = True
                    st.rerun()
