"""
Esperimento A' — Inter-Rater Reliability Tiered.

Variante dell'A con prompt modificato che forza la classificazione in 3 tier:
  - NUCLEAR: primitiva essenziale (test di rimozione positivo)
  - PRESENT: chiaramente manifestata ma non essenziale
  - INFERRED: debolmente manifestata

Output per ogni (coder × sistema): JSON con lista di primitive, ciascuna con tier.
"""
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Carica .env dalla directory parent (A/ ha il .env originale)
PARENT_DIR = Path(__file__).parent.parent
load_dotenv(PARENT_DIR / ".env", override=True)

SCRIPT_DIR = Path(__file__).parent
TEST_SYSTEMS_FILE = PARENT_DIR / "TEST_SYSTEMS.md"
THEORY_PROMPT_FILE = PARENT_DIR / "theory_primitives_prompt.txt"
THEORY_DATA_PATH = Path(r"C:/Users/giacinto/Documents/genesisV2.0/engine/theory-data.json")
THEORY_DATA_SHA256 = "98d277369e0213d54f55910ea8157c86dc3a690e3f8cbb81605fa036b8401b5a"
RAW_DIR = SCRIPT_DIR / "raw_responses_v2"
RAW_DIR.mkdir(exist_ok=True)
LOG_FILE = SCRIPT_DIR / "execution_log_v2.txt"

VALID_TIERS = {"NUCLEAR", "PRESENT", "INFERRED"}


def log(msg: str, *, log_lines: list = None):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    if log_lines is not None:
        log_lines.append(line)


def verify_theory_data(path: Path, expected_sha: str) -> None:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    actual = sha.hexdigest()
    if actual != expected_sha:
        print(
            f"ERRORE INTEGRITA theory-data.json: atteso {expected_sha}, ottenuto {actual}",
            file=sys.stderr,
        )
        sys.exit(1)


