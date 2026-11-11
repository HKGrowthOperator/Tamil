"""Kein Mailversand (Vertrag, Festlegung F0 Punkt 11, Regel vertrag.md): Rückmeldungen stehen auf der Website oder im
Cockpit. Der Test schlägt fehl, sobald im Code irgendwo E-Mail verschickt würde. `mailto:`-Links und Wörter wie
„E-Mail“ sind erlaubt."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORDNER = ("news_radar", "tools", "wordpress/plugins", "wordpress/themes", "wordpress/docker")
ENDUNGEN = {".py", ".php", ".js", ".mjs", ".ts", ".sh", ".ini", ".conf", ".toml", ".json", ".txt", ""}

MUSTER = [
    ("wp_mail()", re.compile(r"\bwp_mail\s*\(")),
    ("PHP mail()", re.compile(r"(?<![\w$>:\-.])mail\s*\(")),  # nicht $x->mail(, nicht get_mail(, nicht „e-mail (“
    ("smtplib", re.compile(r"\bsmtplib\b")),
    ("sendmail", re.compile(r"\bsendmail\b", re.I)),
    ("SMTP", re.compile(r"\bSMTP(?:_SSL)?\s*\(|PHPMailer|\bnodemailer\b")),
    ("Maildienst", re.compile(r"\b(?:sendgrid|mailgun|postmark|mailjet|sparkpost|mandrill|sendinblue|brevo|"
                              r"mailchimp_transactional)\b", re.I)),
    ("Resend/SES", re.compile(r"\b(?:import|from)\s+resend\b|\bsend_(?:raw_)?email\s*\(|\bsend_mail\s*\(")),
]


def dateien():
    for ordner in ORDNER:
        for p in (ROOT / ordner).rglob("*"):
            if p.is_file() and p.suffix in ENDUNGEN and "node_modules" not in p.parts and "vendor" not in p.parts:
                yield p


def funde(text: str) -> list[str]:
    out = []
    for nr, zeile in enumerate(text.splitlines(), 1):
        ohne_mailto = re.sub(r"mailto:[^\s\"'<>]*", "", zeile)
        for name, muster in MUSTER:
            if muster.search(ohne_mailto):
                out.append(f"{nr}: {name}: {zeile.strip()[:120]}")
    return out


def test_kein_mailversand_im_repo():
    gefunden = {}
    for p in dateien():
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        treffer = funde(text)
        if treffer:
            gefunden[str(p.relative_to(ROOT))] = treffer
    assert not gefunden, f"Mailversand gefunden: {gefunden}"


def test_muster_greifen_und_lassen_harmloses_durch():
    for boese in ("wp_mail( $to, $s, $m );", "mail($to, 'x', $body);", "import smtplib",
                  "subprocess.run(['sendmail', '-t'])", "from sendgrid import SendGridAPIClient",
                  "client.send_email(Source=a)", "$m = new PHPMailer();"):
        assert funde(boese), boese
    for harmlos in ('<a href="mailto:redaktion@example.org">E-Mail</a>', "Ihre E-Mail (optional)", "e-mail (Pflicht)",
                    "$user->mail(", "get_mail($x)", "email = form.get('email')", "Kein wp_mail-Versand vorgesehen"):
        assert not funde(harmlos), harmlos
