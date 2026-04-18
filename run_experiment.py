"""
Esperimento A — Inter-Rater Reliability tra LLM indipendenti.

Esegue 30 chiamate API (10 sistemi × 3 LLM):
  - J1: Claude Opus 4.7 (Anthropic)
  - J2: GPT-4o (OpenAI)
  - J3: Gemini 2.5 Pro (Google)

Per ogni chiamata:
  - Legge il system prompt da theory_primitives_prompt.txt (generato deterministicamente
    da theory-data.json e committato insieme al codice)
  - Legge la descrizione del sistema da TEST_SYSTEMS.md
  - Invia con temperature=0, seed=42 dove supportato
  - Salva output grezzo in raw_responses/{LLM}/{S#}.json
  - 1 retry in caso di parsing fallito

Pre-registrato in PRE_REGISTRATION.md §5.
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

load_dotenv(override=True)  # override: il parent shell può avere chiavi vuote che bloccano il caricamento

SCRIPT_DIR = Path(__file__).parent
TEST_SYSTEMS_FILE = SCRIPT_DIR / "TEST_SYSTEMS.md"
THEORY_DATA_PATH = Path(r"C:/Users/giacinto/Documents/genesisV2.0/engine/theory-data.json")
THEORY_DATA_SHA256 = "98d277369e0213d54f55910ea8157c86dc3a690e3f8cbb81605fa036b8401b5a"
RAW_DIR = SCRIPT_DIR / "raw_responses"
RAW_DIR.mkdir(exist_ok=True)
LOG_FILE = SCRIPT_DIR / "execution_log.txt"


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


def build_primitives_prompt(theory_data: dict) -> str:
    """Costruisce la descrizione delle 34 primitive SENZA informazioni che orientano
    (niente attrazioni, niente organizzatrici/hub, niente repulsioni)."""
    parts = [
        "DEFINIZIONI DELLE 34 PRIMITIVE NUCLEARI DELLA TEORIA STRUTTURALE DELLA REALTA' INFORMATIVA (TSRI).",
        "",
        "Ogni primitiva e' una manifestazione locale di una o due proprieta' fondamentali all'interno di una struttura ricorrente.",
        "",
        "Le 5 proprieta' fondamentali sono:",
        "  P1_STATE (Stato): le entita' esistono e rappresentano frammenti di realta'.",
        "  P2_TRANSFORMATION (Trasformazione): lo stato muta.",
        "  P3_RELATIONAL_FACT (Fatto Relazionale): le entita' possono essere connesse tra loro.",
        "  P4_CONSTRAINT (Vincolo): non tutte le mutazioni e non tutte le connessioni sono valide.",
        "  P5_PARTICIPATION (Partecipazione): un osservatore rende l'informazione significativa.",
        "",
        "Le 8 strutture ricorrenti sono:",
        "  CONTENT, INVENTORY, TRANSACTIONS, MEMBERSHIP, WORKFLOW, SCHEDULING, COMMUNICATION, TELEMETRY.",
        "",
        "Elenco delle 34 primitive:",
        "",
    ]
    primitives = theory_data["primitives"]
    # Ordine deterministico: per struttura, poi per ID
    structures_order = [
        "CONTENT", "INVENTORY", "TRANSACTIONS", "MEMBERSHIP",
        "WORKFLOW", "SCHEDULING", "COMMUNICATION", "TELEMETRY",
    ]
    by_struct = {s: [] for s in structures_order}
    for pid, p in primitives.items():
        by_struct[p["structure"]].append(pid)
    for s in structures_order:
        by_struct[s].sort()
        for pid in by_struct[s]:
            p = primitives[pid]
            props = ", ".join(pp["id"] for pp in p["properties"])
            parts.append(f"=== {pid} — {p['name']} (struttura: {p['structure']}) ===")
            parts.append(f"Proprieta' manifestate: {props}")
            tr = p.get("timeRelation", {})
            if tr.get("description"):
                parts.append(f"Relazione col tempo: {tr['description']}")
            bd = p.get("bondDirection", "")
            if bd:
                parts.append(f"Direzione del legame: {bd}")
            ag = p.get("agency", "")
            if ag:
                parts.append(f"Agency: {ag}")
            rr = p.get("regularityRelations", [])
            for r in rr:
                note = r.get("note", "")
                parts.append(f"Regolarita' {r.get('regularity', '')}: {r.get('type', '')} — {note}")
            parts.append("")  # blank line
    return "\n".join(parts)


def extract_test_systems(md_path: Path) -> dict:
    """Parsa TEST_SYSTEMS.md e estrae i 10 sistemi."""
    text = md_path.read_text(encoding="utf-8")
    # Regex per trovare i blocchi ## S1 — ... seguiti fino al prossimo ## o ---
    pattern = re.compile(r"^## (S\d+)\s+[—-]\s+(.+?)\n(.*?)(?=^## |\Z)", re.DOTALL | re.MULTILINE)
    systems = {}
    for match in pattern.finditer(text):
        sid = match.group(1)
        title = match.group(2).strip()
        body = match.group(3).strip()
        # Rimuove eventuali --- di separazione
        body = body.split("---")[0].strip()
        if sid.startswith("S") and sid[1:].isdigit():
            systems[sid] = {"id": sid, "title": title, "description": body}
    return systems


USER_PROMPT_TEMPLATE = (
    "Ti do la descrizione di un sistema informativo reale. Applicando le 34 primitive "
    "della Teoria Strutturale della Realta' Informativa come te le ho definite sopra, "
    "identifica quali primitive sono presenti in questo sistema.\n\n"
    "Per ogni primitiva presente: (1) il suo ID (es. C1, M2), (2) una citazione testuale "
    "dal sistema che la manifesta, (3) il test di rimozione (cosa perderebbe il sistema "
    "se questa primitiva non ci fosse).\n\n"
    "Non identificare primitive che non sono chiaramente presenti. Non aggiungere "
    "primitive per completezza simmetrica con altri sistemi. Non modificare la definizione "
    "delle primitive per farle calzare al sistema.\n\n"
    'Output in JSON: {{"primitives": [{{"id": "...", "quote": "...", "removal_test": "..."}}]}}.'
    "\n\n"
    "Sistema da analizzare:\n\n"
    "{title}\n\n"
    "{description}"
)


def extract_json_from_response(raw: str) -> dict:
    """Estrae il blocco JSON dall'output di un LLM. Gli LLM a volte aggiungono testo prima/dopo."""
    # Prima prova: JSON diretto
    try:
        return json.loads(raw)
    except Exception:
        pass
    # Seconda prova: cerca il blocco ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Terza prova: trova il primo { e fai match parentesi
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
    """J1: Claude Sonnet 4.5 via Anthropic API.

    DEVIAZIONE FORMALE dalla pre-registration §4 (documentata):
    La pre-registration dichiarava Claude Opus 4.7. Quella versione, essendo un
    reasoning model, l'API Anthropic rifiuta il parametro temperature con errore
    400 "temperature is deprecated for this model". Per preservare il determinismo
    dichiarato (temperature=0.0, requisito chiave della §5 pre-registration),
    sostituiamo il modello con Claude Sonnet 4.5 che accetta temperature.

    Tradeoff: piccola perdita di capacità (Sonnet < Opus) in cambio della
    conservazione del determinismo. Si preferisce questa deviazione a quella
    opposta (mantenere Opus senza temperature) perché temperature=0 è la
    condizione operativamente più importante per la riproducibilità.

    La deviazione viene dichiarata nel REPORT.md.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        temperature=0.0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    # Estrazione robusta del testo (gestisce casi dove content non è solo TextBlock)
    raw_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            raw_parts.append(block.text)
    raw = "".join(raw_parts) if raw_parts else ""
    # Usage: estrai solo campi primitivi JSON-serializzabili
    usage = {}
    if hasattr(response, "usage") and response.usage is not None:
        for field in ("input_tokens", "output_tokens",
                      "cache_creation_input_tokens", "cache_read_input_tokens"):
            val = getattr(response.usage, field, None)
            if isinstance(val, (int, float)) or val is None:
                usage[field] = val
    return {"raw": raw, "model_reported": response.model, "usage": usage}


def call_openai(system_prompt: str, user_prompt: str) -> dict:
    """J2: GPT-4o via OpenAI API."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.0,
        seed=42,
        max_tokens=4000,
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
    """J3: Gemini 2.5 Pro via Google AI Studio."""
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=system_prompt,
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 8192,  # aumentato per evitare troncature
            "response_mime_type": "application/json",
        },
    )
    response = model.generate_content(user_prompt)
    # Estrazione robusta del testo
    raw = None
    try:
        raw = response.text
    except Exception:
        # Se response.text fallisce (safety filter, empty parts, ecc.), proviamo parts
        try:
            parts = response.candidates[0].content.parts
            raw = "".join(getattr(p, "text", "") for p in parts)
        except Exception:
            raw = ""
    if not raw:
        # Costruisce una diagnostica utile includendo finish_reason e safety
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


