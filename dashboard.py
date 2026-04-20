import streamlit as st
import pandas as pd
import plotly.express as px
from sheets_client import load_sessions, load_technique_log
import datetime


def render():
    st.header("📊 训练看板")

    sessions = load_sessions()
    tech_log = load_technique_log()

    if sessions.empty:
        st.info("还没有训练记录，去「记录训练」页添加第一条吧！")
        return

    # ── 时间段筛选 ────────────────────────────────────────
    today = pd.Timestamp.today().normalize()
    col_filter, col_custom = st.columns([2, 3])

    with col_filter:
        period = st.radio(
            "时间段",
            ["本周", "本月", "近3个月", "全部", "自定义"],
            horizontal=True,
        )

    if period == "本周":
        start = today - pd.Timedelta(days=today.dayofweek)
        end = today
    elif period == "本月":
        start = today.replace(day=1)
        end = today
    elif period == "近3个月":
        start = today - pd.Timedelta(days=90)
        end = today
    elif period == "全部":
        start = sessions["date"].min()
        end = today
    else:  # 自定义
        with col_custom:
            date_range = st.date_input(
                "选择范围",
                value=(today - pd.Timedelta(days=30), today),
                max_value=today,
            )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        else:
            start, end = sessions["date"].min(), today

    # 筛选数据
    mask = (sessions["date"] >= start) & (sessions["date"] <= end)
    sessions_f = sessions[mask]

    if sessions_f.empty:
        st.warning("该时间段内没有训练记录。")
        return

    tech_log_f = tech_log[tech_log["session_id"].isin(sessions_f["session_id"])]

    # ── 顶部指标 ──────────────────────────────────────────
    total_sessions = len(sessions_f)
    total_hours = sessions_f["duration_min"].sum() / 60
    avg_duration = sessions_f["duration_min"].mean()
    days_span = max((end - start).days, 1)
    freq = total_sessions / (days_span / 7)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("训练次数", total_sessions)
    c2.metric("总时长", f"{total_hours:.1f} 小时")
    c3.metric("平均时长", f"{avg_duration:.0f} 分钟")
    c4.metric("训练频率", f"{freq:.1f} 次/周")

    st.divider()

    # ── 出勤趋势 ──────────────────────────────────────────
    st.subheader("📅 出勤趋势")
    sessions_sorted = sessions_f.sort_values("date")
    fig_trend = px.bar(
        sessions_sorted,
        x="date",
        y="duration_min",
        labels={"date": "日期", "duration_min": "时长（分钟）"},
        color_discrete_sequence=["#2196F3"],
    )
    fig_trend.update_layout(margin=dict(t=20, b=20), height=300)
    st.plotly_chart(fig_trend, use_container_width=True)

    if tech_log_f.empty:
        return

    st.divider()

    # ── 技术时间分布 ──────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🥧 技术时间分布")
        tech_duration = tech_log_f.groupby("technique")["duration_min"].sum().reset_index()
        fig_pie = px.pie(
            tech_duration,
            names="technique",
            values="duration_min",
            hole=0.4,
        )
        fig_pie.update_layout(margin=dict(t=20, b=20), height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("⭐ 技术自评分均值")
        tech_rating = tech_log_f.groupby("technique")["rating"].mean().reset_index()
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

    # ── 评分趋势 ──────────────────────────────────────────
    st.subheader("📈 评分趋势")
    merged = tech_log_f.merge(sessions_f[["session_id", "date"]], on="session_id")
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

    # ── 训练记录 ──────────────────────────────────────────
    st.subheader("🕐 训练记录")
    recent = sessions_f.sort_values("date", ascending=False)
    st.dataframe(
        recent[["date", "duration_min", "notes"]].rename(
            columns={"date": "日期", "duration_min": "时长（分钟）", "notes": "备注"}
        ),
        use_container_width=True,
        hide_index=True,
    )
