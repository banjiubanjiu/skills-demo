import base64
import mimetypes
import os
from pathlib import Path
from typing import Iterable, List


def _strip_unsupported_proxy_env() -> None:
    for key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        value = os.getenv(key, "")
        if value.startswith(("socks://", "socks5://", "socks5h://")):
            os.environ.pop(key, None)


_strip_unsupported_proxy_env()

DEFAULT_UI_LANGUAGE = os.getenv("GRADIO_DEFAULT_LANGUAGE", "zh-CN")


def _set_gradio_language_env() -> None:
    os.environ.setdefault("GRADIO_LANGUAGE", DEFAULT_UI_LANGUAGE)
    os.environ.setdefault("GRADIO_LANG", DEFAULT_UI_LANGUAGE)


_set_gradio_language_env()

import gradio as gr
import yaml
from claude_agent_sdk import query, ClaudeAgentOptions

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = Path(os.getenv("RECOVERY_CONFIG_PATH", PROJECT_ROOT / "config.local.yaml"))
DEFAULT_CONFIG = {
    "api_key": "",
    "base_url": "https://open.bigmodel.cn/api/anthropic",
    "model": "glm-4.7",
    "max_tokens": 1200,
    "max_image_bytes": 8000000,
}

SYSTEM_PROMPT = """You are a sports injury rehab assistant for athletes.
You provide educational guidance only and are not a medical professional.
Respond in Simplified Chinese.

Priorities:
- Phased rehab plan with progression criteria.
- Risk warnings and red flags.
- Educational clinical advice (possible causes, imaging considerations).
- Return-to-sport checkpoints.

Safety:
- Do not provide definitive diagnosis or medication dosing.
- If red flags exist, lead with urgent guidance to seek in-person care.

Use the Skill tool when relevant. Only surface bigmodel-claude-compat when the user asks about API or SDK compatibility.
If the user request is to conduct an interview or ask follow-up questions, output questions only and do not provide a plan yet.
Use Markdown with clear headings and concise bullets.
"""


def _apply_gradio_language() -> None:
    try:
        from gradio.i18n import set_language

        set_language(DEFAULT_UI_LANGUAGE)
    except Exception:
        try:
            i18n = getattr(gr, "i18n", None)
            if i18n and hasattr(i18n, "set_language"):
                i18n.set_language(DEFAULT_UI_LANGUAGE)
        except Exception:
            pass


_apply_gradio_language()

CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Rubik+Mono+One&display=swap');