def extract_test_systems(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    pattern = re.compile(r"^## (S\d+)\s+[—-]\s+(.+?)\n(.*?)(?=^## |\Z)", re.DOTALL | re.MULTILINE)
    systems = {}
    for match in pattern.finditer(text):
        sid = match.group(1)
        title = match.group(2).strip()
        body = match.group(3).strip()
        body = body.split("---")[0].strip()
        if sid.startswith("S") and sid[1:].isdigit():
            systems[sid] = {"id": sid, "title": title, "description": body}
    return systems


USER_PROMPT_TEMPLATE = (
    "Ti do la descrizione di un sistema informativo reale. Applicando le 34 primitive "
    "della Teoria Strutturale della Realta' Informativa come te le ho definite sopra, "
    "identifica quali primitive sono presenti e **classifica ciascuna in uno di tre livelli "
    "di essenzialita'**.\n\n"
    "**NUCLEAR** — Senza questa primitiva, il sistema non e' piu' *quel* sistema. Se la togli, "
    "crolla l'identita' stessa del fenomeno descritto. Applica letteralmente il test di rimozione: "
    "'il sistema cesserebbe di essere cio' che e'?' Se si', la primitiva e' NUCLEAR. Sii severo — "
    "riserva NUCLEAR solo alle primitive strutturalmente indispensabili all'identita' del sistema. "
    "Nel dubbio, preferisci PRESENT.\n\n"
    "**PRESENT** — Chiaramente manifestata nel sistema, ma non essenziale per la sua identita'. "
    "Se la togli, il sistema e' impoverito ma resta riconoscibilmente quello stesso sistema.\n\n"
    "**INFERRED** — Debolmente inferibile, il sistema la manifesta in qualche senso sottile o "
    "periferico. Puo' essere omessa senza perdere informazione sostanziale sull'identita' del sistema.\n\n"
    "Non includere primitive totalmente assenti. Non aggiungere primitive per completezza simmetrica. "
    "Non modificare la definizione delle primitive per farle calzare al sistema.\n\n"
    "Per ogni primitiva identificata: (1) ID (es. C1, M2), (2) tier (NUCLEAR, PRESENT, o INFERRED), "
    "(3) citazione testuale dal sistema, (4) test di rimozione esplicito.\n\n"
    'Output in JSON: {{"primitives": [{{"id": "...", "tier": "NUCLEAR|PRESENT|INFERRED", '
    '"quote": "...", "removal_test": "..."}}]}}.\n\n'
    "Sistema da analizzare:\n\n"
    "{title}\n\n"
    "{description}"
)


def extract_json_from_response(raw: str) -> dict:
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    start = raw.find("{")
    if start >= 0:
        depth = 0
        in_string = False
        esc = False
        for i in range(start, len(raw)):
            c = raw[i]
            if esc:
                esc = False
                continue
            if c == "\\":
                esc = True
                continue
            if c == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    candidate = raw[start : i + 1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        pass
                    break
    raise ValueError("Impossibile estrarre JSON dalla risposta")


# === LLM CLIENTS ===

def call_claude(system_prompt: str, user_prompt: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        temperature=0.0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            raw_parts.append(block.text)
    raw = "".join(raw_parts) if raw_parts else ""
    usage = {}
    if hasattr(response, "usage") and response.usage is not None:
        for field in ("input_tokens", "output_tokens",
                      "cache_creation_input_tokens", "cache_read_input_tokens"):
            val = getattr(response.usage, field, None)
            if isinstance(val, (int, float)) or val is None:
                usage[field] = val
    return {"raw": raw, "model_reported": response.model, "usage": usage}


def call_openai(system_prompt: str, user_prompt: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.0,
        seed=42,
        max_tokens=8000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    raw = response.choices[0].message.content
    usage = response.usage.model_dump() if response.usage else {}
    return {"raw": raw, "model_reported": response.model, "usage": usage}


def call_gemini(system_prompt: str, user_prompt: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=system_prompt,
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        },
    )
    response = model.generate_content(user_prompt)
    raw = None
    try:
        raw = response.text
    except Exception:
        try:
            parts = response.candidates[0].content.parts
            raw = "".join(getattr(p, "text", "") for p in parts)
        except Exception:
            raw = ""
    if not raw:
        try:
            cand = response.candidates[0]
            diag = {
                "finish_reason": str(getattr(cand, "finish_reason", None)),
                "safety_ratings": [str(r) for r in getattr(cand, "safety_ratings", [])],
            }
            raw = "EMPTY_RESPONSE " + json.dumps(diag)
        except Exception:
            raw = "EMPTY_RESPONSE (no candidates)"
    usage = {}
    if hasattr(response, "usage_metadata") and response.usage_metadata is not None:
        usage = {
            "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", None),
            "completion_tokens": getattr(response.usage_metadata, "candidates_token_count", None),
            "total_tokens": getattr(response.usage_metadata, "total_token_count", None),
        }
    return {"raw": raw, "model_reported": "gemini-2.5-pro", "usage": usage}


LLM_CLIENTS = {
    "J1_CLAUDE": call_claude,
    "J2_OPENAI": call_openai,
    "J3_GEMINI": call_gemini,
}


def normalize_primitives(prims_raw: list) -> list:
    """Normalizza l'output: ogni primitiva deve avere id + tier valido."""
    out = []
    for p in prims_raw:
        if not isinstance(p, dict):
            continue
        pid = p.get("id", "").strip()
        tier = p.get("tier", "").strip().upper()
        if not pid or tier not in VALID_TIERS:
            # Scartiamo primitive senza tier valido (documentiamo nel log)
            continue
        out.append({
            "id": pid,
            "tier": tier,
            "quote": p.get("quote", ""),
            "removal_test": p.get("removal_test", ""),
        })
    return out


def main():
    log_lines = []

    log("=" * 70, log_lines=log_lines)
    log("Esperimento A' — Inter-Rater Reliability Tiered", log_lines=log_lines)
    log("=" * 70, log_lines=log_lines)

    log("Verifica integrita' theory-data.json...", log_lines=log_lines)
    verify_theory_data(THEORY_DATA_PATH, THEORY_DATA_SHA256)
    log(f"  SHA-256 OK: {THEORY_DATA_SHA256}", log_lines=log_lines)

    # Riusa il prompt delle primitive già generato dall'A (stesso theory-data.json)
    if not THEORY_PROMPT_FILE.exists():
        log(f"ERRORE: {THEORY_PROMPT_FILE} non esiste. Eseguire prima run_experiment.py dell'A.", log_lines=log_lines)
        sys.exit(1)
    primitives_prompt = THEORY_PROMPT_FILE.read_text(encoding="utf-8")
    log(f"  Prompt primitive riusato da A ({len(primitives_prompt)} char)", log_lines=log_lines)

    log("Estrazione dei 10 sistemi di test (da ../TEST_SYSTEMS.md)...", log_lines=log_lines)
    systems = extract_test_systems(TEST_SYSTEMS_FILE)
    if len(systems) != 10:
        log(f"ATTENZIONE: trovati {len(systems)} sistemi invece di 10", log_lines=log_lines)
        sys.exit(1)
    for sid in sorted(systems.keys(), key=lambda x: int(x[1:])):
        s = systems[sid]
        log(f"  {sid}: {s['title']} ({len(s['description'])} char)", log_lines=log_lines)

    log("\nEsecuzione 30 chiamate API (prompt tiered)...", log_lines=log_lines)
    for llm_id, caller in LLM_CLIENTS.items():
        llm_dir = RAW_DIR / llm_id
        llm_dir.mkdir(exist_ok=True)
        for sid in sorted(systems.keys(), key=lambda x: int(x[1:])):
            s = systems[sid]
            user_prompt = USER_PROMPT_TEMPLATE.format(title=s["title"], description=s["description"])
            key = f"{llm_id}/{sid}"
            output_file = llm_dir / f"{sid}.json"
            if output_file.exists():
                log(f"  [skip] {key}: gia' presente", log_lines=log_lines)
                continue
            attempt = 0
            last_error = None
            last_raw = None
            while attempt < 2:
                attempt += 1
                try:
                    t0 = time.time()
                    response = caller(primitives_prompt, user_prompt)
                    elapsed = time.time() - t0
                    last_raw = response["raw"]
                    parsed = extract_json_from_response(response["raw"])
                    prims_raw = parsed.get("primitives", [])
                    if not isinstance(prims_raw, list):
                        raise ValueError(f"Output non ha una lista 'primitives': {parsed}")
                    prims = normalize_primitives(prims_raw)
                    # Conta per tier
                    tier_counts = {t: sum(1 for p in prims if p["tier"] == t) for t in VALID_TIERS}
                    record = {
                        "llm": llm_id,
                        "system": sid,
                        "system_title": s["title"],
                        "attempt": attempt,
                        "elapsed_s": round(elapsed, 2),
                        "model_reported": response.get("model_reported"),
                        "usage": response.get("usage"),
                        "primitives_identified": prims,
                        "tier_counts": tier_counts,
                        "n_total": len(prims),
                        "raw_response": response["raw"],
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    }
                    output_file.write_text(
                        json.dumps(record, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    log(
                        f"  [OK] {key}: tot={len(prims)} "
                        f"(NUCLEAR={tier_counts['NUCLEAR']}, PRESENT={tier_counts['PRESENT']}, "
                        f"INFERRED={tier_counts['INFERRED']}) ({elapsed:.1f}s, attempt {attempt})",
                        log_lines=log_lines,
                    )
                    break
                except Exception as e:
                    last_error = e
                    log(f"  [FAIL] {key} attempt {attempt}: {type(e).__name__}: {e}", log_lines=log_lines)
                    if attempt < 2:
                        time.sleep(3)
            else:
                record = {
                    "llm": llm_id,
                    "system": sid,
                    "system_title": s["title"],
                    "attempt": 2,
                    "error": f"{type(last_error).__name__}: {last_error}",
                    "primitives_identified": [],
                    "tier_counts": {t: 0 for t in VALID_TIERS},
                    "n_total": 0,
                    "missing": True,
                    "raw_response_full": last_raw,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                }
                output_file.write_text(
                    json.dumps(record, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                log(f"  [MISSING] {key}: 2 tentativi falliti", log_lines=log_lines)

    log("\nTutte le chiamate completate.", log_lines=log_lines)
    LOG_FILE.write_text("\n".join(log_lines), encoding="utf-8")
    log(f"Log salvato in {LOG_FILE.name}", log_lines=log_lines)


if __name__ == "__main__":
    main()
