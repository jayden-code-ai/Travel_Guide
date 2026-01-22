import streamlit as st

def inject_response_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');
        
        /* 기본 (라이트 모드) 변수 */
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

        /* 다크 모드 재정의 - 적용 보장을 위한 직접 재정의 */
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
            
            /* 다크 모드에서 Streamlit 앱 배경 강제 어둡게 설정 */
            .stApp {
                background: var(--bg-gradient) !important;
                background-color: #121212 !important; /* Fallback */
            }
            
            /* 다크 모드에서 텍스트 색상 강제 설정 */
            html, body, .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {
                color: var(--text-color) !important;
            }
        }
        
        /* 전역 폰트 설정 */
        html, body, [class*="css"]  {
            font-family: 'Gowun Dodum', sans-serif;
            color: var(--text-color);
        }

        /* 그라데이션 배경 */
        .stApp {
            background: var(--bg-gradient);
            background-attachment: fixed;
        }

        /* 히어로 섹션 */
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

        /* 섹션 제목 */
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

        /* 일정 카드 */
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

        /* 알약 및 배지 스타일 */
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

        /* 이미지 갤러리 */
        .gallery-img {
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .gallery-img:hover {
            transform: scale(1.02);
        }

        /* 사이드바 커스터마이징 */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
        }
        
        /* 다크 모드에서 입력 필드 및 기타 요소 가독성 확보 */
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
        
        <script>
        // 모바일 사이드바 자동 닫기 스크립트
        function closeSidebarOnMobile() {
            const menuLinks = parent.document.querySelectorAll('[data-testid="stSidebarNav"] a, .nav-link');
            menuLinks.forEach(link => {
                link.addEventListener('click', () => {
                    // 화면 너비가 768px 이하(모바일)일 때만 실행
                    if (parent.window.innerWidth <= 768) {
                        try {
                            const closeBtn = parent.document.querySelector('[data-testid="stSidebar"] button[kind="secondary"]');
                            if (closeBtn) {
                                closeBtn.click();
                            } else {
                                // 닫기 버튼을 찾을 수 없는 경우(이미 닫혀있거나 다른 구조), data-testid="stSidebar"의 상태 확인 후 닫기 시도 (X 버튼이 보통 첫번째 버튼)
                                const sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
                                // React props 접근이 어려우므로 버튼 클릭 시뮬레이션이 가장 확실
                                const toggleBtn = parent.document.querySelector('[data-testid="baseButton-header"]'); // 모바일 상단 햄버거 메뉴/닫기 버튼
                                if(toggleBtn && sidebar && getComputedStyle(sidebar).transform === "none") {
                                     // 열려있는 상태라면 토글 버튼 클릭 (닫기)
                                    toggleBtn.click();
                                }
                            }
                        } catch (e) {
                            console.log("Sidebar auto-close failed", e);
                        }
                    }
                });
            });
            
            // streamlit-option-menu 특성상 iframe 내부에서 동작할 수 있으므로, 
            // 상위 window의 이벤트를 감지하거나 반복적으로 리스너를 붙여야 할 수 있음.
            // 여기서는 간단히 로드 시점과 일정 주기마다 리스너 부착 시도
        }
        
        // DOM 로드 완료 시 실행
        setTimeout(closeSidebarOnMobile, 1000); 
        // 동적 렌더링 대응을 위해 3초 후 한번 더 실행
        setTimeout(closeSidebarOnMobile, 3000);
        </script>
        """,
        unsafe_allow_html=True,
    )
