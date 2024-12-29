import streamlit as st
import google.generativeai as genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from io import BytesIO
import os
import logging
import pandas as pd
import datetime

# Set page configuration
st.set_page_config(page_title="Health & Fitness Bot", layout="wide", initial_sidebar_state="expanded")

if "show_splash" not in st.session_state:
    st.session_state.show_splash = True
    
# Logging setup
logging.basicConfig(level=logging.INFO)

# Gemini API setup
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDRsftfex1wmCRXE6_X-CWe7dz0cI3qYb8'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Function to query health coach
def query_health_coach(goal, metrics):
    prompt = f"""Based on the goal: {goal} and the following fitness metrics: {metrics}, generate:
    1. A customized workout plan.
    2. A personalized dietary plan.
    3. Additional fitness tips or motivational messages.

    Format:
    - Day 1: ...
    Workout Plan:
    - Day 2: ...
    ...

    Dietary Plan:
    - Breakfast: ...
    - Lunch: ...
    - Dinner: ...
    ...

    Tips:
    1. Tip 1
    2. Tip 2
    ...

    End with a unique motivational quote.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        if response and response.parts:
            generated_response = response.text

            # Append a motivational quote
            motivational_quote = "🌟 *“Your body can stand almost anything. It’s your mind you have to convince.”*"
            return f"{generated_response}\n\n{motivational_quote}"
        else:
            logging.error("No response parts found.")
            return "Sorry, there was an error generating the response."
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "Sorry, there was an error generating the response."


def create_pdf(report):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    # Title Section
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0.2, 0.4, 0.6)
    c.drawString(margin, y, "💪 Health & Fitness Report")
    y -= 30

    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(margin, y, "Your Personalized Health Journey 🌟")
    y -= 40

    max_width = width - 2 * margin

    # Helper function to draw wrapped text
    def draw_wrapped_text(c, text, x, y, max_width, font_name="Helvetica", font_size=12, line_spacing=14):
        lines = simpleSplit(text, font_name, font_size, max_width)
        for line in lines:
            if y < margin:
                c.showPage()
                c.setFont(font_name, font_size)
                y = height - margin
            c.drawString(x, y, line)
            y -= line_spacing
        return y

    # Parse and format the report sections
    for line in report.split('\n'):
        line = line.strip()
        if line.startswith("**Workout Plan:**"):
            c.setFont("Helvetica-Bold", 16)
            c.setFillColorRGB(0.2, 0.6, 0.4)
            y = draw_wrapped_text(c, f"🏋️‍♂️ {line.replace('**', '')}", margin, y, max_width, "Helvetica-Bold", 16, line_spacing=18)
        elif line.startswith("**Dietary Plan:**"):
            c.setFont("Helvetica-Bold", 16)
            c.setFillColorRGB(0.6, 0.2, 0.6)
            y = draw_wrapped_text(c, f"🍽️ {line.replace('**', '')}", margin, y, max_width, "Helvetica-Bold", 16, line_spacing=18)
        elif line.startswith("**Tips:**"):
            c.setFont("Helvetica-Bold", 16)
            c.setFillColorRGB(0.4, 0.6, 0.8)
            y = draw_wrapped_text(c, f"💡 {line.replace('**', '')}", margin, y, max_width, "Helvetica-Bold", 16, line_spacing=18)
        elif line.startswith("**Day"):
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0.2, 0.4, 0.6)
            y = draw_wrapped_text(c, f"📅 {line.replace('**', '')}", margin + 20, y, max_width - 20, "Helvetica-Bold", 14, line_spacing=16)
        elif line.startswith("*"):
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(0, 0, 0)
            y = draw_wrapped_text(c, f"• {line[1:].strip()}", margin + 40, y, max_width - 40, "Helvetica", 12, line_spacing=14)
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(0.2, 0.4, 0.6)
            y = draw_wrapped_text(c, f"{line.strip()}", margin + 20, y, max_width - 20, "Helvetica", 12, line_spacing=14)
        else:
            y = draw_wrapped_text(c, line, margin + 20, y, max_width - 20, "Helvetica", 12, line_spacing=14)

    # Footer with team name
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    footer_text = "Generated with ❤️ by SYNTAX SQUAD"
    c.drawString(margin, margin / 2, footer_text)

    c.save()
    buffer.seek(0)
    return buffer



# CSS and JavaScript for styling and animations
st.markdown(
    """
    <style>
   

    /* Main App Styles */
  .dashboard-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; /* Space between cards */
            margin-bottom: 2rem;
            opacity: 0;
            animation: fadeIn 0.5s ease-in-out 2.5s forwards;
        }

        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
        }

        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #2E86C1;
            margin: 10px 0;
        }

        .metric-label {
            color: #7F8C8D;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
        opacity: 0;
        animation: fadeIn 0.5s ease-in-out 2.7s forwards;
    }


   


    .section-title {
        color: #2C3E50;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498DB;
    }

    
    .form-header {
        color:rgb(217, 223, 228);
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
    }

    /* Hide main content initially */
    .main-content {
        opacity: 0;
        animation: fadeIn 0.5s ease-in-out 2.5s forwards;
    }
    </style>

    <script>
    // Add click handler to dismiss splash screen
    document.addEventListener('DOMContentLoaded', function() {
        const splashScreen = document.querySelector('.splash-screen');
        if (splashScreen) {
            splashScreen.addEventListener('click', function() {
                splashScreen.style.animation = 'fadeOut 0.5s ease-in-out forwards';
            });
        }
    });
    </script>
    """,
    unsafe_allow_html=True,
)

# Show splash screen
st.markdown("""
    <div class="splash-screen">
        <div class="splash-content">
            <div class="splash-title">✨ Developed by SYNTAX SQUAD ✨</div>
            
       
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if "data" not in st.session_state:
    st.session_state["data"] = {
        "Date": [],
        "Steps": [],
        "Sleep (hours)": [],
        "Calories Burned": []
    }

