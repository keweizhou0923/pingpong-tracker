import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sheets_client import load_sessions, load_technique_log


def render():
    st.header("📊 训练看板")

    sessions = load_sessions()
    tech_log = load_technique_log()

    if sessions.empty:
        st.info("还没有训练记录，去「记录训练」页添加第一条吧！")
        return

    # ── 顶部指标 ──────────────────────────────────────────
    total_sessions = len(sessions)
    total_hours = sessions["duration_min"].sum() / 60
    recent_30 = sessions[sessions["date"] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
    avg_duration = sessions["duration_min"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总训练次数", total_sessions)
    c2.metric("总训练时长", f"{total_hours:.1f} 小时")
    c3.metric("近 30 天次数", len(recent_30))
    c4.metric("平均时长", f"{avg_duration:.0f} 分钟")

    st.divider()

    # ── 出勤趋势 ──────────────────────────────────────────
    st.subheader("📅 出勤趋势")
    sessions_sorted = sessions.sort_values("date")
    fig_trend = px.bar(
        sessions_sorted,
        x="date",
        y="duration_min",
        labels={"date": "日期", "duration_min": "时长（分钟）"},
        color_discrete_sequence=["#2196F3"],
    )
    fig_trend.update_layout(margin=dict(t=20, b=20), height=300)
    st.plotly_chart(fig_trend, use_container_width=True)

    if tech_log.empty:
        return

    st.divider()

    # ── 技术时间分布 ──────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🥧 技术时间分布")
        tech_duration = tech_log.groupby("technique")["duration_min"].sum().reset_index()
        fig_pie = px.pie(
            tech_duration,
            names="technique",
            values="duration_min",
            hole=0.4,
        )
        fig_pie.update_layout(margin=dict(t=20, b=20), height=320, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("⭐ 技术自评分均值")
        tech_rating = tech_log.groupby("technique")["rating"].mean().reset_index()
        tech_rating = tech_rating.sort_values("rating", ascending=True)
        fig_bar = px.bar(
            tech_rating,
            x="rating",
            y="technique",
            orientation="h",
            range_x=[0, 5],
            color="rating",
            color_continuous_scale="RdYlGn",
            labels={"rating": "平均自评分", "technique": "技术"},
        )
        fig_bar.update_layout(margin=dict(t=20, b=20), height=320, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ── 评分趋势（按技术） ────────────────────────────────
    st.subheader("📈 评分趋势")
    merged = tech_log.merge(sessions[["session_id", "date"]], on="session_id")
    merged = merged.sort_values("date")

    techniques_with_data = merged["technique"].unique().tolist()
    selected = st.multiselect("选择技术", techniques_with_data, default=techniques_with_data[:3])

    if selected:
        filtered = merged[merged["technique"].isin(selected)]
        fig_line = px.line(
            filtered,
            x="date",
            y="rating",
            color="technique",
            markers=True,
            range_y=[0.5, 5.5],
            labels={"date": "日期", "rating": "自评分", "technique": "技术"},
        )
        fig_line.update_layout(margin=dict(t=20, b=20), height=320)
        st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # ── 最近记录 ──────────────────────────────────────────
    st.subheader("🕐 最近训练记录")
    n = st.slider("显示最近几次", 3, 20, 5)
    recent = sessions.sort_values("date", ascending=False).head(n)
    st.dataframe(
        recent[["date", "duration_min", "notes"]].rename(
            columns={"date": "日期", "duration_min": "时长（分钟）", "notes": "备注"}
        ),
        use_container_width=True,
        hide_index=True,
    )