:root {
  --bg: #0b0f14;
  --panel: #121a25;
  --ink: #f7f7f2;
  --muted: #9fb0c5;
  --accent: #1ef7a3;
  --accent-2: #f5c542;
  --danger: #ff3e5b;
  --grid: rgba(247, 247, 242, 0.06);
  --body-text-color: var(--ink);
  --body-text-color-subdued: var(--muted);
  --background-fill-primary: #0f1621;
  --background-fill-secondary: #0b0f14;
  --border-color-primary: #2b3a4f;
  --block-label-text-color: var(--ink);
  --block-title-text-color: var(--ink);
  --block-info-text-color: var(--muted);
  --input-background-fill: #0f1621;
  --color-accent: var(--accent);
  --color-accent-soft: rgba(30, 247, 163, 0.2);
  --checkbox-border-width: 2px;
  --checkbox-border-radius: 999px;
  --checkbox-border-color: #2b3a4f;
  --checkbox-border-color-hover: #3a4c63;
  --checkbox-border-color-focus: var(--accent);
  --checkbox-border-color-selected: var(--accent);
  --checkbox-background-color: #0f1621;
  --checkbox-background-color-hover: #172233;
  --checkbox-background-color-focus: #172233;
  --checkbox-background-color-selected: #0f1621;
  --checkbox-shadow: none;
  --radio-circle: radial-gradient(circle at 50% 50%, #1ef7a3 0 45%, transparent 50%);
  --checkbox-check: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 10'%3E%3Cpath fill='%23ffffff' d='M4.2 7.3L1.4 4.5l-1 1L4.2 9.3 11.6 1.9l-1-1z'/%3E%3C/svg%3E");
  --checkbox-label-text-color: var(--ink);
  --checkbox-label-text-color-selected: var(--ink);
  --checkbox-label-background-fill: rgba(15, 22, 33, 0.7);
  --checkbox-label-background-fill-hover: rgba(23, 34, 51, 0.9);
  --checkbox-label-background-fill-selected: rgba(30, 247, 163, 0.12);
  --checkbox-label-border-color: #2b3a4f;
  --checkbox-label-border-color-selected: var(--accent);
  --checkbox-label-border-width: 2px;
  --checkbox-label-padding: 6px 10px;
  --checkbox-label-gap: 8px;
}

body, .gradio-container {
  background: radial-gradient(circle at 10% 10%, #1b2533 0%, #0b0f14 40%) !important;
  color: var(--ink) !important;
  font-family: "JetBrains Mono", monospace !important;
}

.gradio-container,
.gradio-container * {
  color: var(--ink);
}

.gradio-container {
  border: 3px solid var(--accent);
  box-shadow: 12px 12px 0 #0a1019, 24px 24px 0 rgba(30, 247, 163, 0.2);
  position: relative;
  padding: 20px;
  overflow: hidden;
  isolation: isolate;
}

.gradio-container:before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
  opacity: 0.5;
  z-index: 0;
}

.gradio-container > * {
  position: relative;
  z-index: 1;
}

.hero {
  position: relative;
  z-index: 1;
  border: 2px solid var(--accent);
  padding: 18px 20px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, rgba(30, 247, 163, 0.16), rgba(18, 26, 37, 0.9));
}

