import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="AI C Programming Tutor",
    page_icon="🤖",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def initialize_session_state():
    """Initialize all session state variables"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat"
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None

def create_user(name: str):
    """Create a new user"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/users", params={"name": name})
        if response.status_code == 200:
            return response.json()["user_id"]
    except Exception as e:
        st.error(f"Error creating user: {e}")
    return None

def get_user_profile(user_id: str):
    """Get user profile data"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/users/{user_id}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching user profile: {e}")
    return None

def send_message(message: str, user_id: str):
    """Send a chat message to the AI tutor"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": message, "user_id": user_id}
        )
        if response.status_code == 200:
            return response.json()["response"]
    except Exception as e:
        st.error(f"Error sending message: {e}")
    return None

def generate_quiz(topic: str, difficulty: int = 5, num_questions: int = 5):
    """Generate a quiz on a specific topic"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/quiz/{topic}",
            params={"difficulty": difficulty, "num_questions": num_questions}
        )
        if response.status_code == 200:
            return response.json().get("quiz", [])
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
    return None

def submit_quiz_score(user_id: str, topic: str, score: float):
    """Submit quiz score to backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/quiz/submit",
            json={
                "user_id": user_id,
                "topic": topic,
                "score": score,
                "timestamp": datetime.now().isoformat()
            }
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error submitting score: {e}")
        return False

def sidebar_navigation():
    """Create sidebar navigation and user management"""
    with st.sidebar:
        st.header("🎯 Navigation")
        
        # Page selection
        pages = ["Chat", "Quiz", "Progress", "Lessons"]
        st.session_state.current_page = st.selectbox(
            "Select Page", 
            pages, 
            index=pages.index(st.session_state.current_page)
        )
        
        st.divider()
        
        # User Profile Section
        st.header("👤 User Profile")
        
        if st.session_state.user_id is None:
            name = st.text_input("Enter your name:")
            if st.button("🚀 Start Learning", use_container_width=True):
                if name:
                    user_id = create_user(name)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.user_name = name
                        st.success(f"Welcome, {name}!")
                        st.rerun()
                else:
                    st.warning("Please enter your name!")
        else:
            # Display user info
            st.success(f"👋 Welcome, {st.session_state.user_name}!")
            
            # Get and display user profile
            if st.session_state.user_profile is None:
                st.session_state.user_profile = get_user_profile(st.session_state.user_id)
            
            if st.session_state.user_profile:
                profile = st.session_state.user_profile
                st.metric("Current Level", profile.get("current_level", 1))
                st.metric("Lessons Completed", len(profile.get("completed_lessons", [])))
                
                # Quiz scores summary
                quiz_scores = profile.get("quiz_scores", {})
                if quiz_scores:
                    avg_score = sum(quiz_scores.values()) / len(quiz_scores)
                    st.metric("Average Quiz Score", f"{avg_score:.1f}%")
            
            st.divider()
            
            if st.button("🔄 New Session", use_container_width=True):
                # Reset session
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

def chat_page():
    """Main chat interface"""
    st.title("💬 AI C Programming Tutor")
    st.markdown("Ask me anything about C programming!")
    
    if st.session_state.user_id:
        # Quick topic buttons
        st.markdown("### 🚀 Quick Topics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 Variables", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Explain variables in C"})
        with col2:
            if st.button("🔄 Loops", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "How do loops work in C?"})
        with col3:
            if st.button("📊 Arrays", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Explain arrays in C"})
        with col4:
            if st.button("⚡ Functions", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "How do functions work in C?"})
        
        st.divider()
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Process any pending messages from quick topics
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            last_message = st.session_state.messages[-1]["content"]
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = send_message(last_message, st.session_state.user_id)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about C programming!"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = send_message(prompt, st.session_state.user_id)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("👈 Please enter your name in the sidebar to start learning!")

