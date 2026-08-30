import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_SKILL = REPO_ROOT / ".agents/skills/prompt-refinement-evals/SKILL.md"
CLAUDE_SKILL = REPO_ROOT / ".claude/skills/prompt-refinement-evals/SKILL.md"
EXPECTED_NAME = "prompt-refinement-evals"
PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:todo|tbd|fixme|placeholder|your_api_key|replace[ -]me|coming[ -]soon)\b|"
    r"\{\{[^}\n]+\}\}|<[A-Za-z][^>\n]*>",
    re.IGNORECASE,
)


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    assert lines and lines[0] == "---", "SKILL.md must start with YAML frontmatter"
    try:
        closing_index = lines.index("---", 1)
    except ValueError as error:
        raise AssertionError("SKILL.md frontmatter is not closed") from error

    values: dict[str, str] = {}
    for line in lines[1:closing_index]:
        assert ":" in line, f"invalid frontmatter line: {line!r}"
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def test_codex_and_claude_skill_mirrors_are_byte_identical() -> None:
    assert CODEX_SKILL.read_bytes() == CLAUDE_SKILL.read_bytes()


def test_skill_frontmatter_is_discoverable_and_finished() -> None:
    text = CODEX_SKILL.read_text(encoding="utf-8")
    metadata = _frontmatter(text)

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == EXPECTED_NAME == CODEX_SKILL.parent.name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"])

    description = metadata["description"]
    assert 20 <= len(description) <= 300
    assert "benchmark" in description.lower()
    assert "prompt-refinement" in description.lower()
    assert not PLACEHOLDER_PATTERN.search(text)


def test_skill_keeps_commands_and_safety_invariants_visible() -> None:
    text = CODEX_SKILL.read_text(encoding="utf-8").lower()

    for subcommand in ("validate", "analyze", "report"):
        assert f"prompt-refinement-eval {subcommand}" in text

    assert "explicit authorization" in text
    assert "mass-submit" in text
    assert "never log or expose" in text
    assert "paired evidence" in text
