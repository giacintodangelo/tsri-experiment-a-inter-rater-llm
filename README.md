# Esperimento A — Inter-Rater Reliability tra LLM indipendenti

**Teoria testata:** Teoria Strutturale della Realtà Informativa (TSRI) — Cap. 7 "Primitive Nucleari".

**Domanda:** date le definizioni delle 34 primitive della TSRI, tre LLM indipendenti (Claude, GPT, Gemini) analizzano 10 sistemi informativi nuovi. Convergono sulle stesse primitive?

Se sì (Fleiss κ ≥ 0.70) → supporto preliminare alla tesi di ontologia oggettiva.
Se no (Fleiss κ ≤ 0.40) → vocabolario idiosincratico dell'autore.
Se intermedio → categorie utili ma con variazione sistematica.

**Status:** pre-registrato. Nessuna chiamata agli LLM effettuata prima di questo commit.

## Questa è una variante economica dell'Esperimento A originale

L'Esperimento A del panel critico del 2026-04-18 prevedeva 8 coder umani (costo €8.000). Questa variante usa 3 LLM come coder e costa <€5. Non sostituisce il test umano — lo **screen forte**: se gli LLM non convergono, gli umani molto probabilmente non convergeranno nemmeno.

## Integrità della pre-registration

| File | SHA-256 | Status |
|---|---|---|
| `PRE_REGISTRATION.md` | `22b7a7bd272ced470bbe4cbe23a2ae5fa5ed51e10894322c98f14b13adcc2850` | Committato prima del codice |
| `TEST_SYSTEMS.md` | `a6bca9ea15f79e1a61b0b923b6197327c304364b255243a96fa4e025aa36408f` | Committato prima del codice |

## Struttura del repo

- `PRE_REGISTRATION.md` — ipotesi, metodo, criteri di falsificazione
- `TEST_SYSTEMS.md` — i 10 sistemi di test, scelti fuori dal corpus TSRI
- `run_experiment.py` — chiama i 3 LLM con il prompt dichiarato (scritto prima dell'esecuzione)
- `analyze.py` — Fleiss κ + pairwise κ + metriche secondarie
- `raw_responses/` — output grezzo dei 30 run LLM (3 × 10)
- `coding_matrix.csv` — matrice binaria sistemi × primitive × coder
- `results.json` — metriche complete
- `REPORT.md` — interpretazione dei risultati
- `requirements.txt` — dipendenze Python

## Riproduzione

```bash
# Serve: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY in ambiente
pip install -r requirements.txt
python run_experiment.py
python analyze.py
```

## Pubblicazione

I risultati vengono pubblicati indipendentemente dall'esito, entro 14 giorni dalla pre-registration.
