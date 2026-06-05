import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import os

# Base URL of the FastAPI backend
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ─── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PPC AI Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Theme & CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #F7F6F3 !important;
    }

    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1A1917 !important;
    }

    /* File Uploader */
        .stFileUploader,
        .stFileUploader *,
        [data-testid="stFileUploader"],
        [data-testid="stFileUploader"] * {
            background-color: #FFFFFF !important;
            color: #1A1917 !important;
            background-image: none !important;
            box-shadow: none !important;
        }

        .stFileUploader,
        [data-testid="stFileUploader"] {
            border: 1.5px dashed #D4D0C8 !important;
            border-radius: 12px !important;
            padding: 30px !important; /* Margen externo */
            margin-bottom: 20px !important;
        }

    /*  Cards */
    [data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E6E1 !important;
    }
    
    [data-testid="stMetricValue"] > div {
        color: #1A1917 !important;
    }

    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; display: none; }
    /* Floating chat button */        
    [data-testid="stButton"] button {
    position: fixed;
    bottom: 40px;
    right: 40px;
    z-index: 1000;
    border-radius: 50%;
    width: 70px;
    height: 70px;
    font-size: 20px;
    padding: 0;
    background: #3B7DD8;
    color: white;
    border: none;
}
[data-testid="stButton"] button:hover {
    background: #2D5AA8;
}

