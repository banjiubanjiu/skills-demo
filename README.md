# Sports Recover

运动损伤康复助手（Gradio 应用）。

## 目录结构
- `app.py`: Gradio 主入口。
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

## 配置文件（config.local.yaml）
在项目根目录创建 `config.local.yaml`，启动时会自动读取：
```yaml
api_key: "your_api_key"
base_url: "https://open.bigmodel.cn/api/anthropic"
model: "glm-4.7"
max_tokens: 1200
max_image_bytes: 8000000
```
也支持环境变量覆盖（优先级更高）：
- `ANTHROPIC_API_KEY` 或 `ZHIPUAI_API_KEY`
- `BIGMODEL_BASE_URL`
- `BIGMODEL_MODEL`
- `BIGMODEL_MAX_TOKENS`
- `BIGMODEL_MAX_IMAGE_BYTES`

## 依赖管理
- 依赖在 `pyproject.toml` 中维护。
- 更新依赖后运行 `uv sync` 以刷新本地环境与 `uv.lock`。

## 说明
- 本项目提供运动损伤康复相关的教育性建议，不构成医疗诊断或治疗。
- 若需接入外部模型或配置密钥，请使用本地 `config.local.yaml`（已在 `.gitignore` 中忽略）。
