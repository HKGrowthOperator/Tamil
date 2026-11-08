"""Kostenmessung je Aufruf, Budget mit Reservierung und hartem Stopp, Provider mit FakeClaude, Job-Warteschlange."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import BaseModel

from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.workflow import costs, jobs, repo
from news_radar.workflow.fake import FakeAnthropic
from news_radar.workflow.models import SignalErgebnis
from news_radar.workflow.providers import Claude, schema_fuer


@pytest.fixture
def store(tmp_path):
    with Store(tmp_path / "r.sqlite") as s:
        yield s


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("NOTIFY_WEBHOOK_URL", "")
    return load_settings()


# ---- Preise --------------------------------------------------------------------------------------

def test_prices_per_model_with_cache_and_haiku_long_context_tier():
    t = costs.Tokens(input=1_000_000, output=1_000_000)
    klein = costs.Tokens(input=50_000, output=50_000)
    assert costs.kosten_tokens("claude-haiku-5-5", klein) == pytest.approx((50_000 * 0.10 + 50_000 * 0.50) / 1e6)
    assert costs.kosten_tokens("claude-sonnet-5-5", t) == pytest.approx(12.0)
    assert costs.kosten_tokens("claude-opus-5-5", t) == pytest.approx(24.0)
    assert costs.kosten_tokens("claude-sonnet-5-5[1m]", t) == pytest.approx(12.0)
    cache = costs.Tokens(cache_write_5m=1_000_000, cache_write_1h=1_000_000, cache_read=1_000_000)
    assert costs.kosten_tokens("claude-sonnet-5-5", cache) == pytest.approx(2 * 1.25 + 2 * 2 + 0.20)
    lang = costs.Tokens(input=150_000, output=10_000)  # Haiku über 100K Prompt-Tokens: höherer Satz für alles
    assert costs.kosten_tokens("claude-haiku-5-5", lang) == pytest.approx((150_000 * 0.50 + 10_000 * 2.50) / 1e6)
    with pytest.raises(costs.UnbekanntesModell):
        costs.kosten_tokens("gpt-irgendwas", t)


def test_fallback_iterations_are_billed_per_model():
    usage = {"input_tokens": 1000, "output_tokens": 500, "iterations": [
        {"type": "message", "model": "claude-sonnet-5-5", "input_tokens": 1000, "output_tokens": 0},
        {"type": "fallback_message", "model": "claude-opus-5-5", "input_tokens": 1000, "output_tokens": 500},
    ]}
    abr = costs.abrechnen_usage(usage, "claude-opus-5-5")
    assert abr.iterationen == 2 and abr.tokens.input == 2000
    assert abr.usd == pytest.approx((1000 * 2 + 1000 * 4 + 500 * 20) / 1e6)


def test_image_prices():
    assert costs.bild_kosten("gemini-nano-banana-2.1", "1K") == 0.0336
    assert costs.bild_kosten("gemini-nano-banana-2.1", "4k", 2) == pytest.approx(0.226)


# ---- Budget --------------------------------------------------------------------------------------

def test_budget_reservation_blocks_parallel_overrun_and_releases(store):
    budget = costs.Budget(store, tag_usd=1.0, monat_usd=10.0)
    a = budget.reservieren(0.6, "text")
    with pytest.raises(costs.BudgetErschoepft):
        budget.reservieren(0.5, "text")  # zusammen mit der offenen Reservierung über 1 $
    budget.freigeben(a)
    budget.reservieren(0.5, "text")


def test_budget_day_and_month_limits_warning_and_stop(store, settings):
    gemeldet = []
    budget = costs.Budget(store, tag_usd=1.0, monat_usd=1.5, warnung=0.8, melden=gemeldet.append)
    from news_radar.workflow.providers import usage_protokollieren

    usage_protokollieren(store, rolle="text", modell="claude-sonnet-5-5", usd=0.85)
    budget.pruefe_warnung()
    budget.pruefe_warnung()  # nur einmal je Tag
    assert budget.stand()["warnung"] and not budget.stand()["stopp"]
    assert len(gemeldet) == 1 and "80 %" in gemeldet[0]
    usage_protokollieren(store, rolle="text", modell="claude-sonnet-5-5", usd=0.2)
    with pytest.raises(costs.BudgetErschoepft):
        budget.reservieren(0.01)
    budget.pruefe_warnung()
    assert budget.stand()["stopp"] and "erreicht" in gemeldet[-1]
    # Monatslimit: morgen ist das Tagesbudget frei, der Monat aber fast voll
    morgen = costs.Budget(store, 1.0, 1.5, uhr=lambda: datetime.now(timezone.utc) + timedelta(days=1))
    if morgen.uhr().astimezone(costs.ZONE).month == datetime.now(timezone.utc).astimezone(costs.ZONE).month:
        with pytest.raises(costs.BudgetErschoepft):
            morgen.reservieren(0.5)
        morgen.reservieren(0.4)


# ---- Provider -------------------------------------------------------------------------------------

class Mini(BaseModel):
    ja: bool


def test_provider_records_usage_cost_and_prompt_version(store, settings):
    fake = FakeAnthropic({"seo": {"ja": True}})
    budget = costs.Budget(store, 5, 150)
    claude = Claude(settings, store, client=fake, budget=budget)
    a = claude.call("seo", "System " * 300, "Frage", Mini, story_id=7)
    assert a.ok and a.daten.ja and a.modell == "claude-haiku-5-5" and a.kosten_usd > 0
    req = fake.requests[0]["kwargs"]
    assert "fallbacks" not in req and "betas" not in req  # Haiku: kein serverseitiger Fallback
    assert req["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert req["output_config"]["format"]["schema"]["description"].startswith("rolle:seo")
    row = dict(store.db.execute("SELECT * FROM agent_usage").fetchone())
    assert row["story_id"] == 7 and row["status"] == "ok" and row["prompt_version"] and row["preis_version"] == costs.PRICE_VERSION
    assert row["request_id"] == "req_fake_1" and row["cache_write_5m"] > 0
    assert store.db.execute("SELECT COUNT(*) FROM budget_reservierungen").fetchone()[0] == 0
    claude.call("seo", "System " * 300, "Frage 2", Mini)
    assert store.db.execute("SELECT cache_read FROM agent_usage WHERE id = 2").fetchone()[0] > 0


def test_provider_sonnet_uses_server_fallback_and_records_real_model(store, settings):
    fake = FakeAnthropic({"text": {"ja": True}}, fallback_modell={"text": "claude-opus-5-5"})
    a = Claude(settings, store, client=fake).call("text", "s", "u", Mini)
    req = fake.requests[0]["kwargs"]
    assert req["fallbacks"] == "default" and req["betas"] == ["server-side-fallback-2026-07-01"]
    row = dict(store.db.execute("SELECT * FROM agent_usage").fetchone())
    assert a.modell == "claude-opus-5-5" and row["modell_angefragt"] == "claude-sonnet-5-5" and row["iterationen"] == 2


def test_provider_refusal_truncation_invalid_and_errors_are_logged(store, settings):
    claude = Claude(settings, store, client=FakeAnthropic({"seo": {"ja": True}}, ablehnen=("seo",)))
    assert claude.call("seo", "s", "u", Mini).status == "abgelehnt"
    claude = Claude(settings, store, client=FakeAnthropic({"seo": {"ja": True}}, abschneiden=("seo",)))
    assert claude.call("seo", "s", "u", Mini).status == "abgeschnitten"
    claude = Claude(settings, store, client=FakeAnthropic({"seo": {"falsch": 1}}))
    assert claude.call("seo", "s", "u", Mini).status == "ungueltig"
    claude = Claude(settings, store, client=FakeAnthropic(fehler={"seo": TimeoutError("zu langsam")}))
    with pytest.raises(TimeoutError):
        claude.call("seo", "s", "u", Mini)
    stati = [r[0] for r in store.db.execute("SELECT status FROM agent_usage ORDER BY id")]
    assert stati == ["abgelehnt", "abgeschnitten", "ungueltig", "fehler"]


def test_provider_budget_stop_prevents_call(store, settings):
    fake = FakeAnthropic({"text": {"ja": True}})
    claude = Claude(settings, store, client=fake, budget=costs.Budget(store, tag_usd=0.0001, monat_usd=150))
    with pytest.raises(costs.BudgetErschoepft):
        claude.call("text", "s", "u", Mini)
    assert fake.requests == []
    assert store.db.execute("SELECT status FROM agent_usage").fetchone()[0] == "budget"


def test_schema_is_strict_and_nested():
    schema = schema_fuer(SignalErgebnis, "signal")
    item = schema["$defs"]["SignalBewertung"]
    assert schema["additionalProperties"] is False and item["additionalProperties"] is False
    assert set(item["required"]) == set(item["properties"])


# ---- Jobs ------------------------------------------------------------------------------------------

def test_jobs_idempotent_priority_backoff_dead_letter_and_budget(store):
    sid = repo.story_anlegen(store, typ="news", titel="A")
    assert jobs.einreihen(store, sid, "recherche", prio=jobs.PRIO_NEWS) is not None
    assert jobs.einreihen(store, sid, "recherche") is None  # derselbe Schritt nur einmal
    eilig = jobs.einreihen(store, sid, "schreiben", prio=jobs.PRIO_EVENT_BALD)
    job = jobs.naechster(store, "w1")
    assert job["id"] == eilig and job["status"] == "laeuft" and job["versuche"] == 1
    assert jobs.fehlgeschlagen(store, job["id"], "429") == "offen"
    assert jobs.naechster(store, "w1")["schritt"] == "recherche"  # der fehlgeschlagene wartet 1 Minute
    store.db.execute("UPDATE workflow_jobs SET naechster_versuch = '2000-01-01' WHERE id = ?", (eilig,))
    store.db.commit()
    for _ in range(2):
        j = jobs.naechster(store, "w1")
        status = jobs.fehlgeschlagen(store, j["id"], "kaputt")
        store.db.execute("UPDATE workflow_jobs SET naechster_versuch = '2000-01-01' WHERE id = ?", (eilig,))
        store.db.commit()
    assert status == "tot" and jobs.zaehlen(store)["tot"] == 1
    assert jobs.erneut(store, eilig) and jobs.zaehlen(store)["offen"] == 1
    j = jobs.naechster(store, "w1")
    jobs.wartet_budget(store, j["id"], "Budget")
    assert jobs.naechster(store, "w1") is None and jobs.budget_wieder_frei(store) == 1
    j = jobs.naechster(store, "w1")
    assert j["versuche"] == 1  # der Budget-Versuch zählt nicht
    store.db.execute("UPDATE workflow_jobs SET deadline = '2000-01-01' WHERE id = ?", (j["id"],))
    store.db.commit()
    assert jobs.aufraeumen(store) == 1 and jobs.zaehlen(store)["offen"] == 1


def test_v1_writer_is_measured_and_respects_budget(store, settings):
    from datetime import datetime, timezone

    from news_radar.sources import NewsItem
    from news_radar.workflow.fake import text as text_antwort
    from news_radar.writer import Writer

    item = NewsItem(title="Pongal in Köln", url="https://example.com/p", summary="Fest", source="Test",
                    published=datetime(2026, 11, 8, tzinfo=timezone.utc))
    antwort = text_antwort("<story>\n{\"titel\": \"Pongal in Köln\", \"ort\": \"Köln\"}\n</story>", "", {})
    antwort.pop("belege")
    writer = Writer(settings, client=FakeAnthropic({"text": antwort}), store=store, budget=costs.Budget(store, 5, 150))
    draft = writer.write(item, "")
    assert draft.titel == "Pongal in Köln"
    row = dict(store.db.execute("SELECT * FROM agent_usage").fetchone())
    assert row["rolle"] == "text" and row["modell"] == settings.anthropic_model and row["kosten_usd"] > 0
    leer = Writer(settings, client=FakeAnthropic({"text": antwort}), store=store, budget=costs.Budget(store, 0.0, 150))
    with pytest.raises(costs.BudgetErschoepft):
        leer.write(item, "")