</style>
""", unsafe_allow_html=True)

# ─── Plotly theme ────────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    font_family="DM Sans",
    font_color="#1A1917",
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=20, r=20, t=40, b=60),
    xaxis=dict(gridcolor="#F0EDE8", linecolor="#E8E6E1", tickfont=dict(size=11, color="#1A1917")),
    yaxis=dict(gridcolor="#F0EDE8", linecolor="#E8E6E1", tickfont=dict(size=11, color="#1A1917")),
    legend=dict(
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#E8E6E1",
        borderwidth=1,
        font=dict(size=16, color="#1A1917"),
    ),
    hoverlabel=dict(
        bgcolor="#1A1917",
        font_color="#FFFFFF",
        font_size=16,
        bordercolor="#1A1917",
    ),
)

C_BLUE   = "#3B7DD8"
C_CORAL  = "#E05C3A"
C_GREEN  = "#2D9B6F"
C_RED    = "#D04040"
C_AMBER  = "#C07B20"
C_MUTED  = "#302F2D"

# ─── Header ─────────────────────────────────────────────────────────────────────
 
st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)
st.title("PPC Ads AI Advisor") # Title of the project
st.write("Upload your campaign data to get AI-powered strategic recommendations")


# ─── Upload section ──────────────────────────────────────────────────────────────
# Two side-by-side file uploaders for Google Ads and Meta Ads CSV exports.
col_g, col_m = st.columns(2)
with col_g:
    uploaded_google = st.file_uploader("Google Ads CSV", type="csv", key="google")
with col_m:
    uploaded_meta = st.file_uploader("Meta Ads CSV", type="csv", key="meta")

st.write("")
st.write("")

# ─── Guard: Nothing uploaded yet ────────────────────────────────────────────────
if uploaded_google is None and uploaded_meta is None:
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; color:#8A8680;">
      <div style="font-size:40px; margin-bottom:1rem;">📂</div>
      <div style="font-size:16px; font-weight:500; color:#4A4845; margin-bottom:0.5rem;">Upload your campaign data to get started</div>
      <div style="font-size:13px;">Supports Google Ads and Meta Ads CSV exports</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Upload logic ────────────────────────────────────────────────────────────────
else:
    current_upload = f"g:{uploaded_google.name if uploaded_google else 'none'}_m:{uploaded_meta.name if uploaded_meta else 'none'}"

    if current_upload != st.session_state.get('last_upload'):
        with st.status("Processing data...", expanded=True) as status:
            try:
                files = []
                if uploaded_google:
                    files.append(('google_file', (uploaded_google.name, uploaded_google.getvalue(), "text/csv")))
                if uploaded_meta:
                    files.append(('meta_file', (uploaded_meta.name, uploaded_meta.getvalue(), "text/csv")))

                response = requests.post(f"{API_URL}/upload-all", files=files)

                if response.status_code == 200:
                    res_data = response.json()
                    status.update(label="✅ Synchronization successful", state="complete", expanded=False)
                    st.toast(f"Success! {res_data['total_rows']} campaigns analyzed.", icon="🚀")
                    st.session_state['data_ready'] = True
                    st.session_state['last_upload'] = current_upload
                else:
                    status.update(label="❌ Backend Error", state="error", expanded=True)
                    st.error(f"Error details: {response.text}")
                    st.stop()
            except Exception as e:
                status.update(label="⚠️ Connection Error", state="error", expanded=True)
                st.error("Could not connect to the server. Is it running?")
                st.stop()

# ─── Dashboard: KPI cards + rankings + charts ────────────────────────────────────
if st.session_state.get('data_ready') and st.session_state.get('last_upload'):
    try:
        # 1. KPI summary cards
        response = requests.get(f"{API_URL}/analytics/kpis")
        
        if response.status_code == 200:
            api_data = response.json()
            
            total_cost   = api_data.get("total_cost", 0)
            avg_roi      = api_data.get("avg_roi", 0)
            n_above_roi  = api_data.get("n_above_roi", 0)
            n_total      = api_data.get("n_total", 0)
            pct_above    = api_data.get("pct_above", 0)
            
            df_top_3 = pd.DataFrame(api_data["rankings"]["top_3"])
            df_bottom_3 = pd.DataFrame(api_data["rankings"]["bottom_3"])

            st.divider()
            st.markdown("### Key metrics")

            def delta_html(text, positive=True):
                color = "#2D9B6F" if positive else "#D04040"
                arrow = "▲" if positive else "▼"
                return f'<span style="font-size:12px;color:{color};">{arrow} {text}</span>'

            top_camp_name = df_top_3.iloc[0]['campaign'] if not df_top_3.empty else 'N/A'
            top_camp_roi = df_top_3.iloc[0]['roi'] if not df_top_3.empty else 0
            
            # Four KPI cards rendered as an HTML grid
            cards_html = f"""
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.5rem;">
                <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
                    <div style="font-size:11px;color:#8A8680;font-weight:500;text-transform:uppercase;margin-bottom:6px;">Total spend</div>
                    <div style="font-size:28px;font-weight:600;color:#1A1917;line-height:1.1;margin-bottom:8px;">€{total_cost/1000:.1f}K</div>
                    {delta_html("vs prev period")}
                </div>
                <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
                    <div style="font-size:11px;color:#8A8680;font-weight:500;text-transform:uppercase;margin-bottom:6px;">Avg. ROI</div>
                    <div style="font-size:28px;font-weight:600;color:#1A1917;line-height:1.1;margin-bottom:8px;">{avg_roi:.1f}%</div>
                    {delta_html("above benchmark", avg_roi > 100)}
                </div>
                <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
                    <div style="font-size:11px;color:#8A8680;font-weight:500;text-transform:uppercase;margin-bottom:6px;">Campaigns above ROI</div>
                    <div style="font-size:28px;font-weight:600;color:#1A1917;line-height:1.1;margin-bottom:8px;">{n_above_roi} / {n_total}</div>
                    <span style="font-size:12px;color:#8A8680;">{pct_above:.0f}% of total</span>
                </div>
                <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
                    <div style="font-size:11px;color:#8A8680;font-weight:500;text-transform:uppercase;margin-bottom:6px;">Top Performance</div>
                    <div style="font-size:18px;font-weight:600;color:#1A1917;line-height:1.2;margin-bottom:8px;">{top_camp_name}</div>
                    <span style="font-size:12px;color:#2D9B6F;font-weight:500;">ROI {top_camp_roi:.1f}%</span>
                </div>
            </div>
            """
            st.markdown(cards_html, unsafe_allow_html=True)

            # Top/bottom campaign ranking tables
            col_top, col_bot = st.columns(2)
            with col_top:
                st.markdown("**Top 3 by ROI** 🏆")
                if not df_top_3.empty:
                    st.dataframe(df_top_3[["campaign", "platform", "roi", "cpl", "cvr"]], hide_index=True, width='stretch')
                else:
                    st.info("No data available")
            
            with col_bot:
                st.markdown("**Bottom 3 by ROI** ⚠️")
                if not df_bottom_3.empty:
                    st.dataframe(df_bottom_3[["campaign", "platform", "roi", "cpl", "cvr"]], hide_index=True, width='stretch')
                else:
                    st.info("No data available")

        # 2. Spend vs Revenue grouped bar chart
        chart_res = requests.get(f"{API_URL}/analytics/charts/spend-vs-revenue")
        if chart_res.status_code == 200:
            st.divider()
            st.markdown("### Spend vs Revenue by campaign")
            df_chart = pd.DataFrame(chart_res.json())

            if not df_chart.empty:
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    name="Spend",
                    x=df_chart["campaign"],
                    y=df_chart["cost"],
                    marker_color=C_CORAL,
                    hovertemplate="<b>%{x}</b><br>Spend: €%{y:,.0f}<extra></extra>",
                ))
                fig_bar.add_trace(go.Bar(
                    name="Revenue",
                    x=df_chart["campaign"],
                    y=df_chart["revenue"],
                    marker_color=C_GREEN,
                    hovertemplate="<b>%{x}</b><br>Revenue: €%{y:,.0f}<extra></extra>",
                ))
                fig_bar.update_layout(
                    **PLOT_LAYOUT,
                    barmode="group",
                    height=380,
                    xaxis_tickangle=-30,
                    yaxis_title="Euros (€)",
                )
                st.plotly_chart(fig_bar, )
            else:
                st.info("No campaign data to display in chart.")

    except Exception as e:
        st.error(f"Error connecting to summary endpoints: {e}")
 
# ─── ROI by campaign + Strategic quadrant (side by side) ─────────────────────────
st.divider()
col_roi, col_quad = st.columns([1, 1], gap="large")

try:
    # 3. Horizontal bar chart — ROI per campaign, color-coded vs average
    res_roi = requests.get(f"{API_URL}/analytics/charts/roi-by-campaign")
    if res_roi.status_code == 200:
        df_roi = pd.DataFrame(res_roi.json())
        
        with col_roi:
            st.markdown("### ROI by campaign")
            roi_avg = df_roi["roi"].mean()
            df_roi_plot = df_roi.sort_values("roi", ascending=True).tail(10) 
            df_roi_plot["color"] = df_roi_plot["roi"].apply(lambda x: C_GREEN if x >= roi_avg else C_RED)

            fig_roi = go.Figure()
            fig_roi.add_trace(go.Bar(
                x=df_roi_plot["roi"],
                y=df_roi_plot["campaign"],
                orientation="h",
                marker_color=df_roi_plot["color"],
                hovertemplate="<b>%{y}</b><br>ROI: %{x:.1f}%<extra></extra>",
            ))
            fig_roi.add_vline(x=roi_avg, line_dash="dash", line_color=C_MUTED, annotation_text=f"Avg {roi_avg:.0f}%")
            fig_roi.update_layout(**PLOT_LAYOUT, height=420, xaxis_title="ROI (%)", yaxis_title="")
            st.plotly_chart(fig_roi, width='stretch')
            st.caption("🟢 Above average ROI  ·  🔴 Below average ROI")

    # 4. Scatter plot — Budget vs ROI strategic quadrants
    res_quad = requests.get(f"{API_URL}/analytics/charts/quadrants")
    if res_quad.status_code == 200:
        df_quadrant = pd.DataFrame(res_quad.json())
        
        with col_quad:
            st.markdown("### Budget vs ROI — strategic quadrants")
            median_spend = df_quadrant["cost"].median()
            median_roi   = df_quadrant["roi"].median()
            color_map = {"meta": C_CORAL, "google": C_BLUE}

            fig_quad = px.scatter(
                df_quadrant, x="cost", y="roi", size="conversions",
                color="platform", color_discrete_map=color_map,
                hover_name="campaign", text="campaign", log_x=True,
                labels={"cost": "Spend (€)", "roi": "ROI (%)"},
            )
            fig_quad.update_traces(textposition="top center", textfont_size=9, marker=dict(opacity=0.8, line=dict(width=1, color="white")))
            fig_quad.add_hline(y=median_roi, line_dash="dash", line_color=C_MUTED, annotation_text="Median ROI")
            fig_quad.add_vline(x=median_spend, line_dash="dot", line_color=C_MUTED, annotation_text="Median Spend")
            fig_quad.update_layout(**PLOT_LAYOUT, height=420)
            st.plotly_chart(fig_quad, width='stretch')
            st.caption("Bubble size = conversions · Top-right = scale up · Bottom-left = pause or test")

except Exception as e:
    st.error(f"Error loading charts: {e}")

# ─── Floating AI chat dialog ──────────────────────────────────────────────────────

@st.dialog("Chat with Marketing Agent")
def show_chat():
    """
    Renders the AI chat dialog powered by the LangChain SQL agent.

    Displays the full conversation history with expandable reasoning logs
    for each assistant response. Submits new queries to the /agent/chat
    endpoint and streams the response back into the dialog.
    """
    st.info("Find insights across your campaigns. Ask about performance, comparisons, or get strategic advice.", icon="💡")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    chat_container = st.container()

    # Render conversation history
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant" and msg.get("thought"):
                    with st.expander("Ver razonamiento previo"):
                        st.markdown(msg["thought"])
                st.write(msg["content"])

    # Handle new user input
    if prompt := st.chat_input("What is the ROI of Google Ads?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            st.chat_message("user").write(prompt)

        with chat_container:
            with st.chat_message("assistant"):
                with st.status("Agent is analyzing data...", expanded=False) as status:
                    try:

                        response = requests.post(f"{API_URL}/agent/chat", json={"query": prompt}, timeout=60)
                        res = response.json()
                        
                        if response.status_code == 200:
                            # Display reasoning steps inside the status box
                            thought = res.get("thought_process", "")
                            if thought:
                                st.markdown(thought)
                            
                            status.update(label="Analysis Complete", state="complete", expanded=False)
                            # Display final answer below the reasoning box
                            answer = res.get("response", "No response")
                            st.markdown(answer)
                            
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": answer,
                                "thought": thought
                            })
                        else:
                            status.update(label="API Error", state="error")
                            st.error(f"Error: {res.get('detail', 'Unknown error')}")

                    except Exception as e:
                        status.update(label="Connection Error", state="error")
                        st.error(f"Could not connect to backend: {e}")

# Floating button that opens the chat dialog
if st.button("💬", type="primary"):
    show_chat()