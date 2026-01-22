import streamlit as st

def inject_response_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');
        
        /* Global Font Settings */
        html, body, [class*="css"]  {
            font-family: 'Gowun Dodum', sans-serif;
        }

        /* Gradient Background */
        .stApp {
            background: linear-gradient(180deg, #fff8f0 0%, #f7f8ff 60%, #fff 100%);
        }

        /* Hero Section */
        .hero {
            background: rgba(255, 242, 233, 0.9);
            border: 2px dashed #ffb4a2;
            padding: 20px 24px;
            border-radius: 16px;
            margin-bottom: 24px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(255, 180, 162, 0.1);
        }
        .hero h2 {
            font-family: 'Jua', sans-serif;
            color: #d35400;
            margin-bottom: 8px;
        }

        /* Section Titles */
        .section-title {
            font-family: 'Jua', sans-serif;
            font-size: 1.6rem;
            margin-top: 10px;
            margin-bottom: 10px;
            color: #333;
            border-bottom: 2px solid #ffb4a2;
            display: inline-block;
            padding-bottom: 4px;
        }

        /* Schedule Card */
        .schedule-card {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #f1d4c9;
            padding: 16px;
            border-radius: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease-in-out;
        }
        .schedule-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(255, 180, 162, 0.15);
        }

        /* Pills and Badges */
        .pill {
            display: inline-block;
            background: #ffe4c7;
            padding: 4px 12px;
            border-radius: 999px;
            margin-right: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #d35400;
        }
        
        .muted {
            color: #888;
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
            background-color: #fffbf7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
