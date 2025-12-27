import streamlit as st
import requests
import json
import re
from datetime import datetime

# Initialize session state
if 'flipped_cards' not in st.session_state:
    st.session_state.flipped_cards = set()
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'quiz_raw' not in st.session_state:
    st.session_state.quiz_raw = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'flashcards_data' not in st.session_state:
    st.session_state.flashcards_data = None
if 'study_guide_data' not in st.session_state:
    st.session_state.study_guide_data = None
if 'diagram_url' not in st.session_state:
    st.session_state.diagram_url = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'study_mode' not in st.session_state:
    st.session_state.study_mode = None

# Page config
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Dark theme with white text */
    .stApp {
        background-color: #0e1117;
    }
    
    .main-header {
        text-align: center;
        color: #ffffff !important;
        padding: 20px;
    }
    
    .subtitle {
        text-align: center;
        color: #b0b0b0 !important;
        font-size: 18px;
        margin-bottom: 30px;
    }
    
    /* Ensure all text is white/light */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    p, span, div, label {
        color: #ffffff !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Mode selection cards */
    .mode-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        border: 2px solid #3d3d5c;
        transition: all 0.3s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .mode-card:hover {
        border-color: #6366f1;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }
    
    .mode-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    .mode-title {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff !important;
        margin-bottom: 10px;
    }
    
    .mode-description {
        font-size: 14px;
        color: #a0a0a0 !important;
        line-height: 1.5;
    }
    
    /* Flashcard styles */
    .flashcard {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        border-radius: 15px;
        padding: 25px;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 1px solid #3d7ab5;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    
    .flashcard:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    }
    
    .flashcard-front {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
    }
    
    .flashcard-back {
        background: linear-gradient(135deg, #1a4731 0%, #2d7a4f 100%);
        border-color: #3db56a;
    }
    
    .flashcard-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
        opacity: 0.8;
        color: #a0c4e8 !important;
    }
    
    .flashcard-back .flashcard-label {
        color: #a0e8c4 !important;
    }
    
    .flashcard-content {
        font-size: 18px;
        font-weight: 500;
        color: #ffffff !important;
        line-height: 1.5;
    }
    
    /* Quiz styles */
    .quiz-question {
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #6366f1;
    }
    
    .quiz-question h4 {
        color: #ffffff !important;
        margin-bottom: 15px;
    }
    
    .correct-answer {
        background: linear-gradient(135deg, #1a4731 0%, #2d7a4f 100%) !important;
        border-left-color: #22c55e !important;
    }
    
    .incorrect-answer {
        background: linear-gradient(135deg, #4a1a1a 0%, #7a2d2d 100%) !important;
        border-left-color: #ef4444 !important;
    }
    
    /* Results box */
    .results-box {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        border: 2px solid #6366f1;
    }
    
    .score-display {
        font-size: 48px;
        font-weight: bold;
        color: #6366f1 !important;
        margin: 10px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #888888 !important;
        padding: 20px;
    }
    
    .footer p {
        color: #888888 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: transparent;
    }
    
    .stRadio label {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

def parse_quiz(quiz_text):
    """Parse quiz text into structured format"""
    questions = []
    q_pattern = r'Q\d+[:\.]?\s*'
    parts = re.split(q_pattern, quiz_text)
    
    for part in parts[1:]:
        if not part.strip():
            continue
            
        lines = part.strip().split('\n')
        question_text = ""
        options = {}
        correct_answer = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'correct' in line.lower() and 'answer' in line.lower():
                answer_match = re.search(r'[:\s]+([A-D])\b', line, re.IGNORECASE)
                if answer_match:
                    correct_answer = answer_match.group(1).upper()
                continue
            
            option_match = re.match(r'^\(?([A-D])\)?[\.\):]?\s*(.+)', line, re.IGNORECASE)
            if option_match:
                letter = option_match.group(1).upper()
                text = option_match.group(2).strip()
                options[letter] = text
            elif not options:
                question_text += line + " "
        
        if question_text and len(options) >= 2 and correct_answer:
            questions.append({
                'question': question_text.strip(),
                'options': options,
                'correct': correct_answer
            })
    
    return questions

def parse_flashcards(flashcards_text):
    """Parse flashcards text into structured format"""
    cards = []
    parts = re.split(r'CARD\s*\d*', flashcards_text, flags=re.IGNORECASE)
    
    for part in parts:
        if not part.strip():
            continue
        
        front_match = re.search(r'Front:\s*(.+?)(?=Back:|$)', part, re.DOTALL | re.IGNORECASE)
        back_match = re.search(r'Back:\s*(.+?)(?=Front:|CARD|$)', part, re.DOTALL | re.IGNORECASE)
        
        if front_match and back_match:
            front = front_match.group(1).strip()
            back = back_match.group(1).strip()
            if front and back:
                cards.append({'front': front, 'back': back})
    
    return cards

def reset_study_data():
    """Reset all study data for new generation"""
    st.session_state.quiz_data = None
    st.session_state.quiz_raw = None
    st.session_state.user_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.flipped_cards = set()
    st.session_state.flashcards_data = None
    st.session_state.study_guide_data = None
    st.session_state.diagram_url = None

def go_home():
    """Return to home page"""
    st.session_state.page = "home"
    st.session_state.study_mode = None
    reset_study_data()

# ============== HOME PAGE ==============
if st.session_state.page == "home":
    st.markdown("<h1 class='main-header'>📚 AI Study Buddy</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Generate quizzes, flashcards, and study guides for any topic!<br>Choose a study mode to get started.</p>", unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='mode-card'>
            <div class='mode-icon'>📝</div>
            <div class='mode-title'>Quiz Mode</div>
            <div class='mode-description'>Test your knowledge with AI-generated multiple choice questions. Get instant feedback on your answers!</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Quiz Mode", key="quiz_btn", use_container_width=True):
            st.session_state.page = "study"
            st.session_state.study_mode = "Quiz"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class='mode-card'>
            <div class='mode-icon'>🎴</div>
            <div class='mode-title'>Flashcards Mode</div>
            <div class='mode-description'>Create flip cards for effective memorization. Click to reveal answers and track your progress!</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Flashcards Mode", key="flash_btn", use_container_width=True):
            st.session_state.page = "study"
            st.session_state.study_mode = "Flashcards"
            st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class='mode-card'>
            <div class='mode-icon'>📖</div>
            <div class='mode-title'>Study Guide Mode</div>
            <div class='mode-description'>Get comprehensive study guides with key concepts, definitions, and practice tips!</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Study Guide Mode", key="guide_btn", use_container_width=True):
            st.session_state.page = "study"
            st.session_state.study_mode = "Study Guide"
            st.rerun()
    
    with col4:
        st.markdown("""
        <div class='mode-card'>
            <div class='mode-icon'>🚀</div>
            <div class='mode-title'>All-In-One Mode</div>
            <div class='mode-description'>Generate everything at once! Quiz, flashcards, study guide, and visual diagram.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start All-In-One Mode", key="all_btn", use_container_width=True):
            st.session_state.page = "study"
            st.session_state.study_mode = "All Three"
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
        <div class='footer'>
            <p>Made with ❤️ for students everywhere</p>
            <p>Powered by Pollinations.AI | Free & Open Source</p>
        </div>
    """, unsafe_allow_html=True)

# ============== STUDY PAGE ==============
elif st.session_state.page == "study":
    study_mode = st.session_state.study_mode
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏠 Navigation")
        if st.button("← Back to Home", use_container_width=True):
            go_home()
            st.rerun()
        
        st.markdown("---")
        st.header("⚙️ Settings")
        st.markdown(f"**Current Mode:** {study_mode}")
        
        if study_mode in ["Quiz", "All Three"]:
            difficulty = st.select_slider("Quiz Difficulty", options=["Easy", "Medium", "Hard"])
            num_questions = st.slider("Number of Questions", 3, 10, 5)
        else:
            difficulty = "Medium"
            num_questions = 5
        
        if study_mode in ["Flashcards", "All Three"]:
            num_flashcards = st.slider("Number of Flashcards", 5, 20, 10)
        else:
            num_flashcards = 10
        
        generate_diagram = st.checkbox("Generate Study Diagram", value=True)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("Powered by **Pollinations.AI** 🌸")
    
    # Header
    mode_icons = {"Quiz": "📝", "Flashcards": "🎴", "Study Guide": "📖", "All Three": "🚀"}
    st.markdown(f"<h1 class='main-header'>{mode_icons.get(study_mode, '📚')} {study_mode} Mode</h1>", unsafe_allow_html=True)
    
    # Topic input
    topic = st.text_input("📖 Enter a topic to study:", placeholder="e.g., Photosynthesis, World War 2, Quadratic Equations")
    
    if st.button("🚀 Generate Study Materials", type="primary"):
        if not topic:
            st.warning("Please enter a topic first!")
        else:
            reset_study_data()
            st.session_state.current_topic = topic
            
            with st.spinner("🤖 AI is preparing your study materials..."):
                
                # Generate Quiz
                if study_mode in ["Quiz", "All Three"]:
                    try:
                        quiz_prompt = f"""Generate a {difficulty} difficulty quiz about {topic} with {num_questions} multiple choice questions.
                        
Format your response EXACTLY like this:
Q1: [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [A/B/C/D]

Q2: [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [A/B/C/D]

Continue for all {num_questions} questions."""
                        
                        response = requests.post(
                            "https://text.pollinations.ai/",
                            json={
                                "messages": [
                                    {"role": "system", "content": "You are a helpful educational assistant that creates clear, accurate study materials."},
                                    {"role": "user", "content": quiz_prompt}
                                ],
                                "model": "openai"
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            quiz_text = response.text
                            parsed = parse_quiz(quiz_text)
                            if parsed:
                                st.session_state.quiz_data = parsed
                            else:
                                st.session_state.quiz_raw = quiz_text
                    except Exception as e:
                        st.error(f"Error generating quiz: {str(e)}")
                
                # Generate Flashcards
                if study_mode in ["Flashcards", "All Three"]:
                    try:
                        flashcard_prompt = f"""Generate {num_flashcards} flashcards about {topic}.
                        
Format your response EXACTLY like this:
CARD 1
Front: [Question or term]
Back: [Answer or definition]

CARD 2
Front: [Question or term]
Back: [Answer or definition]

Continue for all {num_flashcards} flashcards."""
                        
                        response = requests.post(
                            "https://text.pollinations.ai/",
                            json={
                                "messages": [
                                    {"role": "system", "content": "You are a helpful educational assistant that creates clear, concise flashcards."},
                                    {"role": "user", "content": flashcard_prompt}
                                ],
                                "model": "openai"
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            st.session_state.flashcards_data = parse_flashcards(response.text)
                    except Exception as e:
                        st.error(f"Error generating flashcards: {str(e)}")
                
                # Generate Study Guide
                if study_mode in ["Study Guide", "All Three"]:
                    try:
                        guide_prompt = f"""Create a comprehensive study guide about {topic}.

Include:
1. Key Concepts (3-5 main ideas)
2. Important Terms and Definitions
3. Summary/Overview
4. Practice Tips

Make it clear, organized, and easy to understand for students."""
                        
                        response = requests.post(
                            "https://text.pollinations.ai/",
                            json={
                                "messages": [
                                    {"role": "system", "content": "You are a helpful educational assistant that creates comprehensive study guides."},
                                    {"role": "user", "content": guide_prompt}
                                ],
                                "model": "openai"
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            st.session_state.study_guide_data = response.text
                    except Exception as e:
                        st.error(f"Error generating study guide: {str(e)}")
                
                # Generate Diagram
                if generate_diagram:
                    try:
                        diagram_prompt = f"educational diagram explaining {topic}, clear labels, simple illustration style, whiteboard drawing"
                        st.session_state.diagram_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(diagram_prompt)}?width=1024&height=768&model=flux&nologo=true"
                    except Exception as e:
                        st.error(f"Error generating diagram: {str(e)}")
                
                st.success("✅ Study materials generated successfully!")
                st.balloons()
                st.rerun()
    
    # ============== DISPLAY QUIZ ==============
    if st.session_state.quiz_data and study_mode in ["Quiz", "All Three"]:
        st.markdown("---")
        st.header("📝 Quiz")
        
        questions = st.session_state.quiz_data
        
        if not st.session_state.quiz_submitted:
            st.markdown(f"**Answer all {len(questions)} questions, then submit to see your results!**")
            
            for i, q in enumerate(questions):
                st.markdown(f"""
                <div class='quiz-question'>
                    <h4>Question {i + 1}: {q['question']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                options = [f"{letter}) {text}" for letter, text in sorted(q['options'].items())]
                selected = st.radio(
                    f"Select your answer for Question {i + 1}:",
                    options,
                    key=f"q_{i}",
                    index=None,
                    label_visibility="collapsed"
                )
                
                if selected:
                    st.session_state.user_answers[i] = selected[0]
            
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                answered = len(st.session_state.user_answers)
                total = len(questions)
                st.markdown(f"**Questions answered: {answered}/{total}**")
                
                if st.button("📊 Submit Quiz", type="primary", use_container_width=True):
                    if answered < total:
                        st.warning(f"Please answer all questions before submitting. You've answered {answered}/{total}.")
                    else:
                        st.session_state.quiz_submitted = True
                        st.rerun()
        
        else:
            correct_count = 0
            for i, q in enumerate(questions):
                user_answer = st.session_state.user_answers.get(i, "")
                is_correct = user_answer == q['correct']
                if is_correct:
                    correct_count += 1
                
                status_class = "correct-answer" if is_correct else "incorrect-answer"
                status_icon = "✅" if is_correct else "❌"
                
                st.markdown(f"""
                <div class='quiz-question {status_class}'>
                    <h4>{status_icon} Question {i + 1}: {q['question']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for letter, text in sorted(q['options'].items()):
                    if letter == q['correct']:
                        st.markdown(f"✅ **{letter}) {text}** *(Correct Answer)*")
                    elif letter == user_answer and not is_correct:
                        st.markdown(f"❌ ~~{letter}) {text}~~ *(Your Answer)*")
                    else:
                        st.markdown(f"{letter}) {text}")
            
            score_percentage = (correct_count / len(questions)) * 100
            
            st.markdown("---")
            st.markdown(f"""
            <div class='results-box'>
                <h2 style='color: #ffffff !important;'>📊 Quiz Results</h2>
                <div class='score-display'>{correct_count}/{len(questions)}</div>
                <p style='font-size: 24px; color: #b0b0b0 !important;'>{score_percentage:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            if score_percentage == 100:
                st.success("🎉 Perfect score! You've mastered this topic!")
            elif score_percentage >= 80:
                st.success("🌟 Great job! You have a strong understanding!")
            elif score_percentage >= 60:
                st.info("👍 Good effort! Review the questions you missed.")
            else:
                st.warning("📚 Keep studying! Review and try again.")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Retake Quiz", use_container_width=True):
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()
    
    elif st.session_state.quiz_raw and study_mode in ["Quiz", "All Three"]:
        st.markdown("---")
        st.header("📝 Quiz")
        st.markdown(st.session_state.quiz_raw)
    
    # ============== DISPLAY FLASHCARDS ==============
    if st.session_state.flashcards_data and study_mode in ["Flashcards", "All Three"]:
        st.markdown("---")
        st.header("🎴 Flashcards")
        
        cards = st.session_state.flashcards_data
        total_cards = len(cards)
        flipped_count = len(st.session_state.flipped_cards)
        
        progress = flipped_count / total_cards if total_cards > 0 else 0
        st.markdown(f"**Progress: {flipped_count}/{total_cards} cards flipped**")
        st.progress(progress)
        
        if st.button("🔄 Reset All Cards"):
            st.session_state.flipped_cards = set()
            st.rerun()
        
        cols = st.columns(2)
        for idx, card in enumerate(cards):
            with cols[idx % 2]:
                card_id = f"card_{idx}"
                is_flipped = card_id in st.session_state.flipped_cards
                
                if not is_flipped:
                    st.markdown(f"""
                    <div class='flashcard flashcard-front'>
                        <div class='flashcard-label'>Question / Term</div>
                        <div class='flashcard-content'>{card['front']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🔄 Flip Card", key=f"flip_{idx}"):
                        st.session_state.flipped_cards.add(card_id)
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class='flashcard flashcard-back'>
                        <div class='flashcard-label'>Answer / Definition</div>
                        <div class='flashcard-content'>{card['back']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"↩️ Flip Back", key=f"unflip_{idx}"):
                        st.session_state.flipped_cards.remove(card_id)
                        st.rerun()
    
    # ============== DISPLAY STUDY GUIDE ==============
    if st.session_state.study_guide_data and study_mode in ["Study Guide", "All Three"]:
        st.markdown("---")
        st.header("📖 Study Guide")
        st.markdown(st.session_state.study_guide_data)
    
    # ============== DISPLAY DIAGRAM ==============
    if st.session_state.diagram_url:
        st.markdown("---")
        st.header("🖼️ Study Diagram")
        st.image(st.session_state.diagram_url, caption=f"Visual Guide: {st.session_state.current_topic}", use_container_width=True)
        st.markdown(f"[Download Diagram]({st.session_state.diagram_url})")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div class='footer'>
            <p>Made with ❤️ for students everywhere</p>
            <p>Powered by Pollinations.AI | Free & Open Source</p>
        </div>
    """, unsafe_allow_html=True)

