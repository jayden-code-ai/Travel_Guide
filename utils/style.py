import streamlit as st

def inject_response_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');
        
        /* Default (Light Mode) Variables */
        :root {
            --bg-gradient: linear-gradient(180deg, #fff8f0 0%, #f7f8ff 60%, #fff 100%);
            --hero-bg: rgba(255, 242, 233, 0.9);
            --hero-border: #ffb4a2;
            --hero-shadow: rgba(255, 180, 162, 0.1);
            --text-color: #333333;
            --title-color: #d35400;
            --border-color: #ffb4a2;
            --card-bg: rgba(255, 255, 255, 0.95);
            --card-border: #f1d4c9;
            --card-shadow: rgba(0, 0, 0, 0.05);
            --card-hover-shadow: rgba(255, 180, 162, 0.15);
            --pill-bg: #ffe4c7;
            --pill-text: #d35400;
            --muted-text: #888888;
            --sidebar-bg: #fffbf7;
        }

        /* Dark Mode Overrides - Direct overrides to ensure application */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-gradient: linear-gradient(180deg, #121212 0%, #1e1e24 50%, #121212 100%);
                --hero-bg: rgba(40, 40, 50, 0.95);
                --hero-border: #4a4a5a;
                --hero-shadow: rgba(0, 0, 0, 0.5);
                --text-color: #f0f0f0;
                --title-color: #ffcc80;
                --border-color: #555;
                --card-bg: rgba(30, 30, 40, 0.95);
                --card-border: #444;
                --card-shadow: rgba(0, 0, 0, 0.4);
                --card-hover-shadow: rgba(255, 255, 255, 0.05);
                --pill-bg: #4a3b30;
                --pill-text: #ffcc80;
                --muted-text: #bbbbbb;
                --sidebar-bg: #1e1e24;
            }
            
            /* Force Streamlit App Background to Dark in Dark Mode */
            .stApp {
                background: var(--bg-gradient) !important;
                background-color: #121212 !important; /* Fallback */
            }
            
            /* Force Text Color in Dark Mode */
            html, body, .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {
                color: var(--text-color) !important;
            }
        }
        
        /* Global Font Settings */
        html, body, [class*="css"]  {
            font-family: 'Gowun Dodum', sans-serif;
            color: var(--text-color);
        }

        /* Gradient Background */
        .stApp {
            background: var(--bg-gradient);
            background-attachment: fixed;
        }

        /* Hero Section */
        .hero {
            background: var(--hero-bg);
            border: 2px dashed var(--hero-border);
            padding: 20px 24px;
            border-radius: 16px;
            margin-bottom: 24px;
            text-align: center;
            box-shadow: 0 4px 12px var(--hero-shadow);
        }
        .hero h2 {
            font-family: 'Jua', sans-serif;
            color: var(--title-color) !important;
            margin-bottom: 8px;
        }

        /* Section Titles */
        .section-title {
            font-family: 'Jua', sans-serif;
            font-size: 1.6rem;
            margin-top: 10px;
            margin-bottom: 10px;
            color: var(--text-color) !important;
            border-bottom: 2px solid var(--border-color);
            display: inline-block;
            padding-bottom: 4px;
        }

        /* Schedule Card */
        .schedule-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 16px;
            border-radius: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 12px var(--card-shadow);
            transition: all 0.2s ease-in-out;
        }
        .schedule-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px var(--card-hover-shadow);
        }
        
        .schedule-card h4, .schedule-card h5 {
            color: var(--text-color) !important; 
        }

        /* Pills and Badges */
        .pill {
            display: inline-block;
            background: var(--pill-bg);
            padding: 4px 12px;
            border-radius: 999px;
            margin-right: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--pill-text) !important;
        }
        
        .muted {
            color: var(--muted-text) !important;
            font-size: 0.9rem;
        }

        /* Image Gallery */
        .gallery-img {
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .gallery-img:hover {
            transform: scale(1.02);
        }

        /* Sidebar Customization */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
        }
        
        /* Ensure inputs and other elements are readable in dark mode */
        @media (prefers-color-scheme: dark) {
            .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
                color: #ffffff !important;
                background-color: #2b2b3b !important;
                border-color: #555 !important;
            }
            .stMarkdown div {
                color: var(--text-color) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
