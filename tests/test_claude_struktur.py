"""Die Claude-Struktur (.claude/) bleibt gültig: Frontmatter, Pflichtfelder, vorgeladene Skills existieren."""

from pathlib import Path

import pytest
import yaml

WURZEL = Path(__file__).resolve().parents[1]
CLAUDE = WURZEL / ".claude"


def frontmatter(p: Path) -> dict:
    text = p.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{p} ohne Frontmatter"
    return yaml.safe_load(text.split("---")[1]) or {}


SKILLS = sorted(CLAUDE.glob("skills/*/SKILL.md"))
AGENTS = sorted(CLAUDE.glob("agents/*.md"))
COMMANDS = sorted(CLAUDE.glob("commands/*.md"))
RULES = sorted(CLAUDE.glob("rules/*.md"))


def test_struktur_vollstaendig():
    assert {p.parent.name for p in SKILLS} >= {
        "tamil-marke", "tamil-screens", "tamil-richtung", "tamil-kritik", "impeccable", "tamil-theme", "tamil-cockpit",
        "radar-research", "radar-auswertung", "coolify-betrieb", "tamil-migration", "pruefen"}
    assert {p.stem for p in AGENTS} >= {
        "referenz-scout", "art-director", "design-kritiker", "qa-pruefer", "theme-bauer", "cockpit-bauer",
        "radar-entwickler", "code-pruefer", "redakteur", "migrator"}
    assert {p.stem for p in COMMANDS} >= {
        "status", "design-runde", "design-ausbau", "design-umsetzung", "research", "website-live", "release"}
    assert {p.stem for p in RULES} >= {"radar", "wordpress", "design", "betrieb"}


@pytest.mark.parametrize("p", SKILLS, ids=lambda p: p.parent.name)
def test_skill(p):
    fm = frontmatter(p)
    assert fm.get("name") == p.parent.name and fm.get("description")


@pytest.mark.parametrize("p", AGENTS, ids=lambda p: p.stem)
def test_agent(p):
    fm = frontmatter(p)
    assert fm.get("name") == p.stem and fm.get("description") and fm.get("tools")
    assert fm.get("model") in {"opus", "sonnet", "haiku", "inherit"}
    vorhanden = {s.parent.name for s in SKILLS}
    assert set(fm.get("skills") or []) <= vorhanden, f"{p.stem}: unbekannter Skill"


@pytest.mark.parametrize("p", COMMANDS, ids=lambda p: p.stem)
def test_command(p):
    fm = frontmatter(p)
    assert fm.get("description")
    assert "Ausführungsvertrag" in p.read_text(encoding="utf-8") or p.stem == "status"


@pytest.mark.parametrize("p", RULES, ids=lambda p: p.stem)
def test_regel_hat_paths(p):
    assert frontmatter(p).get("paths"), f"{p.stem}: ohne paths lädt die Regel in jede Sitzung"


def test_claude_md_kurz_und_verweist_auf_docs():
    text = (WURZEL / "CLAUDE.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) < 150
    for ziel in ("docs/betrieb.md", "docs/ablaeufe.md", "docs/entscheidungen.md"):
        assert ziel in text and (WURZEL / ziel).exists()


def test_keine_geheimnisse_in_docs_und_claude():
    muster = ("sk-ant-", "ghp_", "xoxb-", "BEGIN RSA PRIVATE", "BEGIN OPENSSH PRIVATE")
    for p in [*CLAUDE.rglob("*.md"), *(WURZEL / "docs").rglob("*.md"), WURZEL / "CLAUDE.md"]:
        text = p.read_text(encoding="utf-8")
        for m in muster:
            if m in text and "code-pruefer" not in p.name:
                pytest.fail(f"{p}: verdächtiges Muster {m}")