def main():
    log_lines = []

    log("=" * 70, log_lines=log_lines)
    log("Esperimento A — Inter-Rater Reliability tra LLM indipendenti", log_lines=log_lines)
    log("=" * 70, log_lines=log_lines)

    # 1. Verifica integrità theory-data.json
    log("Verifica integrita' theory-data.json...", log_lines=log_lines)
    verify_theory_data(THEORY_DATA_PATH, THEORY_DATA_SHA256)
    log(f"  SHA-256 OK: {THEORY_DATA_SHA256}", log_lines=log_lines)

    # 2. Carica theory-data e costruisci il prompt delle primitive
    with open(THEORY_DATA_PATH, "r", encoding="utf-8") as f:
        theory_data = json.load(f)
    primitives_prompt = build_primitives_prompt(theory_data)
    prompt_file = SCRIPT_DIR / "theory_primitives_prompt.txt"
    prompt_file.write_text(primitives_prompt, encoding="utf-8")
    log(f"  Prompt delle primitive salvato in {prompt_file.name} ({len(primitives_prompt)} char)", log_lines=log_lines)

    # 3. Estrai i 10 sistemi
    log("Estrazione dei 10 sistemi di test...", log_lines=log_lines)
    systems = extract_test_systems(TEST_SYSTEMS_FILE)
    if len(systems) != 10:
        log(f"ATTENZIONE: trovati {len(systems)} sistemi invece di 10", log_lines=log_lines)
        sys.exit(1)
    for sid in sorted(systems.keys(), key=lambda x: int(x[1:])):
        s = systems[sid]
        log(f"  {sid}: {s['title']} ({len(s['description'])} char)", log_lines=log_lines)

    # 4. Esegui 30 chiamate (10 sistemi × 3 LLM)
    log("\nEsecuzione 30 chiamate API...", log_lines=log_lines)
    results = {}
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
            # Prova + 1 retry
            attempt = 0
            last_error = None
            last_raw = None
            while attempt < 2:
                attempt += 1
                try:
                    t0 = time.time()
                    response = caller(primitives_prompt, user_prompt)
                    elapsed = time.time() - t0
                    last_raw = response["raw"]  # salva anche se il parsing fallisce dopo
                    parsed = extract_json_from_response(response["raw"])
                    # Normalizza l'output
                    prims = parsed.get("primitives", [])
                    if not isinstance(prims, list):
                        raise ValueError(f"Output non ha una lista 'primitives': {parsed}")
                    record = {
                        "llm": llm_id,
                        "system": sid,
                        "system_title": s["title"],
                        "attempt": attempt,
                        "elapsed_s": round(elapsed, 2),
                        "model_reported": response.get("model_reported"),
                        "usage": response.get("usage"),
                        "primitives_identified": prims,
                        "primitive_ids": [p.get("id") for p in prims],
                        "n_primitives": len(prims),
                        "raw_response": response["raw"],
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    }
                    output_file.write_text(
                        json.dumps(record, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    log(
                        f"  [OK] {key}: {len(prims)} primitive identificate ({elapsed:.1f}s, attempt {attempt})",
                        log_lines=log_lines,
                    )
                    break
                except Exception as e:
                    last_error = e
                    log(f"  [FAIL] {key} attempt {attempt}: {type(e).__name__}: {e}", log_lines=log_lines)
                    if attempt < 2:
                        time.sleep(3)
            else:
                # tutti e 2 i tentativi falliti
                record = {
                    "llm": llm_id,
                    "system": sid,
                    "system_title": s["title"],
                    "attempt": 2,
                    "error": f"{type(last_error).__name__}: {last_error}",
                    "primitives_identified": [],
                    "primitive_ids": [],
                    "n_primitives": 0,
                    "missing": True,
                    "raw_response_preview": (last_raw[:2000] if last_raw else None),
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
