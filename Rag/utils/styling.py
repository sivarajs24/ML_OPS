import streamlit as st

def apply_glassmorphism():
    """
    Applies custom structural CSS for a clean, minimalistic theme.
    Colors are now natively handled by .streamlit/config.toml to prevent visibility issues.
    """
    st.markdown(
        """
        <style>
        /* Clean Minimalist Cards (Structural only, colors handled by config) */
        .glass-card {
            background-color: var(--background-color);
            border-radius: 8px;
            border: 1px solid rgba(0,0,0,0.1);
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
            transition: box-shadow 0.2s ease-in-out;
        }
        
        .glass-card:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        /* Typography spacing (Colors handled by config) */
        h1, h2, h3, h4, h5, h6 {
            letter-spacing: -0.025em;
        }

        /* Subheaders inside cards */
        .glass-card h3 {
            margin-top: 0;
            margin-bottom: 16px;
            font-size: 1.25rem;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            padding-bottom: 8px;
        }
        
        /* Lists inside cards */
        .glass-card ul {
            padding-left: 20px;
        }
        
        .glass-card li {
            margin-bottom: 8px;
        }
        
        /* Minor fixes for standard UI */
        div[data-testid="stExpander"] {
            border-radius: 8px !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
