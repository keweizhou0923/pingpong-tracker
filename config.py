TECHNIQUES = [
    "发球",
    "正手攻球",
    "反手攻球",
    "正手拉球",
    "反手拉球",
    "步伐",
    "多球练习",
    "比赛 / 对打",
]

SHEET_SESSIONS = "sessions"
SHEET_TECHNIQUE_LOG = "technique_log"
SHEET_NOTES = "technique_notes"

SESSIONS_COLUMNS = ["session_id", "date", "duration_min", "notes", "created_at"]
TECHNIQUE_COLUMNS = ["log_id", "session_id", "technique", "duration_min", "rating", "notes"]
NOTES_COLUMNS = ["note_id", "title", "technique", "tags", "content", "video_url", "created_at"]

RATING_LABELS = {1: "😞 很差", 2: "😐 一般", 3: "🙂 还行", 4: "😊 不错", 5: "🔥 很好"}
