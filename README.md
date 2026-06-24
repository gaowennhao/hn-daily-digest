# Hacker News 每日中文摘要（GitHub Actions）

这个仓库每天在 GitHub 云端执行，不依赖你的电脑开机。

## 工作流程

1. 抓取东京时区昨天发布的 Hacker News stories。
2. 按采集时 points 排序，取前 30。
3. 获取每篇帖子的代表性评论。
4. 调用 OpenAI API 生成中文摘要。
5. 通过 SMTP 发送 HTML 邮件。
6. 将本次生成结果保留为 GitHub Actions Artifact 14 天。

定时：每天 08:07，时区 Asia/Tokyo。

## 需要配置的 Repository Secrets

必须：

- `OPENAI_API_KEY`：OpenAI API Key
- `SMTP_USERNAME`：Gmail 发件地址，例如 `yourname@gmail.com`
- `SMTP_PASSWORD`：Gmail 应用专用密码，不是 Gmail 登录密码
- `MAIL_TO`：收件地址；多个地址用逗号分隔

可选：

- `OPENAI_MODEL`：默认 `gpt-5.4-mini`
- `SMTP_HOST`：默认 `smtp.gmail.com`
- `SMTP_PORT`：默认 `465`
- `MAIL_FROM`：默认等于 `SMTP_USERNAME`

## 第一次运行

在 GitHub 仓库打开：

Actions → Hacker News Daily Digest → Run workflow

第一次设置：

- `target_date` 留空
- `send_email` 保持关闭

运行成功后，进入该次运行页面，在 Artifacts 下载生成结果，
打开 `digest.html` 检查。

第二次把 `send_email` 打开，验证邮箱投递。

## 文件

- `hn_digest.py`：抓取 HN 数据
- `generate_digest.py`：调用 OpenAI 生成摘要和 HTML
- `send_email.py`：发送邮件
- `.github/workflows/daily-digest.yml`：GitHub Actions 定时流程

## Top 30 口径

“昨天 Top 30”定义为：

东京时区昨天 00:00–24:00 发布的 HN stories，
按今天采集时的 points 降序排列，取前 30。

它不是历史首页快照。

## 安全注意

- 不要把 API Key 或邮箱密码写入任何代码文件。
- 仓库建议设为 Private。
- 外部标题、帖子和评论会被视为不可信数据，提示词明确禁止执行其中指令。
- 建议为自动发送创建一个专用 Gmail 地址。
