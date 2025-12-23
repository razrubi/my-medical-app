import streamlit as st
import json
import os

# --- הגדרות עמוד ---
st.set_page_config(page_title="Medical Prep App", page_icon="🩺", layout="centered")

# --- פונקציה לטעינת שאלות ---
def load_questions(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- ניהול זיכרון (Session State) ---
if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'quiz_finished' not in st.session_state: st.session_state.quiz_finished = False
if 'question_answered' not in st.session_state: st.session_state.question_answered = False
if 'last_choice' not in st.session_state: st.session_state.last_choice = None

# משתנים חדשים לניהול הניווט
if 'selected_source' not in st.session_state: st.session_state.selected_source = None # 'harrison' or 'summary'
if 'selected_system' not in st.session_state: st.session_state.selected_system = None

# --- כותרת ראשית ---
st.title("🩺 MedSchool Master")
st.markdown("---")

# --- לוגיקה 1: בחירת מקור הלימוד (מסך הבית) ---
if st.session_state.selected_source is None:
    st.subheader("Choose Your Learning Source:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📘 Harrison's Principles", use_container_width=True):
            st.session_state.selected_source = "harrison_questions.json"
            st.rerun()
            
    with col2:
        if st.button("📝 My Personal Summary", use_container_width=True):
            st.session_state.selected_source = "summary_questions.json"
            st.rerun()

# --- לוגיקה 2: בחירת נושא (אחרי שבחרנו מקור) ---
elif st.session_state.selected_system is None:
    # טוענים את השאלות מהמקור שנבחר
    all_questions = load_questions(st.session_state.selected_source)
    
    if not all_questions:
        st.error("Error: Could not load questions. Check if JSON file exists.")
        if st.button("Back"):
            st.session_state.selected_source = None
            st.rerun()
    else:
        # כפתור חזרה למסך הראשי
        if st.button("🏠 Change Source"):
            st.session_state.selected_source = None
            st.rerun()

        st.subheader("Select a Topic:")
        
        # חילוץ רשימת הנושאים
        systems = sorted(list(set([q.get('system', 'General') for q in all_questions])))
        
        cols = st.columns(2)
        for i, system in enumerate(systems):
            if cols[i % 2].button(f"🔬 {system}", use_container_width=True):
                st.session_state.selected_system = system
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.session_state.quiz_finished = False
                st.session_state.question_answered = False
                st.rerun()

# --- לוגיקה 3: המבחן עצמו ---
else:
    # טעינה וסינון שאלות
    all_questions = load_questions(st.session_state.selected_source)
    system_questions = [q for q in all_questions if q.get('system') == st.session_state.selected_system]
    
    # כפתור חזרה לבחירת נושאים
    if st.button("🔙 Back to Topics"):
        st.session_state.selected_system = None
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.quiz_finished = False
        st.session_state.question_answered = False
        st.rerun()

    if not system_questions:
        st.error("No questions found.")
    elif st.session_state.quiz_finished:
        st.balloons()
        st.success(f"🎉 Topic Finished! Score: {st.session_state.score} / {len(system_questions)}")
        if st.button("Practice Again 🔄"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.quiz_finished = False
            st.session_state.question_answered = False
            st.rerun()
    else:
        # הצגת השאלה
        q_data = system_questions[st.session_state.current_q]
        
        st.progress((st.session_state.current_q) / len(system_questions))
        st.caption(f"Topic: {st.session_state.selected_system} | Question {st.session_state.current_q + 1}/{len(system_questions)}")
        
        st.subheader(q_data['question'])

        # טופס תשובות
        if not st.session_state.question_answered:
            with st.form(key='quiz_form'):
                user_choice = st.radio("Choose answer:", q_data['options'], index=None)
                submit = st.form_submit_button("Check Answer")
                
                if submit and user_choice:
                    st.session_state.question_answered = True
                    st.session_state.last_choice = user_choice
                    if user_choice == q_data['options'][q_data['correct_index']]:
                        st.session_state.score += 1
                    st.rerun()
        else:
            # תוצאות
            correct_ans = q_data['options'][q_data['correct_index']]
            if st.session_state.last_choice == correct_ans:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Answer: {correct_ans}")
            
            st.info(f"**Explanation:**\n\n{q_data['explanation']}")
            
            # הצגת המקור (אם קיים)
            if 'source' in q_data:
                st.markdown(f"<small style='color: gray'>📖 Source: {q_data['source']}</small>", unsafe_allow_html=True)
            elif 'source_page' in q_data: # תמיכה לאחור בפורמט הקודם
                st.markdown(f"<small style='color: gray'>📖 Source: {q_data['source_page']}</small>", unsafe_allow_html=True)

            if st.button("Next ➡️", type="primary"):
                st.session_state.question_answered = False
                if st.session_state.current_q + 1 < len(system_questions):
                    st.session_state.current_q += 1
                else:
                    st.session_state.quiz_finished = True
                st.rerun()