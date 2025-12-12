import streamlit as st

def app_shell(title: str, subtitle: str):
    st.set_page_config(page_title=title, page_icon="🧠", layout="wide")

    st.markdown(
        """
        <style>
          .cc-wrap {
            padding: 16px 18px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(34,211,238,0.10));
            border: 1px solid rgba(231,234,240,0.08);
          }
          .cc-title { font-size: 24px; font-weight: 800; letter-spacing: 0.2px; }
          .cc-sub   { opacity: 0.86; margin-top: 4px; }
          .cc-chip  { display:inline-block; padding:6px 10px; border-radius: 999px;
                      border:1px solid rgba(231,234,240,0.10); margin-top:10px; font-size:12px; opacity:0.9; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="cc-wrap">
          <div class="cc-title">{title}</div>
          <div class="cc-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
