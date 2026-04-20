# 🏓 乒乓球训练追踪系统

## 快速启动

### 1. GCP 配置

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目 → 启用 **Google Sheets API** 和 **Google Drive API**
3. 创建 **Service Account** → 下载 JSON 密钥文件
4. 创建一个新的 Google Sheet，把 Sheet 的 URL 中间那段 ID 复制下来
5. 在 Google Sheet 的共享设置中，将 Service Account 的邮箱（`xxx@xxx.iam.gserviceaccount.com`）添加为**编辑者**

### 2. 本地配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 secrets
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# 编辑 secrets.toml，填入 spreadsheet_id 和 GCP Service Account 信息
```

### 3. 本地运行

```bash
streamlit run app.py
```

### 4. 部署到 Streamlit Cloud（手机可访问）

1. 将项目推送到 GitHub（注意：**不要提交** `secrets.toml`，加入 `.gitignore`）
2. 前往 [share.streamlit.io](https://share.streamlit.io) 连接 GitHub 仓库
3. 在 Streamlit Cloud 的 App Settings → Secrets 中粘贴 `secrets.toml` 内容
4. 部署完成后获得公开 URL，手机直接访问

## 文件结构

```
pingpong_tracker/
├── app.py                  # 主入口
├── config.py               # 技术列表、常量
├── sheets_client.py        # Google Sheets 读写
├── log_session.py          # 记录训练页面
├── dashboard.py            # 训练看板页面
├── requirements.txt
└── .streamlit/
    └── secrets.toml        # 本地密钥（不提交 git）
```

## .gitignore

```
.streamlit/secrets.toml
credentials.json
__pycache__/
*.pyc
```
