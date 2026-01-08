import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, date

# Import our custom modules
import data_manager
import chatbot

# Get the absolute path to the project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(BASE_DIR, "logo")

# Set page configuration
st.set_page_config(
    page_title="InsureBot - Insurance Recommendation Chatbot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to style the application
def load_css():
    # Path to CSS file
    css_file = "static/css/style.css"
    
    # Read CSS file with explicit UTF-8 encoding
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            css = f.read()
            
        # Apply CSS
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except UnicodeDecodeError as e:
        print(f"Encoding error loading CSS file: {e}")
        # Fallback to basic styling if file can't be loaded due to encoding issues
        st.markdown("""
        <style>
            .main-header { 
                font-size: 2rem; 
                color: #1E88E5; 
                text-align: center; 
            }
        </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        print(f"Error loading CSS file: {e}")
        # Fallback to basic styling if file can't be loaded
        st.markdown("""
        <style>
            .main-header { 
                font-size: 2rem; 
                color: #1E88E5; 
                text-align: center; 
            }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state variables
def initialize_session_state():
    # Navigation state
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = "welcome"
    
    # User profile data
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            "first_name": "",
            "last_name": "",
            "dob": None,
            "gender": "Male",
            "smoker_status": "Non Smoker",
            "email": "",
            "phone": "",
        }
    
    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "bot", "content": "Hi there! I'm InsureBot, your Hong Kong whole life insurance assistant. How can I help you today?"}
        ]
    
    # Chatbot context
    if 'chatbot_context' not in st.session_state:
        st.session_state.chatbot_context = {}
    
    # Selected plan for details view
    if 'selected_plan' not in st.session_state:
        st.session_state.selected_plan = None
    
    # Insurance filter criteria
    if 'insurance_filters' not in st.session_state:
        st.session_state.insurance_filters = {
            "gender": "Male",
            "age": 35,
            "smoker_status": "Non Smoker",
            "max_price": 5000,
            "min_score": 0
        }
    
    # Saved plans from data manager
    if 'saved_plans' not in st.session_state:
        st.session_state.saved_plans = data_manager.get_saved_plans()
    
    # Initialize plans for comparison list
    if 'comparison_plans' not in st.session_state:
        st.session_state.comparison_plans = []
    
    # Flag to show comparison view
    if 'show_comparison' not in st.session_state:
        st.session_state.show_comparison = False

# Function to navigate between screens
def navigate_to(screen):
    st.session_state.current_screen = screen
    st.rerun()

# Function to display the header with logo
def display_header():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<div class="logo">🛡️ InsureBot</div>', unsafe_allow_html=True)
    with col2:
        # Remove the Sign In button which would go to settings
        pass

