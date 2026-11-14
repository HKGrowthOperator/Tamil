"""Kostendeckel je Story (Prüfliste vom 13.11.2026, Punkt 2).

1. Die zweite KI (Rollen „pruefung“/„endpruefung“) hat einen eigenen Anteil: Recherche, Schreiben, Faktencheck,
   Lektorat und SEO dürfen nur bis Deckel minus Prüfanteil laufen, damit die Pflichtprüfung nicht verhungert.
2. Das KI-Bild zählt mit: ist der Deckel erreicht, wird kein KI-Bild mehr erzeugt (Bildkarte statt Kosten).
"""

import base64
import io

from PIL import Image

from news_radar.store import Store
from news_radar.workflow import jobs, orchestrator, repo
from news_radar.workflow.fake import FakeAnthropic
from news_radar.workflow.providers import usage_protokollieren

from test_nachrecherche import HAMM, hamm, settings  # noqa: F401


def _story_mit_kosten(settings, store, client, usd: float, rolle: str = "schreiben"):
    ctx = orchestrator.kontext(settings, store, client=client, fetch_text=lambda u: HAMM, suche=lambda q: [])
    orchestrator.scan(ctx, [hamm()])
    sid = repo.stories(store)[0]["id"]
    usage_protokollieren(store, rolle=rolle, provider="anthropic", modell="x", usd=usd, story_id=sid)
    return ctx, sid


def test_schreibschritte_lassen_den_pruefanteil_frei(settings):
    # 0,80 $ von 1 $ verbraucht, Prüfanteil 0,30 $: kein weiterer Schreib- oder Rechercheschritt
    settings.kosten_story_usd, settings.kosten_story_pruefung_usd = 1.0, 0.3
    with Store(settings.db_path) as store:
        client = FakeAnthropic()
        ctx, sid = _story_mit_kosten(settings, store, client, 0.8)
        orchestrator.abarbeiten(ctx)
        story = repo.story(store, sid)
    assert client.requests == [] and story["status"] == "verworfen" and "Kostendeckel" in story["notiz"]


def test_endpruefung_laeuft_im_eigenen_anteil(settings):
    settings.kosten_story_usd, settings.kosten_story_pruefung_usd = 1.0, 0.3
    with Store(settings.db_path) as store:
        client = FakeAnthropic()
        ctx, sid = _story_mit_kosten(settings, store, client, 0.8)
        # die Schreibschritte sind schon gelaufen: offen ist nur noch die Endprüfung
        store.db.execute("UPDATE workflow_jobs SET status = 'fertig' WHERE story_id = ?", (sid,))
        store.db.commit()
        felder = {"titel": "Lichterfest in Hamm", "teaser": "t", "inhalt_html": "<p>x</p>", "kategorie": "news"}
        repo.fassung_speichern(store, sid, "seo", felder, von="test")
        jobs.einreihen(store, sid, "endpruefung", payload={})
        orchestrator.abarbeiten(ctx)
        story = repo.story(store, sid)
    # die Endprüfung lief; eine Überarbeitung danach fällt wieder unter den Deckel für die Schreibschritte
    assert [r["rolle"] for r in client.requests][:1] == ["pruefer"], client.requests
    assert "„endpruefung“" not in (story["notiz"] or "")


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (1600, 900), (200, 30, 30)).save(buf, "PNG")
    return buf.getvalue()


def test_ki_bild_zaehlt_zum_kostendeckel(settings):
    settings.kosten_story_usd = 1.0
    settings.bild_ki_freigabe, settings.gemini_key, settings.bild_retry_pause = True, "test", 0
    settings.bild_reihenfolge = ["ki", "karte"]
    aufrufe = []
    daten = base64.b64encode(_png()).decode()
    with Store(settings.db_path) as store:
        ctx, sid = _story_mit_kosten(settings, store, None, 1.2)
        ctx.bild_transport = lambda headers, body: (aufrufe.append(1), (200, {"status": "completed", "outputs": [
            {"type": "image", "data": daten}]}))[1]
        store.db.execute("UPDATE workflow_jobs SET status = 'fertig' WHERE story_id = ?", (sid,))
        store.db.commit()
        felder = {"titel": "Lichterfest in Hamm", "teaser": "t", "inhalt_html": "<p>x</p>", "kategorie": "community",
                  "bild_thema": "tempelfest", "bild_prompt": "Temple courtyard at dusk with oil lamps"}
        repo.fassung_speichern(store, sid, "seo", felder, von="test")
        jobs.einreihen(store, sid, "bild", payload={})
        orchestrator.abarbeiten(ctx)
        ki = store.db.execute("SELECT COUNT(*) FROM agent_usage WHERE rolle = 'bild'").fetchone()[0]
    assert aufrufe == [] and ki == 0