# Main content wrapper with fade-in animation
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("🌟 Health & Fitness Personal Coach")


dashboard_tab, planning_tab = st.tabs(["📈 User Performance Dashboard", "📝 Generate Plans"])

with dashboard_tab:
    st.markdown('<h2 class="section-title">📊 Performance Dashboard</h2>', unsafe_allow_html=True)
    
    # Data Input Form
    with st.container():
        st.markdown('<div class="data-form">', unsafe_allow_html=True)
        st.markdown('<p class="form-header">📝 Add Today\'s Metrics</p>', unsafe_allow_html=True)
        
        with st.form("add_data_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("📅 Date", value=datetime.date.today())
                steps = st.number_input("👟 Steps", min_value=0, step=1)
            with col2:
                sleep = st.number_input("🛌 Sleep (hours)", min_value=0.0, max_value=24.0, step=0.1)
                calories = st.number_input("🔥 Calories", min_value=0, step=1)
            
            submitted = st.form_submit_button("💾 Save Data")
            
            if submitted:
                if date in st.session_state["data"]["Date"]:
                    index = st.session_state["data"]["Date"].index(date)
                    st.session_state["data"]["Steps"][index] = steps
                    st.session_state["data"]["Sleep (hours)"][index] = sleep
                    st.session_state["data"]["Calories Burned"][index] = calories
                    st.success("✅ Data updated successfully!")
                else:
                    st.session_state["data"]["Date"].append(date)
                    st.session_state["data"]["Steps"].append(steps)
                    st.session_state["data"]["Sleep (hours)"].append(sleep)
                    st.session_state["data"]["Calories Burned"].append(calories)
                    st.success("✅ Data added successfully!")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["data"]["Date"]:
        df = pd.DataFrame(st.session_state["data"])
        
        # Summary Metrics
        st.markdown('<div class="dashboard-metrics">', unsafe_allow_html=True)
        metrics = {
            "Average Daily Steps": f"{int(df['Steps'].mean()):,}",
            "Average Sleep": f"{df['Sleep (hours)'].mean():.1f} hrs",
            "Total Calories Burned": f"{int(df['Calories Burned'].sum()):,}",
            "Days Tracked": f"{len(df)} days"
        }
        
        for label, value in metrics.items():
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts
        st.markdown('<div class="chart-grid">', unsafe_allow_html=True)
        
        # Steps Chart
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">👟 Step Count Trends</h3>', unsafe_allow_html=True)
            st.line_chart(df.set_index("Date")["Steps"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sleep Chart
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">🛌 Sleep Pattern</h3>', unsafe_allow_html=True)
            st.line_chart(df.set_index("Date")["Sleep (hours)"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Calories Chart
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">🔥 Calories Burned</h3>', unsafe_allow_html=True)
            st.bar_chart(df.set_index("Date")["Calories Burned"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Table
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">📋 Detailed Log</h3>', unsafe_allow_html=True)
        st.dataframe(
            df.style.format({
                'Steps': '{:,.0f}',
                'Sleep (hours)': '{:.1f}',
                'Calories Burned': '{:,.0f}'
            }),
            use_container_width=True,
            height=300
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👋 Welcome! Start by adding your daily metrics using the form above.")

with planning_tab:
    st.subheader("🎯 Generate Your Plan")

    goal = st.text_area("🎯 Enter your health and fitness goal:", "")
    metrics = st.text_area("📊 Provide your current fitness metrics (e.g., steps, calories, sleep hours):", "")

    if st.button("🚀 Generate Plan and Recommendations"):
        if goal and metrics:
            with st.spinner("Generating your personalized plan... ✨"):
                report = query_health_coach(goal, metrics)
                

            st.subheader("📄 Your Personalized Plan")
            st.write(report)

            pdf = create_pdf(report)
            st.download_button(
                label="📥 Download Report as PDF",
                data=pdf,
                file_name="health_fitness_report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("⚠️ Please enter both your goal and fitness metrics.")

st.markdown('</div>', unsafe_allow_html=True)  # Close main-content wrapper

st.sidebar.markdown("""
## ℹ️ PROBLEM STATEMENT:
Design an AI-powered health and fitness bot that acts as a personal coach. The bot should monitor fitness metrics like steps, 
calories, and sleep patterns, generate customized workout and dietary plans based on user goals, and offer real-time tips and motivational messages. 
Integration with wearable devices for seamless data collection is essential. This bot should empower users to maintain a healthier lifestyle with minimal effort.

---

## 👥 SYNTAX SQUAD MEMBERS:
- **Afrid Sk**
- **Manikanta**
- **Praveen**
- **Satwika**
- **Thanmai**


""")

st.markdown("---")
st.write("🚀 Built by **Syntax Squad** during the **BUILD-A-BOT 24hrs Hackathon - December 2024** ")