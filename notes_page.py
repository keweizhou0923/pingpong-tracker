import uuid
import datetime
import streamlit as st
from config import TECHNIQUES
from sheets_client import append_note, delete_note, load_notes


def render():
    st.header("📚 技术笔记")

    tab_browse, tab_add = st.tabs(["🔍 浏览 / 搜索", "✏️ 新增笔记"])

    # ── 新增笔记 ──────────────────────────────────────────
    with tab_add:
        with st.form("note_form"):
            title = st.text_input("标题", placeholder="例如：正手拉球发力要点")
            technique = st.selectbox("关联技术", ["不限"] + TECHNIQUES)
            tags = st.text_input("标签（逗号分隔）", placeholder="例如：发力, 击球点, 教练建议")
            content = st.text_area("笔记内容", placeholder="写下技术要点、注意事项、训练心得...", height=200)
            video_url = st.text_input("视频链接（可选）", placeholder="https://youtube.com/...")
            submitted = st.form_submit_button("💾 保存笔记", use_container_width=True, type="primary")

        if submitted:
            if not title:
                st.warning("请填写标题！")
            else:
                row = {
                    "note_id": str(uuid.uuid4()),
                    "title": title,
                    "technique": technique if technique != "不限" else "",
                    "tags": tags,
                    "content": content,
                    "video_url": video_url,
                    "created_at": datetime.datetime.now().isoformat(),
                }
                with st.spinner("保存中..."):
                    append_note(row)
                    load_notes.clear()
                st.success("✅ 笔记已保存！")

    # ── 浏览 / 搜索 ───────────────────────────────────────
    with tab_browse:
        notes = load_notes()

        if notes.empty:
            st.info("还没有笔记，去「新增笔记」添加第一条吧！")
            return

        # 搜索和筛选
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            keyword = st.text_input("🔍 搜索", placeholder="搜标题 / 内容 / 标签...")
        with col2:
            tech_filter = st.selectbox("技术分类", ["全部"] + TECHNIQUES)
        with col3:
            # 收集所有标签
            all_tags = set()
            for t in notes["tags"].dropna():
                for tag in str(t).split(","):
                    tag = tag.strip()
                    if tag:
                        all_tags.add(tag)
            tag_filter = st.selectbox("标签", ["全部"] + sorted(all_tags))

        # 应用筛选
        filtered = notes.copy()
        if keyword:
            kw = keyword.lower()
            filtered = filtered[
                filtered["title"].str.lower().str.contains(kw, na=False) |
                filtered["content"].str.lower().str.contains(kw, na=False) |
                filtered["tags"].str.lower().str.contains(kw, na=False)
            ]
        if tech_filter != "全部":
            filtered = filtered[filtered["technique"] == tech_filter]
        if tag_filter != "全部":
            filtered = filtered[filtered["tags"].str.contains(tag_filter, na=False)]

        st.caption(f"共 {len(filtered)} 条笔记")

        # 展示笔记
        for _, row in filtered.sort_values("created_at", ascending=False).iterrows():
            with st.expander(f"📝 {row['title']}", expanded=False):
                cols = st.columns([3, 1])
                with cols[0]:
                    if row.get("technique"):
                        st.caption(f"🏓 {row['technique']}")
                    if row.get("tags"):
                        tags_list = [f"`{t.strip()}`" for t in str(row["tags"]).split(",") if t.strip()]
                        st.markdown(" ".join(tags_list))
                with cols[1]:
                    if st.button("🗑️ 删除", key=f"del_{row['note_id']}"):
                        delete_note(row["note_id"])
                        load_notes.clear()
                        st.rerun()

                st.markdown(row.get("content", ""))

                if row.get("video_url"):
                    st.markdown(f"🎬 [观看视频]({row['video_url']})")
                    # 尝试嵌入 YouTube
                    url = str(row["video_url"])
                    if "youtube.com/watch?v=" in url:
                        vid_id = url.split("v=")[-1].split("&")[0]
                        st.video(f"https://www.youtube.com/watch?v={vid_id}")
                    elif "youtu.be/" in url:
                        vid_id = url.split("youtu.be/")[-1].split("?")[0]
                        st.video(f"https://www.youtube.com/watch?v={vid_id}")