.hero-title {
  font-family: "Rubik Mono One", sans-serif;
  font-size: clamp(22px, 3.2vw, 42px);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.hero-sub {
  color: var(--muted);
  margin-top: 8px;
  max-width: 720px;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.hero-tag {
  border: 2px solid var(--accent-2);
  padding: 4px 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

button, .gr-button {
  border: 2px solid var(--accent) !important;
  background: #0b111a !important;
  color: var(--ink) !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}

input, textarea, select, .gr-input, .gr-text-input, .gr-text-area, .gr-dropdown {
  border: 2px solid #2b3a4f !important;
  background: #0f1621 !important;
  color: var(--ink) !important;
}

input[type="radio"],
input[type="checkbox"] {
  accent-color: var(--accent);
  cursor: pointer;
}

label {
  cursor: pointer;
}

.required label::after,
.required .block-label::after,
.required .label::after,
.required .field-label::after {
  content: " *";
  color: var(--danger);
  margin-left: 4px;
}

label[data-testid$="-radio-label"],
label[data-testid$="-checkbox-label"] {
  display: inline-flex;
  align-items: center;
  gap: var(--checkbox-label-gap);
  padding: var(--checkbox-label-padding);
  border-radius: 999px;
  border: var(--checkbox-label-border-width) solid var(--checkbox-label-border-color);
  background: var(--checkbox-label-background-fill);
  color: var(--checkbox-label-text-color);
}

label[data-testid$="-radio-label"].selected,
label[data-testid$="-checkbox-label"].selected {
  border-color: var(--checkbox-label-border-color-selected);
  background: var(--checkbox-label-background-fill-selected);
  color: var(--checkbox-label-text-color-selected);
}

input::placeholder,
textarea::placeholder {
  color: var(--muted) !important;
  opacity: 0.75;
}

select option {
  background: #0f1621;
  color: var(--ink);
}

.gr-chatbot .message {
  border: 2px solid var(--accent);
  background: rgba(18, 26, 37, 0.85);
  box-shadow: 6px 6px 0 rgba(30, 247, 163, 0.2);
}

.gr-chatbot .message.user {
  border-color: var(--accent-2);
}

.disclaimer {
  border: 2px dashed var(--danger);
  padding: 10px 12px;
  color: var(--muted);
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}
"""

SYMPTOM_OPTIONS = [
    "肿胀",
    "关节不稳",
    "卡住/绞锁",
    "麻木或刺痛",
    "明显畸形",
    "开放性伤口或出血",
    "发热或寒战",
    "头部受伤相关症状",
    "无法负重",
]

RED_FLAG_SYMPTOMS = {
    "明显畸形",
    "开放性伤口或出血",
    "发热或寒战",
    "头部受伤相关症状",
    "无法负重",
    "麻木或刺痛",
}


def _load_config_file() -> tuple[dict, str | None]:
    if not CONFIG_PATH.exists():
        return {}, None
    try:
        raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return {}, f"Config read failed: {exc}"
    if not isinstance(raw, dict):
        return {}, "Config must be a YAML mapping."
    return raw, None


def _parse_int(value: object, fallback: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return fallback


def _runtime_config() -> dict:
    config, _ = _load_config_file()
    merged = DEFAULT_CONFIG.copy()
    merged.update(config)
    env_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ZHIPUAI_API_KEY")
    if env_key:
        merged["api_key"] = env_key
    if os.getenv("BIGMODEL_BASE_URL"):
        merged["base_url"] = os.getenv("BIGMODEL_BASE_URL")
    if os.getenv("BIGMODEL_MODEL"):
        merged["model"] = os.getenv("BIGMODEL_MODEL")
    if os.getenv("BIGMODEL_MAX_TOKENS"):
        merged["max_tokens"] = _parse_int(os.getenv("BIGMODEL_MAX_TOKENS"), merged["max_tokens"])
    if os.getenv("BIGMODEL_MAX_IMAGE_BYTES"):
        merged["max_image_bytes"] = _parse_int(
            os.getenv("BIGMODEL_MAX_IMAGE_BYTES"),
            merged["max_image_bytes"],
        )
    merged["max_tokens"] = _parse_int(merged.get("max_tokens"), DEFAULT_CONFIG["max_tokens"])
    merged["max_image_bytes"] = _parse_int(
        merged.get("max_image_bytes"),
        DEFAULT_CONFIG["max_image_bytes"],
    )
    return merged




def _format_list(values: Iterable[str]) -> str:
    cleaned = [value for value in values if value]
    return "、".join(cleaned) if cleaned else "未报告"


def _normalize_history(history: List) -> List[List[str]]:
    if not history:
        return []
    first = history[0]
    if isinstance(first, dict):
        normalized = []
        pending_user = None
        for item in history:
            role = item.get("role")
            content = item.get("content", "")
            if role == "user":
                if pending_user is not None:
                    normalized.append([pending_user, ""])
                pending_user = content
            elif role == "assistant":
                if pending_user is None:
                    normalized.append(["", content])
                else:
                    normalized.append([pending_user, content])
                    pending_user = None
        if pending_user is not None:
            normalized.append([pending_user, ""])
        return normalized
    normalized = []
    for item in history:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            normalized.append([item[0], item[1]])
    return normalized


def _build_intake(
    sport: str,
    injury_region: str,
    injury_type: str,
    onset_type: str,
    time_since: str,
    pain_score: int,
    symptoms: List[str],
    image_path: str,
    training_goal: str,
    training_phase: str,
    prior_injury: str,
    treatment_done: str,
    notes: str,
) -> str:
    symptom_text = _format_list(symptoms)
    red_flags = sorted(RED_FLAG_SYMPTOMS.intersection(symptoms or []))
    red_flags_text = _format_list(red_flags)
    image_status = "是" if image_path else "否"
    lines = [
        f"运动项目: {sport or '未填写'}",
        f"伤处: {injury_region or '未填写'}",
        f"损伤类型: {injury_type or '未填写'}",
        f"起病方式: {onset_type or '未填写'}",
        f"受伤时长: {time_since or '未填写'}",
        f"疼痛评分(0-10): {pain_score}",
        f"症状: {symptom_text}",
        f"问诊红旗: {red_flags_text}",
        f"已上传图片: {image_status}",
        f"训练阶段: {training_phase or '未填写'}",
        f"训练目标: {training_goal or '未填写'}",
        f"既往伤史: {prior_injury or '无'}",
        f"已尝试处理: {treatment_done or '无'}",
        f"补充说明: {notes or '无'}",
    ]
    return "\n".join(lines)


def _get_api_key() -> str:
    return str(_runtime_config().get("api_key", "")).strip()


def _build_image_payload(
    image_path: str | None,
    max_bytes: int,
) -> tuple[dict | None, str | None]:
    if not image_path:
        return None, None
    try:
        if not os.path.exists(image_path):
            return None, "未找到图片路径，将继续进行但不使用图片。"
        size = os.path.getsize(image_path)
        if size > max_bytes:
            return None, "图片过大，将继续进行但不使用图片。"
        media_type = mimetypes.guess_type(image_path)[0]
        if not media_type or not media_type.startswith("image/"):
            return None, "不支持的图片格式，请上传 PNG 或 JPG。"
        with open(image_path, "rb") as handle:
            data = base64.b64encode(handle.read()).decode("ascii")
        payload = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": data,
            },
        }
        return payload, None
    except Exception:
        return None, "图片加载失败，将继续进行但不使用图片。"


def _build_messages(
    history: List[List[str]],
    user_message: str,
    image_payload: dict | None = None,
) -> List[dict]:
    messages: List[dict] = []
    for user_text, assistant_text in (history or [])[-6:]:
        if user_text:
            messages.append({"role": "user", "content": user_text})
        if assistant_text:
            messages.append({"role": "assistant", "content": assistant_text})
    if image_payload:
        content = [{"type": "text", "text": user_message}, image_payload]
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": user_message})
    if messages and messages[0]["role"] == "assistant":
        messages.insert(0, {"role": "user", "content": "已提供基础信息，请开始问诊。"})
    return messages


def _extract_response_text(response: object) -> str:
    content = getattr(response, "content", None)
    if not content:
        return ""
    parts = []
    for block in content:
        text = getattr(block, "text", None)
        if isinstance(text, str):
            parts.append(text)
        elif isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "".join(parts).strip()


def _strip_images_from_messages(messages: List[dict]) -> List[dict]:
    stripped = []
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "".join(text_parts).strip()
        stripped.append({"role": message.get("role", "user"), "content": content})
    return stripped


def _message_content_to_text(content: object) -> str:
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts).strip()
    if content is None:
        return ""
    return str(content).strip()


def _messages_to_prompt(system_prompt: str, messages: List[dict]) -> str:
    lines = [system_prompt.strip(), "", "Conversation:"]
    for message in messages:
        role = message.get("role", "user")
        content = _message_content_to_text(message.get("content", ""))
        if not content:
            continue
        lines.append(f"{role.capitalize()}: {content}")
    lines.append("Assistant:")
    return "\n".join(lines).strip()




async def _run_agent(
    system_prompt: str,
    messages: List[dict],
    had_image: bool,
) -> str:
    config = _runtime_config()
    api_key = str(config.get("api_key", "")).strip()
    if api_key and not os.getenv("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = api_key
    if config.get("base_url") and not os.getenv("ANTHROPIC_BASE_URL"):
        os.environ["ANTHROPIC_BASE_URL"] = str(config.get("base_url"))
    if config.get("model") and not os.getenv("ANTHROPIC_MODEL"):
        os.environ["ANTHROPIC_MODEL"] = str(config.get("model"))
    if config.get("max_tokens") and not os.getenv("ANTHROPIC_MAX_TOKENS"):
        os.environ["ANTHROPIC_MAX_TOKENS"] = str(
            _parse_int(config.get("max_tokens"), DEFAULT_CONFIG["max_tokens"])
        )

    prompt_messages = _strip_images_from_messages(messages) if had_image else messages
    if had_image:
        system_prompt = (
            f"{system_prompt}\n\nNote: Image inputs are omitted; provide text-only guidance."
        )
    prompt = _messages_to_prompt(system_prompt, prompt_messages)

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        setting_sources=["project", "user"],
        allowed_tools=["Skill"],
    )

    chunks: list[str] = []
    async for event in query(prompt=prompt, options=options):
        if isinstance(event, str):
            chunks.append(event)
            continue
        content = getattr(event, "content", None)
        if isinstance(content, str):
            chunks.append(content)
            continue
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    text_part = block.get("text")
                else:
                    text_part = getattr(block, "text", None)
                if isinstance(text_part, str):
                    parts.append(text_part)
            if parts:
                chunks.append("".join(parts))
            continue
        text_part = getattr(event, "text", None)
        if isinstance(text_part, str):
            chunks.append(text_part)

    output = "".join(chunks).strip()
    return output or "未收到模型回复。"



async def respond(
    message: str,
    history: List[List[str]],
    sport: str,
    injury_region: str,
    injury_type: str,
    onset_type: str,
    time_since: str,
    pain_score: int,
    symptoms: List[str],
    injury_image: str,
    training_goal: str,
    training_phase: str,
    prior_injury: str,
    treatment_done: str,
    notes: str,
) -> str:
    if not _get_api_key():
        return "缺少 API Key。请设置 ANTHROPIC_API_KEY 或在 config.local.yaml 中填写 api_key。"

    normalized_history = _normalize_history(history or [])
    intake = _build_intake(
        sport,
        injury_region,
        injury_type,
        onset_type,
        time_since,
        pain_score,
        symptoms or [],
        injury_image or "",
        training_goal,
        training_phase,
        prior_injury,
        treatment_done,
        notes,
    )
    config = _runtime_config()
    image_payload, image_note = _build_image_payload(
        injury_image,
        _parse_int(config.get("max_image_bytes"), DEFAULT_CONFIG["max_image_bytes"]),
    )
    user_message = f"""运动员基本信息:
{intake}

用户诉求:
{message}
"""
    if image_note:
        user_message = f"{user_message}\n\n图片提示: {image_note}"
    system_prompt = SYSTEM_PROMPT
    messages = _build_messages(normalized_history, user_message, image_payload)
    return await _run_agent(system_prompt, messages, had_image=bool(image_payload))


def build_app() -> gr.Blocks:
    with gr.Blocks(css=CSS) as demo:
        gr.HTML(
            """
            <div class="hero">
              <div class="hero-title">康复指挥台</div>
              <div class="hero-sub">
                面向运动员的运动损伤康复助手：阶段化计划、风险红旗与临床提示，
                协助更安全地重返运动。
              </div>
              <div class="hero-tags">
                <span class="hero-tag">阶段计划</span>
                <span class="hero-tag">风险红旗</span>
                <span class="hero-tag">临床提示</span>
                <span class="hero-tag">回归标准</span>
              </div>
            </div>
            """
        )
        gr.Markdown(
            "本工具仅用于科普教育，不能替代线下面诊。",
            elem_classes=["disclaimer"],
        )


        def _toggle_steps(step: int):
            return (
                gr.update(visible=step == 1),
                gr.update(visible=step == 2),
                gr.update(visible=step == 3),
            )

        def _missing_required_fields(
            sport: str,
            injury_region: str,
            injury_type: str,
            onset_type: str,
            time_since: str,
            training_goal: str,
        ) -> List[str]:
            missing = []
            if not sport or not sport.strip():
                missing.append("运动项目")
            if not injury_region:
                missing.append("伤处")
            if not injury_type or not injury_type.strip():
                missing.append("损伤类型")
            if not onset_type:
                missing.append("起病方式")
            if not time_since or not time_since.strip():
                missing.append("受伤时长")
            if not training_goal or not training_goal.strip():
                missing.append("训练目标")
            return missing

        def _validate_step1(
            sport: str,
            injury_region: str,
            injury_type: str,
            onset_type: str,
            time_since: str,
            training_goal: str,
        ):
            missing = _missing_required_fields(
                sport,
                injury_region,
                injury_type,
                onset_type,
                time_since,
                training_goal,
            )
            if missing:
                note = "请完成必填项：" + "、".join(missing)
                return gr.update(interactive=False), gr.update(value=note, visible=True)
            return gr.update(interactive=True), gr.update(value="", visible=False)

        async def _send_message(
            message: str,
            history: List[dict],
            sport: str,
            injury_region: str,
            injury_type: str,
            onset_type: str,
            time_since: str,
            pain_score: int,
            symptoms: List[str],
            injury_image: str,
            training_goal: str,
            training_phase: str,
            prior_injury: str,
            treatment_done: str,
            notes: str,
        ):
            if not message.strip():
                return history, history, ""
            interview_note = (
                "继续问诊，只提出 1 个追问问题，不要给出方案。"
            )
            response = await respond(
                f"{interview_note}\n\nUser answer: {message}",
                history,
                sport,
                injury_region,
                injury_type,
                onset_type,
                time_since,
                pain_score,
                symptoms,
                injury_image,
                training_goal,
                training_phase,
                prior_injury,
                treatment_done,
                notes,
            )
            updated = (history or []) + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response},
            ]
            return updated, updated, ""

        async def _enter_step2(
            sport: str,
            injury_region: str,
            injury_type: str,
            onset_type: str,
            time_since: str,
            pain_score: int,
            symptoms: List[str],
            injury_image: str,
            training_goal: str,
            training_phase: str,
            prior_injury: str,
            treatment_done: str,
            notes: str,
        ):
            missing = _missing_required_fields(
                sport,
                injury_region,
                injury_type,
                onset_type,
                time_since,
                training_goal,
            )
            if missing:
                note = "请完成必填项：" + "、".join(missing)
                return (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(interactive=False),
                    gr.update(value=note, visible=True),
                    [],
                    [],
                    "",
                )
            interview_prompt = (
                "你将开始问诊。基于已提供的信息，提出1个高价值追问问题，"
                "只输出一个问题，不要给出诊疗方案。"
            )
            response = await respond(
                interview_prompt,
                [],
                sport,
                injury_region,
                injury_type,
                onset_type,
                time_since,
                pain_score,
                symptoms,
                injury_image,
                training_goal,
                training_phase,
                prior_injury,
                treatment_done,
                notes,
            )
            initial_history = [{"role": "assistant", "content": response}]
            return (
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(interactive=True),
                gr.update(value="", visible=False),
                initial_history,
                initial_history,
                "",
            )

        async def _generate_plan(
            history: List[dict],
            sport: str,
            injury_region: str,
            injury_type: str,
            onset_type: str,
            time_since: str,
            pain_score: int,
            symptoms: List[str],
            injury_image: str,
            training_goal: str,
            training_phase: str,
            prior_injury: str,
            treatment_done: str,
            notes: str,
        ):
            if not history:
                return "暂无问诊记录，请返回第 2 步先完成问诊。"
            has_user_reply = any(
                item.get("role") == "user" and str(item.get("content", "")).strip()
                for item in history
            )
            if not has_user_reply:
                return "暂无问诊回答，请返回第 2 步先完成追问。"
            plan_request = (
                "基于问诊信息生成最终的阶段化康复计划与临床建议，"
                "包含进阶标准、回归运动清单与清晰的风险红旗。"
                "如存在红旗症状，先给出紧急就医提示。"
            )
            return await respond(
                plan_request,
                history,
                sport,
                injury_region,
                injury_type,
                onset_type,
                time_since,
                pain_score,
                symptoms,
                injury_image,
                training_goal,
                training_phase,
                prior_injury,
                treatment_done,
                notes,
            )

        step1_group = gr.Group(visible=True)
        step2_group = gr.Group(visible=False)
        step3_group = gr.Group(visible=False)

        with step1_group:
            gr.Markdown("第 1 步：信息采集与上传")
            validation_note = gr.Markdown(visible=False)
            sport = gr.Textbox(
                label="运动项目",
                placeholder="例如：足球、篮球",
                elem_classes=["required"],
            )
            injury_region = gr.Dropdown(
                label="伤处",
                choices=[
                    "踝关节",
                    "膝关节",
                    "髋部",
                    "下背部",
                    "肩部",
                    "肘部",
                    "手腕或手",
                    "足部",
                    "腘绳肌",
                    "股四头肌",
                    "小腿",
                    "颈部",
                    "其他",
                ],
                value="膝关节",
                elem_classes=["required"],
            )
            injury_type = gr.Textbox(
                label="损伤类型",
                placeholder="例如：扭伤、拉伤",
                elem_classes=["required"],
            )
            onset_type = gr.Radio(
                label="起病方式",
                choices=["急性外伤", "过度使用", "不确定"],
                value="急性外伤",
                elem_classes=["required"],
            )
            time_since = gr.Textbox(
                label="受伤时长",
                placeholder="例如：2 天、3 周",
                elem_classes=["required"],
            )
            pain_score = gr.Slider(label="疼痛评分", minimum=0, maximum=10, value=4, step=1)
            symptoms = gr.CheckboxGroup(label="症状", choices=SYMPTOM_OPTIONS)
            injury_image = gr.Image(
                label="可选图片（PNG/JPG）",
                type="filepath",
                height=160,
            )
            training_goal = gr.Textbox(
                label="训练目标",
                placeholder="例如：6 周内回归比赛",
                elem_classes=["required"],
            )
            training_phase = gr.Dropdown(
                label="训练阶段",
                choices=["赛季中", "休赛期", "季前备战", "回归训练"],
                value="赛季中",
            )
            prior_injury = gr.Textbox(label="既往伤史", placeholder="可选")
            treatment_done = gr.Textbox(label="已尝试处理", placeholder="例如：休息、冰敷")
            notes = gr.Textbox(
                label="影像/报告摘要或补充说明",
                lines=3,
                placeholder="例如：MRI 结论或医生建议",
            )
            to_step2 = gr.Button("第 2 步：开始问诊", interactive=False)


        with step2_group:
            gr.Markdown("第 2 步：问诊")
            chat_history = gr.State([])
            chat = gr.Chatbot(height=360)
            chat_input = gr.Textbox(
                placeholder="请回答追问，或补充具体问题...",
                lines=3,
            )
            with gr.Row():
                send_btn = gr.Button("发送")
                back_to_step1 = gr.Button("返回信息采集")
                to_step3 = gr.Button("第 3 步：生成方案")

        with step3_group:
            gr.Markdown("第 3 步：方案与建议")
            plan_output = gr.Markdown()
            with gr.Row():
                back_to_step2 = gr.Button("返回问诊")
                regenerate_plan = gr.Button("重新生成方案")

        intake_inputs = [
            sport,
            injury_region,
            injury_type,
            onset_type,
            time_since,
            pain_score,
            symptoms,
            injury_image,
            training_goal,
            training_phase,
            prior_injury,
            treatment_done,
            notes,
        ]
        required_inputs = [
            sport,
            injury_region,
            injury_type,
            onset_type,
            time_since,
            training_goal,
        ]

        send_btn.click(
            _send_message,
            inputs=[chat_input, chat_history] + intake_inputs,
            outputs=[chat, chat_history, chat_input],
        )
        chat_input.submit(
            _send_message,
            inputs=[chat_input, chat_history] + intake_inputs,
            outputs=[chat, chat_history, chat_input],
        )

        for comp in required_inputs:
            comp.change(
                _validate_step1,
                inputs=required_inputs,
                outputs=[to_step2, validation_note],
            )


        to_step2.click(
            _enter_step2,
            inputs=intake_inputs,
            outputs=[
                step1_group,
                step2_group,
                step3_group,
                to_step2,
                validation_note,
                chat,
                chat_history,
                chat_input,
            ],
        )
        back_to_step1.click(
            lambda: _toggle_steps(1),
            outputs=[step1_group, step2_group, step3_group],
        )
        back_to_step2.click(
            lambda: _toggle_steps(2),
            outputs=[step1_group, step2_group, step3_group],
        )
        to_step3.click(
            _generate_plan,
            inputs=[chat_history] + intake_inputs,
            outputs=[plan_output],
        )
        to_step3.click(
            lambda: _toggle_steps(3),
            outputs=[step1_group, step2_group, step3_group],
        )
        regenerate_plan.click(
            _generate_plan,
            inputs=[chat_history] + intake_inputs,
            outputs=[plan_output],
        )
    return demo


if __name__ == "__main__":
    build_app().launch(share=True)