# Navigation sidebar
def display_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar">', unsafe_allow_html=True)
        
        # Create button container for consistent width
        st.markdown('<div style="padding: 0 10px;">', unsafe_allow_html=True)
        
        # Helper function to create nav buttons with active state styling
        def nav_button(label, screen_name, key):
            # Check if this button is the active screen
            is_active = st.session_state.current_screen == screen_name
            
            # If active, wrap in div with active class
            if is_active:
                st.markdown(f'<div class="active-nav-button">', unsafe_allow_html=True)
                result = st.button(label, key=key, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                result = st.button(label, key=key, use_container_width=True)
                
            if result:
                navigate_to(screen_name)
            
            return result
        
        # Navigation buttons - simplified for whole life focus
        nav_button("Welcome", "welcome", "nav_welcome")
        # nav_button("Profile Setup", "profile_setup", "nav_profile")
        nav_button("Chat", "chat", "nav_chat")
        nav_button("Insurance Plans", "insurance_plans", "nav_insurance")
        nav_button("Compare Plans", "comparison", "nav_comparison")
        nav_button("Saved Plans", "saved", "nav_saved")
            
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Welcome screen
def welcome_screen():
    st.markdown('<h1 class="main-header" style="text-align: center;">Welcome to InsureBot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text" style="text-align: center; font-size: 1.2rem;">Your AI-powered assistant for Hong Kong whole life insurance</p>', unsafe_allow_html=True)
    
    # Display a centered image or icon
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center; font-size: 5rem; margin: 20px 0;">🛡️</div>', unsafe_allow_html=True)
    
    # Card container
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-bottom: 20px;">Find the Perfect Whole Life Insurance in Hong Kong</h2>', unsafe_allow_html=True)
    
    # Create three columns for the steps
    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div style="display: inline-block; width: 30px; height: 30px; border-radius: 50%; background-color: #1E88E5; color: white; text-align: center; line-height: 30px; margin-bottom: 10px; font-weight: bold;">1</div>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center;">Chat with InsureBot</h3>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center;">Ask questions about whole life insurance policies and get personalized recommendations.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with step2:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div style="display: inline-block; width: 30px; height: 30px; border-radius: 50%; background-color: #1E88E5; color: white; text-align: center; line-height: 30px; margin-bottom: 10px; font-weight: bold;">2</div>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center;">Save Plans</h3>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center;">Browse through our database of Hong Kong whole life insurance plans and save your preferred options.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with step3:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div style="display: inline-block; width: 30px; height: 30px; border-radius: 50%; background-color: #1E88E5; color: white; text-align: center; line-height: 30px; margin-bottom: 10px; font-weight: bold;">3</div>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center;">Compare Plans</h3>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center;">Compare your saved plans side by side to find the best match for your needs.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bottom text
    st.markdown('<div style="text-align: center; margin-top: 20px;">', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Our AI assistant helps you understand complex insurance terms and finds the best plans for your needs.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close card
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">', unsafe_allow_html=True)
        # col_a, col_b = st.columns(2)
        # with col_a:
        #     if st.button("Get Started", key="get_started", use_container_width=True):
        #         navigate_to("profile_setup")
        # with col_b:
        if st.button("Chat Now", key="chat_now", use_container_width=True):
            navigate_to("chat")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Information about the app
    st.markdown('<div class="card" style="margin-top: 30px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center;">Why Choose InsureBot?</h3>', unsafe_allow_html=True)
    
    benefit1, benefit2, benefit3 = st.columns(3)
    
    with benefit1:
        st.markdown('<h4>🔍 Comprehensive Database</h4>', unsafe_allow_html=True)
        st.markdown('<p>Access to extensive Hong Kong whole life insurance plans with detailed information.</p>', unsafe_allow_html=True)
    
    with benefit2:
        st.markdown('<h4>💬 Expert Assistance</h4>', unsafe_allow_html=True)
        st.markdown('<p>Get answers to your insurance questions in plain language.</p>', unsafe_allow_html=True)
    
    with benefit3:
        st.markdown('<h4>📊 Personalized Recommendations</h4>', unsafe_allow_html=True)
        st.markdown('<p>Receive tailored plan suggestions based on your specific needs and preferences.</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Profile setup screen
def profile_setup_screen():
    st.markdown('<h1 class="main-header">Set Up Your Profile</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Let\'s get to know you better so we can provide personalized whole life insurance recommendations.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.user_profile["first_name"] = st.text_input("First Name", value=st.session_state.user_profile.get("first_name", ""))
    
    with col2:
        st.session_state.user_profile["last_name"] = st.text_input("Last Name", value=st.session_state.user_profile.get("last_name", ""))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Using dynamic date range for birth date based on current date
        from datetime import date, datetime, timedelta
        
        # Get current date
        current_date = datetime.now().date()
        
        # Set min date to 100 years ago from current date
        min_date = date(current_date.year - 100, current_date.month, current_date.day)
        
        # Set max date to current date (allowing selection up to today)
        max_date = current_date
        
        # Get existing DOB or default to 30 years ago
        if not st.session_state.user_profile.get("dob") or not isinstance(st.session_state.user_profile.get("dob"), date):
            default_date = date(current_date.year - 30, current_date.month, current_date.day)
            # Adjust if the default date would be February 29 on a non-leap year
            try:
                default_date = date(current_date.year - 30, current_date.month, current_date.day)
            except ValueError:
                # Handle February 29 issue on non-leap years
                default_date = date(current_date.year - 30, current_date.month, 28)
        else:
            default_date = st.session_state.user_profile.get("dob")
        
        st.session_state.user_profile["dob"] = st.date_input(
            "Date of Birth", 
            value=default_date,
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        gender_options = ["Male", "Female"]
        st.session_state.user_profile["gender"] = st.selectbox(
            "Gender",
            options=gender_options,
            index=gender_options.index(st.session_state.user_profile["gender"]) if st.session_state.user_profile["gender"] in gender_options else 0
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        smoker_options = ["Non Smoker", "Smoker"]
        st.session_state.user_profile["smoker_status"] = st.selectbox(
            "Smoker Status",
            options=smoker_options,
            index=smoker_options.index(st.session_state.user_profile["smoker_status"]) if st.session_state.user_profile["smoker_status"] in smoker_options else 0
        )
    
    # Add Save button in the center
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Save Profile", key="save_profile"):
            # Save profile data
            data_manager.save_user_profile(st.session_state.user_profile)
            st.success("Profile information saved successfully!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", key="profile_back"):
            navigate_to("welcome")
    with col2:
        if st.button("Next", key="profile_next"):
            # Save profile data
            data_manager.save_user_profile(st.session_state.user_profile)
            
            # Update insurance filters with profile data
            if st.session_state.user_profile.get("dob"):
                today = date.today()
                age = today.year - st.session_state.user_profile["dob"].year - ((today.month, today.day) < (st.session_state.user_profile["dob"].month, st.session_state.user_profile["dob"].day))
                st.session_state.insurance_filters["age"] = age
            
            st.session_state.insurance_filters["gender"] = st.session_state.user_profile["gender"]
            st.session_state.insurance_filters["smoker_status"] = st.session_state.user_profile["smoker_status"]
            
            # Update chatbot context with profile data
            st.session_state.chatbot_context["user_name"] = st.session_state.user_profile["first_name"]
            st.session_state.chatbot_context["gender"] = st.session_state.user_profile["gender"]
            st.session_state.chatbot_context["smoker_status"] = st.session_state.user_profile["smoker_status"]
            
            navigate_to("chat")

# Chat screen
def chat_screen():
    # Create containers for chat display and input
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message_idx, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            elif message["role"] == "bot":
                if message.get("type") == "plans":
                    with st.chat_message("assistant"):
                        st.write(message["content"])
                        
                        if hasattr(st.session_state, 'current_recommendations'):
                            for i, plan in enumerate(st.session_state.current_recommendations, 1):
                                col1, col2 = st.columns([5, 1])
                                with col1:
                                    # Get score from whole_life_score in details if available
                                    score = plan.get("details", {}).get("whole_life_score", "N/A")
                                    st.write(f'{i}. {plan["title"]} by {plan["company"]} | Price: HKD {plan["price"]}/month Score: {score}')
                                with col2:
                                    # Add message_idx to make the key unique for each message/plan combination
                                    unique_key = f"save_plan_{message_idx}_{plan['id']}_{i}"
                                    if st.button("save plan", key=unique_key):
                                        data_manager.save_plan(plan['id'])
                                        # Replace success message with toast notification
                                        st.toast(f"✅ Saved {plan['title']}", icon="✅")
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])
    
    # Chat input at bottom
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Show spinner while waiting for API response
        with st.spinner("waiting for response..."):
            # Get response from chatbot
            response = chatbot.get_chatbot_response(prompt, st.session_state.chatbot_context)
            
            try:
                # Check if the response is a dictionary with has_search_criteria flag
                has_search_criteria = False
                bot_response = ""
                
                if isinstance(response, dict) and "has_search_criteria" in response:
                    has_search_criteria = response["has_search_criteria"]
                    bot_response = response["response"]
                elif isinstance(response, str):
                    clean_response = response.strip('`').strip('json').strip()
                    try:
                        response_data = json.loads(clean_response)
                        bot_response = response_data.get("response", "")
                        # Check if insurance_criteria exists and is not empty
                        if "insurance_criteria" in response_data and response_data["insurance_criteria"]:
                            has_search_criteria = True
                        if not bot_response:
                            bot_response = clean_response
                    except json.JSONDecodeError:
                        bot_response = clean_response
                else:
                    bot_response = str(response)
                
                # Add bot response to chat history
                st.session_state.chat_history.append({"role": "bot", "content": bot_response})
                
                # Only show insurance plans if there are search criteria
                if has_search_criteria:
                    # Show spinner while fetching insurance plans
                    with st.spinner("Finding insurance plans for you..."):
                        insurance_plans = data_manager.get_whole_life_insurance()
                        if insurance_plans:
                            sorted_plans = sorted(insurance_plans, key=lambda x: x.get("score", 0), reverse=True)
                            top_3_plans = sorted_plans[:3]
                            st.session_state.current_recommendations = top_3_plans
                            plans_message = "Here are the top 3 insurance plans for you:"
                            st.session_state.chat_history.append({"role": "bot", "content": plans_message, "type": "plans"})
            
            except Exception as e:
                print(f"Error: {str(e)}")
                st.session_state.chat_history.append({"role": "bot", "content": str(response)})
        
        # Rerun the app to display the updated chat
        st.rerun()

# Function to display the plan comparison
def comparison_screen():
    """Display a side-by-side comparison of selected plans."""
    st.markdown('<h1 class="main-header">Plan Comparison</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Compare insurance plans side by side to find the best option for you.</p>', unsafe_allow_html=True)
    
    if len(st.session_state.comparison_plans) < 1:
        st.info("No plans selected for comparison. Add plans from the Insurance Plans page.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Browse Plans", use_container_width=True):
                navigate_to("insurance_plans")
        return
    
    # Get the plans to compare
    plans = st.session_state.comparison_plans
    
    # Create columns for plan headers
    cols = st.columns(len(plans) + (3 - len(plans)))  # Create exactly 3 columns: labels + up to 2 plan columns
    
    # First column is for labels/titles
    cols[0].markdown('<div style="height: 80px; padding-top: 30px;"><h3 style="color: #1E88E5;">Plan Details</h3></div>', unsafe_allow_html=True)
    
    # Display plan headers with bordered cards
    for i, plan in enumerate(plans):
        with cols[i+1]:
            # Create a container for each plan with a border
            with st.container():
                # Using Streamlit native components for better rendering
                st.markdown("""
                <div style="border: 2px solid #00bfa5; border-radius: 12px; padding: 20px; margin-bottom: 20px; position: relative; background-color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="position: absolute; top: 10px; right: 10px; background-color: #00bfa5; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                        Comparing
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Map company names to logo filenames
                company_logo_map = {
                    "AIA": "Brokerage_AIA_e76423525d.png",
                    "AXA": "AXA_logo_21b519b8f2.png",
                    "BOC Life": "BOCL_logo_c3917e8087.png",
                    "Chubb": "Chubb_logo_bbd61d9801.png",
                    "China Life": "China_Life_logo_6849c94581.png",
                    "FT Life": "FT_Life_logo_954f536d7e.jpg",
                    "FWD": "FWD_logo_694230ea93.jpg",
                    "Generali": "Generali_logo_78dd1d3d8b.png",
                    "Manulife": "Manulife_logo_1449597a78.png",
                    "Prudential": "Prudential_logo_f4e56bc4f0.png",
                    "Sun Life": "Insurer_Sun_Life_logo_new2023_b0ccadbe5f.png",
                    "Well Link": "Well_Link_logo_2_resized_96d44077d2.png",
                    "YF Life": "YF_Life_logo_065ba084ce.png"
                }
                
                # Company name display
                company_name = plan['company']
                st.markdown(f"<h3 style='text-align: center; color: #00bfa5;'>{company_name}</h3>", unsafe_allow_html=True)
                
                # Get the correct logo for the company - handle Chinese characters
                logo_filename = ""
                # First try direct lookup
                if company_name in company_logo_map:
                    logo_filename = company_logo_map[company_name]
                else:
                    # Try matching on the English part before any pipe symbol
                    if "|" in company_name:
                        english_name = company_name.split("|")[0].strip()
                        if english_name in company_logo_map:
                            logo_filename = company_logo_map[english_name]
                        else:
                            # Try partial matching - find if any key is contained in the company name
                            for key in company_logo_map:
                                if key in company_name:
                                    logo_filename = company_logo_map[key]
                                    break
                
                print(f"Company name: {company_name}, English part: {company_name.split('|')[0].strip() if '|' in company_name else company_name}, Logo filename: {logo_filename}")
                
                # Initialize company_logo variable
                company_logo = None
                
                if logo_filename:
                    # Display company logo using Streamlit's image display functionality
                    try:
                        # Use absolute path to logo directory
                        logo_path = os.path.join(LOGO_DIR, logo_filename)
                        print(f"Looking for logo at: {logo_path}")
                        print(f"File exists: {os.path.exists(logo_path)}")
                        
                        if os.path.exists(logo_path):
                            company_logo = Image.open(logo_path)
                    except Exception as e:
                        # Show the error for debugging
                        print(f"Error loading logo: {str(e)}")
                        pass
                
                # Plan name
                st.markdown(f"<h4 style='text-align: center;'>{plan['title']}</h4>", unsafe_allow_html=True)
                
                # Score display in circle
                total_score = float(plan["details"].get("total_score", 0))
                
                # Create score display with Streamlit
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    #show company logo or 10Life rating if logo not available
                    if company_logo is not None:
                        st.image(company_logo, width=150)
                    else:
                        print(f"company_logo: {company_logo}")
                        st.markdown(f"""
                        <div style="width: 60px; height: 60px; background-color: #00bfa5; border-radius: 50%; 
                            margin: 0 auto; display: flex; flex-direction: column; justify-content: center; 
                            align-items: center; color: white; text-align: center;">
                            <div style="font-size: 10px;">10Life</div>
                            <div>{total_score:.1f}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Remove button
            if st.button("Remove", key=f"remove_{plan['id']}", use_container_width=True):
                remove_from_comparison(plan['id'])
                st.rerun()
    
    # Add "Add Plan" button if we have fewer than 2 plans
    if len(plans) < 2:
        with cols[len(plans)+1]:
            # Create a visual button with st.container
            with st.container():
                st.markdown("""
                <div style="height: 100px; display: flex; align-items: center; justify-content: center; 
                    border: 2px dashed #1E88E5; border-radius: 12px; margin-bottom: 20px; cursor: pointer;">
                    <div style="text-align: center; color: #1E88E5;">
                        <span style="font-size: 24px;">+</span><br>
                        Add another plan to compare
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("+ Add Plan", key="add_plan_to_compare", use_container_width=True):
                    navigate_to("insurance_plans")
    
    # Create a table for comparing plan details with a card style and border
    st.markdown("""
    <div style="border: 2px solid #1E88E5; border-radius: 12px; padding: 24px; margin-top: 30px; margin-bottom: 20px; 
         background-color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    """, unsafe_allow_html=True)
    
    # Scores section
    st.markdown('<h3 style="color: #1E88E5; border-bottom: 1px solid #e0e0e0; padding-bottom: 10px;">Scores</h3>', unsafe_allow_html=True)
    cols = st.columns(len(plans) + 1)  # Always create enough columns for plans + labels
    
    # Labels column
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Total Score</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Whole Life CI Coverage Score</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Terms Score</div>", unsafe_allow_html=True)
    
    # Values columns
    for i, plan in enumerate(plans):
        total_score = float(plan["details"].get("total_score", 0))
        whole_life_score = float(plan["details"].get("whole_life_score", 0))
        terms_score = float(plan["details"].get("terms_score", 0))
        
        formatted_total = f"{total_score:.1f}"
        formatted_whole_life = f"{whole_life_score:.1f}" if whole_life_score > 0 else "N/A"
        formatted_terms = f"{terms_score:.1f}" if terms_score > 0 else "N/A"
        
        cols[i+1].markdown(f"<div style='margin-bottom: 15px; font-weight: bold; color: #00bfa5;'>{formatted_total} <span style='font-weight: normal; color: #666;'>/10</span></div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px; font-weight: bold;'>{formatted_whole_life} <span style='font-weight: normal; color: #666;'>/10</span></div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px; font-weight: bold;'>{formatted_terms} <span style='font-weight: normal; color: #666;'>/10</span></div>", unsafe_allow_html=True)
    
    # Coverage section
    st.markdown('<h3 style="color: #1E88E5; border-bottom: 1px solid #e0e0e0; padding-bottom: 10px; margin-top: 20px;">Coverage Details</h3>', unsafe_allow_html=True)
    cols = st.columns(len(plans) + 1)
    
    # Coverage labels
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Annual Premium</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Premium Term (Years)</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Major Illnesses Covered</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Early Illnesses Covered</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Maximum Payout</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Waiting Period</div>", unsafe_allow_html=True)
    cols[0].markdown("<div style='font-weight: bold; margin-bottom: 15px;'>Issue Age</div>", unsafe_allow_html=True)
    
    # Coverage values
    for i, plan in enumerate(plans):
        cols[i+1].markdown(f"<div style='margin-bottom: 15px; font-weight: bold;'>USD {float(plan['price']) * 12:.0f} <span style='font-weight: normal; color: #666;'>/ Year</span></div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px;'>{plan['details'].get('premium_term_years', 'N/A')}</div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px;'>{plan['details'].get('major_illnesses', 'N/A')}</div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px;'>{plan['details'].get('early_illnesses', 'N/A')}</div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px;'>{plan['details'].get('maximum_payout', 'N/A')}</div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px;'>{plan['details'].get('waiting_period', 'N/A')}</div>", unsafe_allow_html=True)
        cols[i+1].markdown(f"<div style='margin-bottom: 15px;'>{plan['details'].get('issue_age', 'N/A')}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close card div
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Browse More Plans", key="compare_browse_more", use_container_width=True):
            navigate_to("insurance_plans")
    
    if len(plans) == 2:
        with col2:
            if st.button("Save Plans", key="save_comparison", use_container_width=True):
                for plan in plans:
                    data_manager.save_plan(plan['id'])
                st.success("Both plans saved to your saved plans!")

# Saved plans screen
def saved_plans_screen():
    st.markdown('<h1 class="main-header">Your Saved Insurance Plans</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Review and manage your saved insurance plan recommendations.</p>', unsafe_allow_html=True)
    
    # Refresh saved plans from data manager
    saved_plans = data_manager.get_saved_plans()
    st.session_state.saved_plans = saved_plans
    
    if not saved_plans:
        st.info("You don't have any saved plans yet. Explore recommendations to find and save insurance plans.")
    else:
        # Initialize dialog state if not exists
        if 'show_dialog' not in st.session_state:
            st.session_state.show_dialog = False
            st.session_state.dialog_plan = None
        
        # Either show the detailed view OR the list view, not both
        if st.session_state.show_dialog and st.session_state.dialog_plan:
            # DETAILED VIEW
            plan = st.session_state.dialog_plan
            
            # Back button
            if st.button("← Back to Saved Plans", key="back_to_saved"):
                st.session_state.show_dialog = False
                st.rerun()
            
            # Create a container for the detailed view
            detail_container = st.container()
            with detail_container:
                # Display in a card
                st.markdown('<div class="card" style="border-radius: 12px; padding: 20px; margin-bottom: 20px;">', unsafe_allow_html=True)
                
                # Plan header section
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 18px; font-weight: bold; color: #1E88E5;">{plan['company']}</div>
                    <h2 style="margin: 10px 0;">{plan['title']}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Display plan scores
                col1, col2, col3 = st.columns(3)
                
                total_score = float(plan["details"].get("total_score", 0))
                whole_life_score = float(plan["details"].get("whole_life_score", 0))
                terms_score = float(plan["details"].get("terms_score", 0))
                
                formatted_total = f"{total_score:.1f}"
                formatted_whole_life = f"{whole_life_score:.1f}" if whole_life_score > 0 else "N/A"
                formatted_terms = f"{terms_score:.1f}" if terms_score > 0 else "N/A"
                
                col1.metric("Total Score", f"{formatted_total}/10")
                col2.metric("Whole Life CI Score", f"{formatted_whole_life}/10")
                col3.metric("Terms Score", f"{formatted_terms}/10")
                
                # Divider
                st.markdown("<hr>", unsafe_allow_html=True)
                
                # Coverage Details section
                st.markdown("<h3>Coverage Details</h3>", unsafe_allow_html=True)
                
                # Create two columns for better organization
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<b>Annual Premium</b>", unsafe_allow_html=True)
                    st.write(f"USD {float(plan['price']) * 12:.0f} / Year")
                    
                    st.markdown("<b>Premium Term</b>", unsafe_allow_html=True)
                    st.write(f"{plan['details'].get('premium_term_years', 'N/A')} years")
                    
                    st.markdown("<b>Major Illnesses Covered</b>", unsafe_allow_html=True)
                    st.write(f"{plan['details'].get('major_illnesses', 'N/A')}")
                    
                    st.markdown("<b>Early Illnesses Covered</b>", unsafe_allow_html=True)
                    st.write(f"{plan['details'].get('early_illnesses', 'N/A')}")
                
                with col2:
                    st.markdown("<b>Maximum Payout</b>", unsafe_allow_html=True)
                    st.write(f"{plan['details'].get('maximum_payout', 'N/A')}")
                    
                    st.markdown("<b>Waiting Period</b>", unsafe_allow_html=True)
                    st.write(f"{plan['details'].get('waiting_period', 'N/A')}")
                    
                    st.markdown("<b>Issue Age</b>", unsafe_allow_html=True)
                    st.write(f"{plan['details'].get('issue_age', 'N/A')}")
                    
                    st.markdown("<b>Saved On</b>", unsafe_allow_html=True)
                    st.write(f"{plan.get('date_saved', 'Unknown date')}")
                
                # Features section
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("<h3>Key Features</h3>", unsafe_allow_html=True)
                
                if "features" in plan and plan["features"]:
                    for feature in plan["features"]:
                        st.markdown(f"✅ {feature}")
                else:
                    st.write("No features listed for this plan.")
                
                # Action buttons at the bottom
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Compare", key="dialog_compare_btn", use_container_width=True):
                        add_to_comparison(plan['id'])
                        st.toast(f"Added {plan['title']} to comparison", icon="✅")
                        st.session_state.show_dialog = False
                        st.rerun()
                
                with col2:
                    if st.button("Close", key="dialog_close_btn", use_container_width=True):
                        st.session_state.show_dialog = False
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)  # Close card div
                
        else:
            # LIST VIEW
            # Display saved plans grid
            col1, col2 = st.columns(2)
            
            for i, plan in enumerate(saved_plans):
                col = col1 if i % 2 == 0 else col2
                with col:
                    # Create a card container with border
                    with st.container():
                        st.markdown(f"""
                        <div style="border-radius: 12px; padding: 20px; margin-bottom: 20px; position: relative; background-color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <div style="position: absolute; top: 10px; right: 10px; background-color: #1E88E5; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                                Saved
                            </div>
                        """, unsafe_allow_html=True)
                            
                            # Company and plan name - outside the markdown
                        st.markdown(f"""
                            <div style="text-align: center; margin: 10px auto; padding: 10px; font-weight: bold; color: #333; font-size: 18px;">
                                {plan["company"]}
                            </div>
                            <div style="text-align: center; font-size: 20px; font-weight: bold; margin: 15px 0; color: #333;">
                                {plan["title"]}
                            </div>
                            <p style="text-align: center; color: #666; font-size: 14px;">
                                Saved on: {plan.get("date_saved", "Unknown date")}
                            </p>
                        """, unsafe_allow_html=True)
                        
                        # Features section
                        if "features" in plan and plan["features"]:
                            features_html = ""
                            for feature in plan["features"][:2]:
                                features_html += f'<li><span style="color: #4CAF50;">✓</span> {feature}</li>'
                            
                            st.markdown(f"""
                            <ul style="list-style-type: none; padding-left: 20px; margin-bottom: 15px;">
                                {features_html}
                            </ul>
                            """, unsafe_allow_html=True)
                        
                        # Price
                        st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                                <span style="font-size: 1.3rem; font-weight: bold; color: #333;">${plan["price"]}/month</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add buttons to interact with the saved plan
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"View Plan", key=f"view_saved_{plan['id']}", use_container_width=True):
                                # Set dialog state to show this plan
                                st.session_state.show_dialog = True
                                st.session_state.dialog_plan = plan
                                st.rerun()
                        with col_b:
                            if st.button(f"Remove", key=f"remove_{plan['id']}", use_container_width=True):
                                # Remove this saved plan
                                data_manager.remove_saved_plan(plan['id'])
                                st.success(f"{plan['title']} has been removed from your saved plans.")
                                # Refresh the page
                                st.rerun()

# Function to add a plan to comparison
def add_to_comparison(plan_id):
    """Add a plan to the comparison list."""
    plan = data_manager.get_plan_by_id(plan_id)
    if not plan:
        return False
    
    # Check if plan is already in comparison
    if any(p['id'] == plan_id for p in st.session_state.comparison_plans):
        return False
    
    # Limit to 2 plans for comparison
    if len(st.session_state.comparison_plans) >= 2:
        # Remove the oldest plan
        st.session_state.comparison_plans.pop(0)
    
    # Add the plan to comparison
    st.session_state.comparison_plans.append(plan)
    
    return True

# Function to remove a plan from comparison
def remove_from_comparison(plan_id):
    """Remove a plan from the comparison list."""
    st.session_state.comparison_plans = [p for p in st.session_state.comparison_plans if p['id'] != plan_id]
    
    # Hide comparison view if we have less than 2 plans
    if len(st.session_state.comparison_plans) < 2:
        st.session_state.show_comparison = False

# Insurance plans screen
def insurance_plans_screen():
    st.markdown('<h1 class="main-header">Hong Kong Whole Life Insurance Plans</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Explore available whole life insurance plans and filter based on your preferences.</p>', unsafe_allow_html=True)
    
    # Display the heading in Chinese style
    st.markdown('<h2 style="text-align: center; margin: 30px 0; color: #1E88E5;">Compare Whole Life Critical Illness Insurance</h2>', unsafe_allow_html=True)
    
    # Create custom styled filter section with teal background and white text
    st.markdown("""
    <div style="background-color: #4DD0E1; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
    """, unsafe_allow_html=True)
    
    # Create a 3-column layout for filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    # Add custom CSS for the filter buttons
    st.markdown("""
    <style>
    .custom-filter-container {
        margin: 0 5px 20px 5px;
    }
    .filter-dropdown {
        background-color: white;
        border-radius: 30px;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    .filter-icon {
        margin-right: 10px;
        color: #4DD0E1;
    }
    .filter-label {
        font-weight: bold;
        color: #4DD0E1;
        font-size: 14px;
    }
    .filter-value {
        color: #333;
        font-weight: bold;
        font-size: 14px;
        margin-top: 3px;
    }
    .filter-arrow {
        margin-left: auto;
        color: #4DD0E1;
    }
    /* Override Streamlit's selectbox styling */
    div[data-testid="stSelectbox"] > div {
        background-color: white !important;
        border-radius: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with filter_col1:
        # Gender filter
        st.markdown('<div class="custom-filter-container">', unsafe_allow_html=True)
        st.markdown('<div class="filter-label">Gender</div>', unsafe_allow_html=True)
        gender_options = ["Male", "Female"]
        st.session_state.insurance_filters["gender"] = st.selectbox(
            "Gender",
            options=gender_options,
            index=gender_options.index(st.session_state.insurance_filters["gender"]) 
                if st.session_state.insurance_filters["gender"] in gender_options else 0,
            key="filter_gender"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with filter_col2:
        # Age filter
        st.markdown('<div class="custom-filter-container">', unsafe_allow_html=True)
        st.markdown('<div class="filter-label">Age</div>', unsafe_allow_html=True)
        age_options = list(range(18, 81, 1))  # Ages from 18 to 80
        age_index = min(st.session_state.insurance_filters["age"] - 18, len(age_options) - 1) 
        st.session_state.insurance_filters["age"] = st.selectbox(
            "Age",
            options=age_options,
            index=max(0, age_index),
            key="filter_age"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with filter_col3:
        # Smoker status filter
        st.markdown('<div class="custom-filter-container">', unsafe_allow_html=True)
        st.markdown('<div class="filter-label">Smoker Status</div>', unsafe_allow_html=True)
        smoker_options = ["Non Smoker", "Smoker"]
        st.session_state.insurance_filters["smoker_status"] = st.selectbox(
            "Smoker Status",
            options=smoker_options,
            index=smoker_options.index(st.session_state.insurance_filters["smoker_status"]) 
                if st.session_state.insurance_filters["smoker_status"] in smoker_options else 0,
            key="filter_smoker_status"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Helper function to parse score values
    def parse_score(score_value):
        try:
            if isinstance(score_value, (int, float)):
                return float(score_value)
            
            # Convert to string and handle None/empty cases
            score_str = str(score_value or "0")
            
            # Replace "N/A" with "0"
            score_str = score_str.replace("N/A", "0")
            
            # If score contains " / 10", extract the number part
            if "/" in score_str:
                score_str = score_str.split("/")[0].strip()
            
            return float(score_str)
        except (ValueError, TypeError):
            return 0.0
    
    # Get filtered plans
    filtered_plans = data_manager.filter_whole_life_insurance(
        gender=st.session_state.insurance_filters["gender"],
        age=st.session_state.insurance_filters["age"],
        smoker_status=st.session_state.insurance_filters["smoker_status"],
        max_price=st.session_state.insurance_filters["max_price"],
        min_score=st.session_state.insurance_filters["min_score"]
    )
    
    # Remove duplicate plans (same name and company)
    seen_plans = {}
    unique_plans = []
    for plan in filtered_plans:
        plan_key = (plan['company'], plan['title'])
        if plan_key not in seen_plans:
            seen_plans[plan_key] = plan
            unique_plans.append(plan)
        else:
            # If we find a duplicate, keep the one with the higher score
            existing_plan = seen_plans[plan_key]
            new_plan_score = float(plan["details"].get("total_score", 0))
            existing_plan_score = float(existing_plan["details"].get("total_score", 0))
            if new_plan_score > existing_plan_score:
                seen_plans[plan_key] = plan
                unique_plans[unique_plans.index(existing_plan)] = plan
    
    # Replace filtered_plans with unique_plans
    filtered_plans = unique_plans
    
    # Sort plans by score (highest first)
    filtered_plans.sort(key=lambda x: parse_score(x["details"].get("whole_life_score", "0")), reverse=True)
    
    # Display number of found plans
    st.markdown(f"<p style='text-align: center; margin-bottom: 20px; font-size: 1.2rem;'><strong>Found {len(filtered_plans)} matching plans</strong></p>", unsafe_allow_html=True)
    
    # Show comparison banner if plans are selected
    if st.session_state.comparison_plans:
        num_selected = len(st.session_state.comparison_plans)
        st.info(f"{num_selected}/2 plans selected for comparison.")
        
        if st.button("View Comparison", use_container_width=True):
            navigate_to("comparison")
    
    # Display plans
    if not filtered_plans:
        st.warning("No plans match your criteria. Consider adjusting your filters.")
    else:
        # Create a 3-column layout for the cards
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        for i, plan in enumerate(filtered_plans):
            col = columns[i % 3]
            with col:
                # Get scores from the plan details
                whole_life_score = float(plan["details"].get("whole_life_score", 0))
                terms_score = float(plan["details"].get("terms_score", 0))
                total_score = float(plan["details"].get("total_score", 0))
                
                # Format the scores before using in f-string
                formatted_whole_life = f"{whole_life_score:.1f}" if whole_life_score > 0 else "N/A"
                formatted_terms = f"{terms_score:.1f}" if terms_score > 0 else "N/A"
                formatted_total = f"{total_score:.1f}"
                
                # Use Streamlit components instead of raw HTML
                with st.container():
                    # Apply CSS class from style.css
                    st.markdown('<div class="insurance-card">', unsafe_allow_html=True)
                    
                    # Rating circle using plain HTML (this is simpler and more reliable)
                    star_rating = '★★★★★' if total_score >= 9 else '★★★★☆' if total_score >= 7 else '★★★☆☆' if total_score >= 5 else '★★☆☆☆' if total_score >= 3 else '★☆☆☆☆'
                    st.markdown(f"""
                    <div class="card-rating">
                        <span>Star Rating</span>
                        <span>{star_rating}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Company and plan name
                    st.markdown(f'<div class="company-logo">{plan["company"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="plan-name">{plan["title"]}</div>', unsafe_allow_html=True)
                    
                    # Scores
                    st.markdown("<div style='margin: 20px 0;'>", unsafe_allow_html=True)
                    
                    # Total Score
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">Total Score</div>
                        <div class="detail-value">{formatted_total} <span style="font-weight: normal; color: #666;">/10</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Whole Life Score
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">Whole Life CI Coverage Score</div>
                        <div class="detail-value">{formatted_whole_life} <span style="font-weight: normal; color: #666;">/10</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Terms Score
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">Terms Score</div>
                        <div class="detail-value">{formatted_terms} <span style="font-weight: normal; color: #666;">/10</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Annual Premium
                    st.markdown(f"""
                    <div class="premium-row">
                        <div class="premium-label">Annual Premium</div>
                        <div class="premium-value">USD {plan['price'] * 12:.0f} <span style="font-weight: normal; font-size: 14px;">/ Year</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)  # Close insurance-card div
                
                # Add actual Streamlit buttons for functionality
                cols = st.columns(2)
                with cols[0]:
                    # Check if plan is already in comparison
                    is_in_comparison = any(p['id'] == plan['id'] for p in st.session_state.comparison_plans)
                    compare_label = "Selected" if is_in_comparison else "Compare"
                    compare_disabled = is_in_comparison
                    
                    if st.button(compare_label, key=f"compare_btn_{i}_{plan['id']}", 
                               use_container_width=True, disabled=compare_disabled, 
                               help="Add this plan to your comparison list"):
                        if add_to_comparison(plan['id']):
                            st.toast(f"Added {plan['title']} to comparison", icon="✅")
                            st.rerun()
                
                with cols[1]:
                    if st.button("Save Plan", key=f"save_plan_btn_{i}_{plan['id']}", use_container_width=True,
                               help="Save this plan to your saved plans"):
                        # Save the plan using data_manager function
                        data_manager.save_plan(plan['id'])
                        st.toast(f"Saved {plan['title']} to your plans", icon="💾")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Chat", key="insurance_to_chat"):
            navigate_to("chat")
    with col2:
        if st.button("View Saved Plans", key="insurance_to_saved"):
            navigate_to("saved")

# Main function
def main():
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    load_css()
    
    # Display header
    display_header()
    
    # Display navigation sidebar
    display_sidebar()
    
    # Display the appropriate screen based on session state
    if st.session_state.current_screen == "welcome":
        welcome_screen()
    elif st.session_state.current_screen == "profile_setup":
        profile_setup_screen()
    elif st.session_state.current_screen == "chat":
        chat_screen()
    elif st.session_state.current_screen == "insurance_plans":
        insurance_plans_screen()
    elif st.session_state.current_screen == "comparison":
        comparison_screen()
    elif st.session_state.current_screen == "saved":
        saved_plans_screen()

if __name__ == "__main__":
    main() 