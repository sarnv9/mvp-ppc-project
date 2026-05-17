import streamlit as st
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.analytics_engine import run_analysis, upload_to_sql
from src.prompt_templates import get_sql_agent
from src.harmonize import harmonize_data


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
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
 
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }
 
  /* Background */
  .stApp { background-color: #F7F6F3; }
 
  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 2rem 3rem 4rem; max-width: 1400px; }
 
  /* Metric cards */
  [data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E8E6E1;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  [data-testid="metric-container"] label {
    font-size: 15px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8A8680 !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 32px;
    font-weight: 600;
    color: #1A1917;
  }
 
  /* Dataframe */
  [data-testid="stDataFrame"] {
    border: 1px solid #E8E6E1;
    border-radius: 10px;
    overflow: hidden;
  }
 
  /* Divider */
  hr { border-color: #E8E6E1; margin: 2rem 0; }
 
  /* Section headers */
  h2, h3 { 
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: #1A1917 !important;
    letter-spacing: -0.02em;
  }
 
  /* File uploader */
  [data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1.5px dashed #D4D0C8;
    border-radius: 12px;
    padding: 1rem;
  }
 
  /* Chat input */
  [data-testid="stChatInput"] {
    border-radius: 12px;
    border: 1px solid #E8E6E1;
    background: #FFFFFF;
  }
 
  /* Buttons */
  .stButton > button {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    border-radius: 8px;
    border: 1px solid #D4D0C8;
    background: #FFFFFF;
    color: #1A1917;
    transition: all 0.15s ease;
  }
  .stButton > button:hover {
    background: #F0EDE8;
    border-color: #B8B4AC;
  }
 
  /* Status/toast */
  .stAlert {
    border-radius: 10px;
    border: 1px solid #E8E6E1;
  }
 
  /* Caption text */
  .stCaption { color: #8A8680; font-size: 18px; }
 
  /* Expanders */
  [data-testid="stExpander"] {
    border: 1px solid #E8E6E1 !important;
    border-radius: 10px !important;
    background: #FFFFFF;
  }
</style>
""", unsafe_allow_html=True)

# ─── Plotly theme ────────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    font_family="DM Sans",
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=20, r=20, t=40, b=60),
    xaxis=dict(gridcolor="#F0EDE8", linecolor="#E8E6E1", tickfont_size=11),
    yaxis=dict(gridcolor="#F0EDE8", linecolor="#E8E6E1", tickfont_size=11),
    legend=dict(
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#E8E6E1",
        borderwidth=1,
        font_size=16,
    ),
    hoverlabel=dict(
        bgcolor="#1A1917",
        font_color="#F7F6F3",
        font_size=16,
        bordercolor="#1A1917",
    ),
)
 
# Coherent color palette
C_BLUE   = "#3B7DD8"
C_CORAL  = "#E05C3A"
C_GREEN  = "#2D9B6F"
C_RED    = "#D04040"
C_AMBER  = "#C07B20"
C_MUTED  = "#8A8680"

# ─── Header ─────────────────────────────────────────────────────────────────────
 
st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

st.title("PPC Ads AI Advisor") # Title of the project
st.write("Upload your campaign data to get AI-powered strategic recommendations")


# ─── Upload section ──────────────────────────────────────────────────────────────
col_g, col_m = st.columns(2)
with col_g:
    uploaded_google = st.file_uploader("Google Ads CSV", type="csv", key="google")
with col_m:
    uploaded_meta = st.file_uploader("Meta Ads CSV", type="csv", key="meta")

# ─── Guard: nothing uploaded ─────────────────────────────────────────────────────
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

google_df = pd.read_csv(uploaded_google) if uploaded_google is not None else None
meta_df = pd.read_csv(uploaded_meta) if uploaded_meta is not None else None

if google_df is not None or meta_df is not None:
    df = harmonize_data(google_df, meta_df)

    st.write("Running analysis...")
    result = run_analysis(df)
    df = result["df"]
    st.write("Analysis complete! (Results below)")

    with st.status("Syncing with PostgreSQL database...", expanded=True) as status:
        st.write("Verifying connection...")
        try:
            success = upload_to_sql(df)
            if success:
                status.update(label="✅ Synchronization successful", state="complete", expanded=False)
                st.toast("Data saved to Postgres", icon="🗄️")
            else:
                status.update(label="⚠️ Connection unavailable", state="error", expanded=False)
        except Exception as e:
            status.update(label="⚠️ Connection unavailable", state="error", expanded=False)
            st.info("Running without database. Configure PostgreSQL in .env to sync data.")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


    # KPI Summary cards

    st.divider()
    st.markdown("### Key metrics")

    # ── compute values ───────────────────────────────────────────────────────────
    total_cost        = float(df["cost"].sum())
    total_revenue     = float(df["revenue"].sum())
    avg_roi           = float(df["roi"].mean())
    n_above_roi       = int((df.groupby("campaign")["roi"].mean() >= avg_roi).sum())
    n_total           = df["campaign"].nunique()
    pct_above         = n_above_roi / n_total * 100
    top_campaign      = df.groupby("campaign")["roi"].mean().idxmax()
    top_roi           = df.groupby("campaign")["roi"].mean().max()

    # ── helper: delta badge ───────────────────────────────────────────────────────
    def delta_html(text, positive=True):
        color = "var(--color-text-success)" if positive else "var(--color-text-danger)"
        arrow = "▲" if positive else "▼"
        return f'<span style="font-size:12px;color:{color};">{arrow} {text}</span>'

    # ── 4 cards via HTML ──────────────────────────────────────────────────────────
    cards_html = f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.5rem;">

    <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
        <div style="font-size:11px;color:#8A8680;font-weight:500;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Total spend</div>
        <div style="font-size:28px;font-weight:600;color:#1A1917;line-height:1.1;margin-bottom:8px;">€{total_cost/1000:.0f}K</div>
        {delta_html("vs prev period")}
    </div>

    <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
        <div style="font-size:11px;color:#8A8680;font-weight:500;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Avg. ROI</div>
        <div style="font-size:28px;font-weight:600;color:#1A1917;line-height:1.1;margin-bottom:8px;">{avg_roi:.0f}%</div>
        {delta_html("above benchmark", avg_roi > 100)}
    </div>

    <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
        <div style="font-size:11px;color:#8A8680;font-weight:500;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Campaigns above ROI</div>
        <div style="font-size:28px;font-weight:600;color:#1A1917;line-height:1.1;margin-bottom:8px;">{n_above_roi} / {n_total}</div>
        <span style="font-size:12px;color:#8A8680;">{pct_above:.0f}% of total</span>
    </div>

    <div style="background:#fff;border:1px solid #E8E6E1;border-radius:12px;padding:1.25rem 1.5rem;">
        <div style="font-size:11px;color:#8A8680;font-weight:500;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Top campaign</div>
        <div style="font-size:18px;font-weight:600;color:#1A1917;line-height:1.2;margin-bottom:8px;">{top_campaign}</div>
        <span style="font-size:12px;color:#2D9B6F;font-weight:500;">ROI {top_roi:.0f}%</span>
    </div>

    </div>
    """
    st.markdown(cards_html, unsafe_allow_html=True)

    col_top, col_bot = st.columns(2)
    with col_top:
        st.markdown("**Top 3 by ROI** 🏆")
        st.dataframe(result["top_roi"][["campaign", "platform", "roi", "roas", "cvr", "cpl"]],
        width='content',
        hide_index=True,
    )
 
    with col_bot:
        st.markdown("**Bottom 3 by ROI** ⚠️")
        st.dataframe(
        result["bottom_roi"][["campaign", "platform", "roi", "cpc", "cvr", "cpl"]],
        width='content',
        hide_index=True,
    )
# ════════════════════════════════════════════════════════════════════════════════
# 3. SPEND vs REVENUE bar chart
# ════════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("### Spend vs Revenue by campaign")
 
df_grouped = (
    df.groupby("campaign")
    .agg({"cost": "sum", "revenue": "sum"})
    .reset_index()
    .sort_values("revenue", ascending=False)
    .head(10)
)
 
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Spend",
    x=df_grouped["campaign"],
    y=df_grouped["cost"],
    marker_color=C_CORAL,
    hovertemplate="<b>%{x}</b><br>Spend: €%{y:,.0f}<extra></extra>",
))
fig_bar.add_trace(go.Bar(
    name="Revenue",
    x=df_grouped["campaign"],
    y=df_grouped["revenue"],
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
st.plotly_chart(fig_bar, width='stretch')
 
# ════════════════════════════════════════════════════════════════════════════════
# 4. ROI by Campaign  +  Budget vs ROI Quadrant  (side by side)
# ════════════════════════════════════════════════════════════════════════════════
st.divider()
 
col_roi, col_quad = st.columns([1, 1], gap="large")
 
# ── ROI horizontal bar ───────────────────────────────────────────────────────
with col_roi:
    st.markdown("### ROI by campaign")
 
    df_roi_grouped = (
        df.groupby(["campaign", "platform"])
        .agg({"cost": "sum", "revenue": "sum"})
        .reset_index()
    )
    df_roi_grouped["roi"] = (
        (df_roi_grouped["revenue"] - df_roi_grouped["cost"])
        / df_roi_grouped["cost"] * 100
    )
    roi_avg = df_roi_grouped["roi"].mean()
    df_roi_grouped = df_roi_grouped.sort_values("roi", ascending=True).head(10)
    df_roi_grouped["color"] = df_roi_grouped["roi"].apply(
        lambda x: C_GREEN if x >= roi_avg else C_RED
    )
 
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Bar(
        x=df_roi_grouped["roi"],
        y=df_roi_grouped["campaign"],
        orientation="h",
        marker_color=df_roi_grouped["color"],
        hovertemplate="<b>%{y}</b><br>ROI: %{x:.1f}%<extra></extra>",
    ))
    fig_roi.add_vline(
        x=roi_avg,
        line_dash="dash",
        line_color=C_MUTED,
        line_width=1.5,
        annotation_text=f"Avg {roi_avg:.0f}%",
        annotation_font_size=11,
        annotation_font_color=C_MUTED,
    )
    fig_roi.update_layout(
        **PLOT_LAYOUT,
        height=420,
        xaxis_title="ROI (%)",
        yaxis_title="",
    )
    st.plotly_chart(fig_roi, width='content')
    st.caption("🟢 Above average ROI  ·  🔴 Below average ROI")
 
# ── Budget vs ROI scatter ────────────────────────────────────────────────────
with col_quad:
    st.markdown("### Budget vs ROI — strategic quadrants")
 
    df_quadrant = (
        df.groupby(["campaign", "platform"])
        .agg({"cost": "sum", "revenue": "sum", "conversions": "sum"})
        .reset_index()
    )
    df_quadrant["roi"] = (
        (df_quadrant["revenue"] - df_quadrant["cost"])
        / df_quadrant["cost"] * 100
    )
    median_spend = df_quadrant["cost"].median()
    median_roi   = df_quadrant["roi"].median()
 
    color_map = {"meta": C_CORAL, "google": C_BLUE}
 
    fig_quad = px.scatter(
        df_quadrant,
        x="cost",
        y="roi",
        size="conversions",
        color="platform",
        color_discrete_map=color_map,
        hover_name="campaign",
        text="campaign",
        log_x=True,
        labels={"cost": "Spend (€)", "roi": "ROI (%)"},
    )
    fig_quad.update_traces(
        textposition="top center",
        textfont_size=9,
        textfont_color="#4A4845",
        marker=dict(opacity=0.8, line=dict(width=1, color="white")),
    )
    fig_quad.add_hline(
        y=median_roi,
        line_dash="dash",
        line_color=C_MUTED,
        line_width=1.5,
        annotation_text="Median ROI",
        annotation_font_size=10,
        annotation_font_color=C_MUTED,
        annotation_position="right",
    )
    fig_quad.add_vline(
        x=median_spend,
        line_dash="dot",
        line_color=C_MUTED,
        line_width=1.5,
        annotation_text="Median Spend",
        annotation_font_size=10,
        annotation_font_color=C_MUTED,
        annotation_position="top",
    )
    fig_quad.update_layout(**PLOT_LAYOUT, height=420)
    st.plotly_chart(fig_quad, width='content')
    st.caption("Bubble size = conversions · Top-right = scale up · Bottom-left = pause or test")

# ════════════════════════════════════════════════════════════════════════════════
# ASK THE DASHBOARD 

@st.dialog("Chat with Marketing Agent")
def show_chat():
    st.info("Find insights across your campaigns. Ask about performance, comparisons, or get strategic advice.", icon="💡")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("What is the ROI of Google Ads?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            
            try:
                agent = get_sql_agent()
                full_response = agent.invoke(
                    {"input": prompt},
                    {"callbacks": [st_callback]}
                )
                response = full_response["output"]
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")

# Floating button
st.markdown("""
<style>
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

if st.button("💬"):
    show_chat()