def quiz_page():
    """Interactive quiz interface"""
    st.title("🧠 C Programming Quiz")
    
    if not st.session_state.user_id:
        st.info("👈 Please create a user profile first!")
        return
    
    # Quiz topic selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📚 Select Quiz Topic")
        
        # Predefined topics
        topics = {
            "Variables & Data Types": "variables",
            "Control Structures": "control_structures", 
            "Functions": "functions",
            "Arrays & Strings": "arrays",
            "Pointers": "pointers",
            "File I/O": "file_io",
            "Memory Management": "memory",
            "Structures": "structures"
        }
        
        selected_topic = st.selectbox(
            "Choose a topic:",
            list(topics.keys())
        )
        
        # Custom topic input
        custom_topic = st.text_input("Or enter a custom topic:")
        final_topic = custom_topic if custom_topic else topics[selected_topic]
    
    with col2:
        st.markdown("### ⚙️ Quiz Settings")
        difficulty = st.slider("Difficulty Level", 1, 10, 5)
        num_questions = st.slider("Number of Questions", 3, 10, 5)
    
    # Generate Quiz Button
    if st.button("🎯 Generate Quiz", use_container_width=True):
        with st.spinner("Generating quiz questions..."):
            quiz_data = generate_quiz(final_topic, difficulty, num_questions)
            if quiz_data:
                st.session_state.quiz_data = quiz_data
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_topic = final_topic
                st.success("Quiz generated successfully!")
                st.rerun()
    
    # Display Quiz
    if st.session_state.quiz_data and not st.session_state.quiz_submitted:
        st.divider()
        st.markdown("### 📝 Quiz Questions")
        
        # Display questions
        for i, question in enumerate(st.session_state.quiz_data):
            st.markdown(f"**Question {i+1}:** {question['question']}")
            
            # Radio buttons for options
            options = question.get('options', [])
            if options:
                answer = st.radio(
                    f"Select your answer for question {i+1}:",
                    options,
                    key=f"q_{i}",
                    index=None
                )
                if answer:
                    st.session_state.quiz_answers[i] = options.index(answer)
            
            st.markdown("---")
        
        # Submit Quiz Button
        if len(st.session_state.quiz_answers) == len(st.session_state.quiz_data):
            if st.button("✅ Submit Quiz", use_container_width=True):
                score = calculate_quiz_score()
                st.session_state.quiz_score = score
                st.session_state.quiz_submitted = True
                
                # Submit score to backend
                submit_quiz_score(
                    st.session_state.user_id, 
                    st.session_state.quiz_topic, 
                    score
                )
                st.rerun()
        else:
            st.info(f"Please answer all questions ({len(st.session_state.quiz_answers)}/{len(st.session_state.quiz_data)} completed)")
    
    # Display Results
    elif st.session_state.quiz_data and st.session_state.quiz_submitted:
        display_quiz_results()

def calculate_quiz_score():
    """Calculate quiz score based on correct answers"""
    if not st.session_state.quiz_data or not st.session_state.quiz_answers:
        return 0
    
    correct_answers = 0
    total_questions = len(st.session_state.quiz_data)
    
    for i, question in enumerate(st.session_state.quiz_data):
        user_answer = st.session_state.quiz_answers.get(i)
        correct_answer = question.get('correct_answer', 0)
        
        if user_answer == correct_answer:
            correct_answers += 1
    
    return (correct_answers / total_questions) * 100

