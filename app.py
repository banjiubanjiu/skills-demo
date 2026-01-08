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
    "swelling",
    "instability",
    "locking or catching",
    "numbness or tingling",
    "visible deformity",
    "open wound or bleeding",
    "fever or chills",
    "head injury symptoms",
    "unable to bear weight",
]

RED_FLAG_SYMPTOMS = {
    "visible deformity",
    "open wound or bleeding",
    "fever or chills",
    "head injury symptoms",
    "unable to bear weight",
    "numbness or tingling",
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
    return ", ".join(cleaned) if cleaned else "none reported"


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
    image_status = "yes" if image_path else "no"
    lines = [
        f"Sport: {sport or 'unspecified'}",
        f"Injury region: {injury_region or 'unspecified'}",
        f"Injury type: {injury_type or 'unspecified'}",
        f"Onset: {onset_type or 'unspecified'}",
        f"Time since injury: {time_since or 'unspecified'}",
        f"Pain score (0-10): {pain_score}",
        f"Symptoms: {symptom_text}",
        f"Red flags from intake: {red_flags_text}",
        f"Image uploaded: {image_status}",
        f"Training phase: {training_phase or 'unspecified'}",
        f"Training goal: {training_goal or 'unspecified'}",
        f"Prior injury: {prior_injury or 'none'}",
        f"Treatments tried: {treatment_done or 'none'}",
        f"Notes: {notes or 'none'}",
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
            return None, "Image path not found; proceeding without image."
        size = os.path.getsize(image_path)
        if size > max_bytes:
            return None, "Image too large; proceeding without image."
        media_type = mimetypes.guess_type(image_path)[0]
        if not media_type or not media_type.startswith("image/"):
            return None, "Unsupported image type; please upload PNG or JPG."
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
        return None, "Image could not be loaded; proceeding without image."


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
    return output or "No response received from the model."



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
        return "Missing API key. Set ANTHROPIC_API_KEY or add api_key in config.local.yaml."

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
    user_message = f"""Athlete intake:
{intake}

User request:
{message}
"""
    if image_note:
        user_message = f"{user_message}\n\nImage note: {image_note}"
    system_prompt = SYSTEM_PROMPT
    messages = _build_messages(normalized_history, user_message, image_payload)
    return await _run_agent(system_prompt, messages, had_image=bool(image_payload))


def build_app() -> gr.Blocks:
    with gr.Blocks(css=CSS) as demo:
        gr.HTML(
            """
            <div class="hero">
              <div class="hero-title">Recovery Ops</div>
              <div class="hero-sub">
                Athlete-focused sports injury rehab assistant. Phased plans, red flags,
                and clinical guidance for safer return-to-sport decisions.
              </div>
              <div class="hero-tags">
                <span class="hero-tag">Phase Plan</span>
                <span class="hero-tag">Risk Flags</span>
                <span class="hero-tag">Clinical Notes</span>
                <span class="hero-tag">Return Criteria</span>
              </div>
            </div>
            """
        )
        gr.Markdown(
            "This tool is for education only and not a substitute for medical care.",
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
                missing.append("Sport")
            if not injury_region:
                missing.append("Injury region")
            if not injury_type or not injury_type.strip():
                missing.append("Injury type")
            if not onset_type:
                missing.append("Onset type")
            if not time_since or not time_since.strip():
                missing.append("Time since injury")
            if not training_goal or not training_goal.strip():
                missing.append("Training goal")
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
                note = "Complete required fields: " + ", ".join(missing)
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
                "Continue the interview. Ask exactly 1 follow-up question only, "
                "do not provide a plan yet."
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
                note = "Complete required fields: " + ", ".join(missing)
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
                return "No interview history yet. Go back to Step 2 and answer a few questions first."
            has_user_reply = any(
                item.get("role") == "user" and str(item.get("content", "")).strip()
                for item in history
            )
            if not has_user_reply:
                return "No interview answers yet. Go back to Step 2 and answer the follow-up questions first."
            plan_request = (
                "Generate a final phased rehab plan and clinical advice based on the intake "
                "and interview. Include progression criteria, return-to-sport checklist, and "
                "clear risk flags. If any red flags exist, lead with urgent guidance."
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
            gr.Markdown("Step 1: Intake & uploads")
            validation_note = gr.Markdown(visible=False)
            sport = gr.Textbox(
                label="Sport",
                placeholder="e.g., soccer, basketball",
                elem_classes=["required"],
            )
            injury_region = gr.Dropdown(
                label="Injury region",
                choices=[
                    "ankle",
                    "knee",
                    "hip",
                    "lower back",
                    "shoulder",
                    "elbow",
                    "wrist or hand",
                    "foot",
                    "hamstring",
                    "quad",
                    "calf",
                    "neck",
                    "other",
                ],
                value="knee",
                elem_classes=["required"],
            )
            injury_type = gr.Textbox(
                label="Injury type",
                placeholder="e.g., sprain, strain",
                elem_classes=["required"],
            )
            onset_type = gr.Radio(
                label="Onset type",
                choices=["acute trauma", "overuse", "unknown"],
                value="acute trauma",
                elem_classes=["required"],
            )
            time_since = gr.Textbox(
                label="Time since injury",
                placeholder="e.g., 2 days, 3 weeks",
                elem_classes=["required"],
            )
            pain_score = gr.Slider(label="Pain score", minimum=0, maximum=10, value=4, step=1)
            symptoms = gr.CheckboxGroup(label="Symptoms", choices=SYMPTOM_OPTIONS)
            injury_image = gr.Image(
                label="Optional image (PNG/JPG)",
                type="filepath",
                height=160,
            )
            training_goal = gr.Textbox(
                label="Training goal",
                placeholder="e.g., return to competition in 6 weeks",
                elem_classes=["required"],
            )
            training_phase = gr.Dropdown(
                label="Training phase",
                choices=["in-season", "off-season", "pre-season", "returning"],
                value="in-season",
            )
            prior_injury = gr.Textbox(label="Prior injury history", placeholder="optional")
            treatment_done = gr.Textbox(label="Treatments tried", placeholder="e.g., rest, ice")
            notes = gr.Textbox(
                label="Report summary / extra notes",
                lines=3,
                placeholder="e.g., MRI impression or prior clinician notes",
            )
            to_step2 = gr.Button("Step 2: Start interview", interactive=False)


        with step2_group:
            gr.Markdown("Step 2: Interview")
            chat_history = gr.State([])
            chat = gr.Chatbot(height=360)
            chat_input = gr.Textbox(
                placeholder="Answer the intake questions or ask a specific concern...",
                lines=3,
            )
            with gr.Row():
                send_btn = gr.Button("Send")
                back_to_step1 = gr.Button("Back to intake")
                to_step3 = gr.Button("Step 3: Generate plan")

        with step3_group:
            gr.Markdown("Step 3: Plan & recommendations")
            plan_output = gr.Markdown()
            with gr.Row():
                back_to_step2 = gr.Button("Back to interview")
                regenerate_plan = gr.Button("Regenerate plan")

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
    build_app().launch()
