# Sports Recover

运动损伤康复助手（Gradio 应用）。

## 目录结构
- `app.py`: Gradio 主入口。
- `web/`: 静态页面资源（`index.html`、`styles.css`、`script.js`）。
- `data/`: 资料库与抓取内容。
  - `data/knowledge/`: PDF 等医学/康复参考资料。
  - `data/rehab-docs/`: 抓取的网页原文与清洗文本。
- `dist/`: 构建或打包输出目录（按需生成）。
- `.claude/`: 本地运行配置（通常不需要改动）。

## 运行方式（uv）
1. 创建并激活虚拟环境：
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```
2. 安装依赖（会生成/更新 `uv.lock`）：
   ```bash
   uv sync
   ```
3. 启动服务：
   ```bash
   uv run python app.py
   ```

## 依赖管理
- 依赖在 `pyproject.toml` 中维护。
- 更新依赖后运行 `uv sync` 以刷新本地环境与 `uv.lock`。

## 说明
- 本项目提供运动损伤康复相关的教育性建议，不构成医疗诊断或治疗。
- 若需接入外部模型或配置密钥，请使用本地 `config.local.yaml`（已在 `.gitignore` 中忽略）。

## 本地预览（静态页）
```bash
python -m http.server 8000
```
然后打开 `http://localhost:8000/web/index.html`。