def display_quiz_results():
    """Display quiz results with detailed feedback"""
    st.divider()
    st.markdown("### 🎉 Quiz Results")
    
    score = st.session_state.quiz_score
    total_questions = len(st.session_state.quiz_data)
    correct_answers = int((score / 100) * total_questions)
    
    # Score display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score:.1f}%")
    with col2:
        st.metric("Correct Answers", f"{correct_answers}/{total_questions}")
    with col3:
        if score >= 80:
            st.success("🌟 Excellent!")
        elif score >= 60:
            st.info("👍 Good job!")
        else:
            st.warning("📚 Keep practicing!")
    
    # Detailed feedback
    st.markdown("### 📊 Detailed Feedback")
    
    for i, question in enumerate(st.session_state.quiz_data):
        user_answer = st.session_state.quiz_answers.get(i, -1)
        correct_answer = question.get('correct_answer', 0)
        options = question.get('options', [])
        
        # Question display
        st.markdown(f"**Question {i+1}:** {question['question']}")
        
        if user_answer == correct_answer:
            st.success(f"✅ Correct! Answer: {options[correct_answer] if options else 'N/A'}")
        else:
            st.error(f"❌ Incorrect")
            if options:
                st.info(f"Your answer: {options[user_answer] if user_answer < len(options) else 'No answer'}")
                st.info(f"Correct answer: {options[correct_answer]}")
        
        # Show explanation if available
        explanation = question.get('explanation', '')
        if explanation:
            st.markdown(f"💡 **Explanation:** {explanation}")
        
        st.markdown("---")
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_data = None
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()
    
    with col2:
        if st.button("💬 Ask Questions", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()

def progress_page():
    """User progress tracking page"""
    st.title("📈 Learning Progress")
    
    if not st.session_state.user_id:
        st.info("👈 Please create a user profile first!")
        return
    
    # Get user profile
    profile = get_user_profile(st.session_state.user_id)
    
    if profile:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Overall Progress")
            st.metric("Current Level", profile.get("current_level", 1))
            st.metric("Lessons Completed", len(profile.get("completed_lessons", [])))
            
            # Progress bar (mock data)
            progress = min(profile.get("current_level", 1) * 10, 100)
            st.progress(progress / 100)
            st.caption(f"Progress: {progress}% to next level")
        
        with col2:
            st.markdown("### 🧠 Quiz Performance")
            quiz_scores = profile.get("quiz_scores", {})
            
            if quiz_scores:
                avg_score = sum(quiz_scores.values()) / len(quiz_scores)
                st.metric("Average Score", f"{avg_score:.1f}%")
                st.metric("Quizzes Taken", len(quiz_scores))
                
                # Quiz scores chart
                st.markdown("#### Recent Quiz Scores")
                for topic, score in quiz_scores.items():
                    st.write(f"**{topic.replace('_', ' ').title()}:** {score:.1f}%")
                    st.progress(score / 100)
            else:
                st.info("No quiz scores yet. Take a quiz to see your progress!")
        
        # Learning suggestions
        st.divider()
        st.markdown("### 💡 Learning Suggestions")
        
        current_level = profile.get("current_level", 1)
        
        if current_level <= 2:
            st.info("🌱 **Beginner Focus:** Master variables, data types, and basic input/output")
        elif current_level <= 5:
            st.info("🚀 **Intermediate Focus:** Practice loops, functions, and arrays")
        else:
            st.info("⚡ **Advanced Focus:** Explore pointers, memory management, and file operations")
    
    else:
        st.error("Could not load user profile")

def lessons_page():
    """Structured lessons page"""
    st.title("📚 C Programming Lessons")
    
    if not st.session_state.user_id:
        st.info("👈 Please create a user profile first!")
        return
    
    # Lesson categories
    lessons = {
        "🌱 Beginner": [
            "Introduction to C Programming",
            "Variables and Data Types", 
            "Input and Output",
            "Operators and Expressions"
        ],
        "🚀 Intermediate": [
            "Control Structures (if/else)",
            "Loops (for, while, do-while)",
            "Functions and Parameters",
            "Arrays and Strings"
        ],
        "⚡ Advanced": [
            "Pointers and Memory",
            "Structures and Unions", 
            "File Input/Output",
            "Dynamic Memory Allocation"
        ]
    }
    
    for category, lesson_list in lessons.items():
        st.markdown(f"### {category}")
        
        for i, lesson in enumerate(lesson_list):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{i+1}.** {lesson}")
            
            with col2:
                if st.button("📖 Study", key=f"study_{category}_{i}"):
                    # Add lesson topic to chat
                    lesson_query = f"Teach me about {lesson} in C programming"
                    st.session_state.messages.append({"role": "user", "content": lesson_query})
                    st.session_state.current_page = "Chat"
                    st.rerun()
            
            with col3:
                if st.button("🧠 Quiz", key=f"quiz_{category}_{i}"):
                    # Generate quiz for this topic
                    st.session_state.current_page = "Quiz"
                    st.rerun()
        
        st.markdown("---")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Sidebar navigation
    sidebar_navigation()
    
    # Main content based on selected page
    if st.session_state.current_page == "Chat":
        chat_page()
    elif st.session_state.current_page == "Quiz":
        quiz_page()
    elif st.session_state.current_page == "Progress":
        progress_page()
    elif st.session_state.current_page == "Lessons":
        lessons_page()

if __name__ == "__main__":
    main()