import streamlit as st

def inject_response_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');
        
        /* :root Variables for Light Mode (Default) */
        :root {
            --bg-gradient: linear-gradient(180deg, #fff8f0 0%, #f7f8ff 60%, #fff 100%);
            --hero-bg: rgba(255, 242, 233, 0.9);
            --hero-border: #ffb4a2;
            --hero-shadow: rgba(255, 180, 162, 0.1);
            --text-color: #333;
            --title-color: #d35400;
            --border-color: #ffb4a2;
            --card-bg: rgba(255, 255, 255, 0.95);
            --card-border: #f1d4c9;
            --card-shadow: rgba(0, 0, 0, 0.05);
            --card-hover-shadow: rgba(255, 180, 162, 0.15);
            --pill-bg: #ffe4c7;
            --pill-text: #d35400;
            --muted-text: #888;
            --sidebar-bg: #fffbf7;
        }

        /* Dark Mode Overrides */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-gradient: linear-gradient(180deg, #1e1e24 0%, #2a2a35 60%, #121212 100%);
                --hero-bg: rgba(40, 40, 50, 0.9);
                --hero-border: #4a4a5a;
                --hero-shadow: rgba(0, 0, 0, 0.3);
                --text-color: #e0e0e0;
                --title-color: #ffcc80;
                --border-color: #555;
                --card-bg: rgba(45, 45, 55, 0.95);
                --card-border: #444;
                --card-shadow: rgba(0, 0, 0, 0.2);
                --card-hover-shadow: rgba(255, 255, 255, 0.05);
                --pill-bg: #4a3b30;
                --pill-text: #ffcc80;
                --muted-text: #aaa;
                --sidebar-bg: #1e1e24;
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
            color: var(--title-color);
            margin-bottom: 8px;
        }

        /* Section Titles */
        .section-title {
            font-family: 'Jua', sans-serif;
            font-size: 1.6rem;
            margin-top: 10px;
            margin-bottom: 10px;
            color: var(--text-color);
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
            color: var(--pill-text);
        }
        
        .muted {
            color: var(--muted-text);
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

        /* Sidebar Customization (if not using option-menu) */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
