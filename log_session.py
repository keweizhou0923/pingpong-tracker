import uuid
import datetime
import streamlit as st
from config import TECHNIQUES, RATING_LABELS
from sheets_client import append_session, append_technique_logs, load_sessions, load_technique_log


def render():
    st.header("📝 记录训练")

    with st.form("session_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("训练日期", value=datetime.date.today())
        with col2:
            duration = st.number_input("总时长（分钟）", min_value=1, max_value=480, value=60, step=5)

        custom = st.text_input(
            "自定义技术（可选，多个用逗号分隔）",
            placeholder="例如：侧旋发球, 反手弹击",
        )
        custom_list = [t.strip() for t in custom.split(",") if t.strip()] if custom else []
        all_techniques = TECHNIQUES + custom_list

        selected_techniques = st.multiselect(
            "今天练了哪些技术？",
            options=all_techniques,
            placeholder="可多选...",
        )

        session_notes = st.text_area("整体备注（可选）", placeholder="今天状态、场地、陪练等...")

        tech_data = {}
        if selected_techniques:
            st.divider()
            st.subheader("技术详情")
            for tech in selected_techniques:
                with st.expander(f"🏓 {tech}", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        t_dur = st.number_input(
                            "时长（分钟）", min_value=1, max_value=300, value=15, step=5,
                            key=f"dur_{tech}"
                        )
                    with c2:
                        t_rating = st.select_slider(
                            "自评分",
                            options=[1, 2, 3, 4, 5],
                            value=3,
                            format_func=lambda x: RATING_LABELS[x],
                            key=f"rating_{tech}",
                        )
                    t_notes = st.text_input("备注", placeholder="感受、问题、改进点...", key=f"notes_{tech}")
                    tech_data[tech] = {"duration_min": t_dur, "rating": t_rating, "notes": t_notes}

        submitted = st.form_submit_button("✅ 提交训练记录", use_container_width=True, type="primary")

    if submitted:
        if not selected_techniques:
            st.warning("请至少选择一项技术动作！")
            return

        session_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()

        session_row = {
            "session_id": session_id,
            "date": str(date),
            "duration_min": duration,
            "notes": session_notes,
            "created_at": now,
        }

        tech_rows = [
            {
                "log_id": str(uuid.uuid4()),
                "session_id": session_id,
                "technique": tech,
                "duration_min": data["duration_min"],
                "rating": data["rating"],
                "notes": data["notes"],
            }
            for tech, data in tech_data.items()
        ]

        with st.spinner("保存中..."):
            append_session(session_row)
            append_technique_logs(tech_rows)
            # Clear cache so dashboard reflects new data
            load_sessions.clear()
            load_technique_log.clear()

        st.success(f"✅ 训练记录已保存！共记录 {len(tech_rows)} 项技术。")
        st.balloons()