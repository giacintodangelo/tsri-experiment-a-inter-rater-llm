# Pre-Registration — Esperimento A': Inter-Rater Reliability Tiered

**Variante dell'Esperimento A originale proposta dai dati dell'A stesso** (`../REPORT.md` §6).
**Esperimento A' al setup identico dell'A, con un'unica modifica: il prompt introduce tre tier di essenzialità (NUCLEAR / PRESENT / INFERRED).**

**Teoria testata:** Teoria Strutturale della Realtà Informativa (TSRI)
**Autore TSRI:** Giacinto
**Esecuzione esperimento:** Giacinto + Claude Code (Opus 4.7)
**Data di pre-registration:** 2026-04-19
**Data prevista di esecuzione:** entro 2026-05-03 (14 giorni)
**Status:** PRE-REGISTRAZIONE — nessuna chiamata agli LLM come judge è ancora avvenuta con questo prompt

---

## 1. Motivazione — perché A' e non solo A

L'Esperimento A (eseguito 2026-04-18, repo `tsri-experiment-a-inter-rater-llm`, commit `6d44bdf`) ha prodotto **Fleiss κ = 0.124** (H0 confermato per la tabella decisionale). L'analisi dei dati ha rivelato che **l'asimmetria di soglia di inclusione tra LLM domina meccanicamente il κ**:

- Claude Sonnet 4.6: media 23.7 primitive/sistema (generoso)
- Gemini 2.5 Pro: media 22.2 (generoso)
- GPT-4o (OpenAI): media 7.1 (parsimonioso)

Il prompt dell'A chiedeva "identifica tutte le primitive presenti" con soglia ambigua ("chiaramente presente"). Gli LLM l'hanno risolta in modi sistematicamente diversi, producendo disaccordo meccanico.

L'intuizione metodologica che ha generato A' è stata espressa dall'autore durante l'esecuzione dell'A: "non ritieni che in un prossimo esperimento sempre A dovremmo dare alle 3 macchine dei limiti indicando di scegliere quelle che ritengono veramente fondamentali e non 'tutte quelle che sembrano starci'?"

L'A' risponde a questa osservazione forzando la **prioritizzazione in tier**.

### Valore epistemico

Questo esperimento A' è **un secondo test della stessa teoria con uno strumento più selettivo**. Se le primitive della TSRI costituiscono un'ontologia oggettiva, il tier NUCLEAR dovrebbe avere accordo alto anche se l'accordo sul totale è basso. Se il risultato è negativo anche sul NUCLEAR, la teoria ha un problema ontologico reale e non solo un problema di formulazione del prompt.

---

## 2. Ipotesi testate (multiple)

### H1_NUCLEAR (teoria)

Le primitive classificate come **NUCLEAR** (essenziali — test di rimozione positivo) sono oggettivamente riconoscibili. Tre LLM indipendenti convergono sul NUCLEAR anche se divergono sui tier inferiori.

**Predizione operativa H1_NUCLEAR:** **Fleiss κ (tier NUCLEAR) ≥ 0.60**.

### H1_ORDINAL (teoria forte)

Esiste un gradiente oggettivo di essenzialità. L'ordinamento tier NUCLEAR > PRESENT > INFERRED è condiviso dai tre LLM.

**Predizione operativa H1_ORDINAL:** **Fleiss κ pesato (trattando tier come ordinali) ≥ 0.50**.

### H0 (alternativa)

Nessun tier produce accordo significativo. Il tiered approach non risolve il disaccordo — lo sposta di livello senza eliminarlo.

**Predizione operativa H0:** **Fleiss κ (tier NUCLEAR) ≤ 0.40 E Fleiss κ pesato ≤ 0.30**.

### Zona grigia

Risultati intermedi: tier NUCLEAR moderato (0.40-0.60), oppure ordinal moderato (0.30-0.50).

---

## 3. Dataset — identico all'A

**Riuso integrale dei 10 sistemi dell'Esperimento A** (`../TEST_SYSTEMS.md`, SHA-256 registrato nel commit `51d7306` del repo `tsri-experiment-a-inter-rater-llm`).

Non modifichiamo il dataset perché:
1. L'obiettivo di A' è **isolare l'effetto del prompt**, tenendo tutto il resto costante.
2. Un confronto diretto con i risultati di A (stessi sistemi, stessi LLM) è più informativo di un dataset nuovo.

**Impegno di immutabilità:** i 10 sistemi non vengono modificati. Se per qualche motivo il file `TEST_SYSTEMS.md` dell'A fosse modificato, A' viene invalidato e re-pre-registrato.

**theory-data.json**: identico (SHA-256 `98d277369e...`, registrato nel commit corrente). Verifica integrità al runtime.

---

## 4. I tre LLM valutatori — identici all'A

| Coder | Modello | Note |
|---|---|---|
| J1 | `claude-sonnet-4-6` | Stessa sostituzione dell'A (Opus 4.7 incompatibile con `temperature=0`) |
| J2 | `gpt-4o` | Identico all'A |
| J3 | `gemini-2.5-pro` | Identico all'A |

Parametri: `temperature=0`, `seed=42` dove supportato, `max_tokens=8000`.

---

## 5. Prompt — la variabile unica che cambia

### Prompt di sistema

**Identico all'A**: le definizioni delle 34 primitive da `theory_primitives_prompt.txt` generato deterministicamente da `theory-data.json`. Nessuna modifica.

### Prompt utente

**Sostituito integralmente**. La versione A' è riportata qui letteralmente:

---

> Ti do la descrizione di un sistema informativo reale. Applicando le 34 primitive della Teoria Strutturale della Realta' Informativa come te le ho definite sopra, identifica quali primitive sono presenti e **classifica ciascuna in uno di tre livelli di essenzialita'**.
>
> **NUCLEAR** — Senza questa primitiva, il sistema non e' piu' *quel* sistema. Se la togli, crolla l'identita' stessa del fenomeno descritto. Applica letteralmente il **test di rimozione**: "il sistema cesserebbe di essere cio' che e'?" Se si', la primitiva e' NUCLEAR. Sii **severo** — riserva NUCLEAR solo alle primitive strutturalmente indispensabili all'identita' del sistema. Nel dubbio, preferisci PRESENT.
>
> **PRESENT** — Chiaramente manifestata nel sistema, ma non essenziale per la sua identita'. Se la togli, il sistema e' impoverito ma resta riconoscibilmente quello stesso sistema.
>
> **INFERRED** — Debolmente inferibile, il sistema la manifesta in qualche senso sottile o periferico. Puo' essere omessa senza perdere informazione sostanziale sull'identita' del sistema.
>
> **Non includere** primitive totalmente assenti. Non aggiungere primitive per completezza simmetrica. Non modificare la definizione delle primitive per farle calzare al sistema.
>
> Per ogni primitiva identificata, fornisci:
> 1. ID (es. C1, M2)
> 2. tier (NUCLEAR, PRESENT, o INFERRED)
> 3. citazione testuale dal sistema che la manifesta
> 4. test di rimozione esplicito ("se tolgo X, il sistema... [resta / collassa / si impoverisce]")
>
> Output in JSON: `{{"primitives": [{{"id": "...", "tier": "NUCLEAR|PRESENT|INFERRED", "quote": "...", "removal_test": "..."}}]}}`.
>
> Sistema da analizzare:
>
> {title}
>
> {description}

---

### Razionale delle scelte del prompt

1. **Severità esplicita sul NUCLEAR**: "Sii severo" + "Nel dubbio preferisci PRESENT" crea bias verso la parsimonia. Il test di rimozione è il criterio operativo della teoria stessa (Cap. 6-7).
2. **Tre tier invece di due**: un approccio binario (NUCLEAR/not) produrrebbe un test troppo grezzo. Tre tier permettono un gradiente ordinale.
3. **INFERRED come escape**: invece di forzare l'LLM a dire "presente o assente", fornisce un livello intermedio per le identificazioni ambigue — riducendo l'asimmetria di soglia di A.
4. **Test di rimozione esplicito nell'output**: rende l'LLM "responsabile" della classificazione — non può marcare NUCLEAR senza giustificare.

---

## 6. Metriche

**Rappresentazione dei dati**: per ogni (coder, sistema, primitiva), la cella contiene uno di 4 valori: NUCLEAR, PRESENT, INFERRED, ABSENT (implicito se non menzionata). 3 × 10 × 34 = 1020 decisioni multi-classe.

### Metrica primaria 1 — Fleiss κ sul tier NUCLEAR

Binarizzo: NUCLEAR=1, altri=0. Calcolo Fleiss κ. Misura l'accordo sulle primitive *essenziali*.

### Metrica primaria 2 — Fleiss κ pesato ordinale

Considero i 4 livelli come ordinali: ABSENT=0, INFERRED=1, PRESENT=2, NUCLEAR=3. Calcolo Fleiss κ pesato (linear weights) — penalizza meno i disaccordi di un solo tier rispetto a disaccordi di più tier.

### Metriche secondarie

- **Fleiss κ sul tier PRESENT (binarizzato)**: accordo sulle primitive chiaramente manifestate
- **Fleiss κ sul tier INFERRED (binarizzato)**: accordo sulle primitive debolmente manifestate
- **Fleiss κ su "almeno INFERRED" (binarizzato)**: accordo binario sulla *presenza* (equivalente all'Esperimento A, per confronto diretto)
- **Pairwise Cohen κ** su ogni tier, tra ogni coppia
- **Confusion matrix 4×4** tra ogni coppia di coder (ABSENT/INFERRED/PRESENT/NUCLEAR)
- **Recovery rate delle primitive nucleari FR della teoria** (T1, M2, CO1, N5): quante volte identificate come tier NUCLEAR da tutti e 3 i coder?

---

## 7. Tabella decisionale

La decisione si basa sulle **due metriche primarie**. Richiediamo che *entrambe* le condizioni siano soddisfatte per dichiarare una delle ipotesi.

| Esito | κ(NUCLEAR) | κ pesato ordinale | Verdetto |
|---|---|---|---|
| **H1 confermata** | ≥ 0.60 | ≥ 0.50 | Le primitive essenziali sono oggettivamente riconoscibili. Il gradiente di essenzialità è condiviso. |
| **H1 confermata parziale** | ≥ 0.60 | < 0.50 | Le primitive essenziali sono riconoscibili, ma il gradiente sotto-NUCLEAR è ambiguo. |
| **H1 confermata ordinale** | < 0.60 | ≥ 0.50 | C'è accordo sul gradiente ma non sulle soglie specifiche. |
| **Zona grigia** | 0.40-0.60 | 0.30-0.50 | Supporto parziale, né conferma né falsificazione. |
| **H0 confermata** | ≤ 0.40 | ≤ 0.30 | Nessun tier produce accordo. Il problema non è di prompt, è di definizione. |

### Confronto con A

Oltre al verdetto A', il risultato viene **confrontato direttamente** con l'Esperimento A:
- **Confronto A vs A' su "almeno INFERRED"** (binarizzato, equivalente ad A): il κ migliora con il tiering?
- Se l'Esperimento A ha prodotto κ = 0.124 su binario "presente/assente", A' dovrebbe mostrare κ superiore sulla stessa binarizzazione, se il tiering riduce il rumore di soglia.

### Impegno vincolante

Gli stessi impegni dell'A:
1. Non modificare le soglie dopo aver visto i risultati.
2. Non modificare il prompt dopo aver visto le risposte.
3. Non modificare il dataset dopo aver visto i risultati.
4. Pubblicare tutti i valori e tutti gli output grezzi.
5. Pubblicare il risultato indipendentemente dall'esito.

---

## 8. Output attesi

Alla fine dell'esecuzione, il repo sottocartella `v2_tiered/` conterrà:

1. `PRE_REGISTRATION.md` — questo documento
2. `run_experiment_v2.py` — pipeline tiered
3. `analyze_v2.py` — metriche per-tier
4. `raw_responses_v2/` — 30 output LLM grezzi
5. `coding_matrix_v2.csv` — matrice ordinale sistemi × primitive × coder
6. `results_v2.json` — metriche complete
7. `REPORT_v2.md` — interpretazione + confronto con A
8. `execution_log_v2.txt` — log di esecuzione

---

## 9. Caveat dichiarati (oltre a quelli dell'A)

### C1 — Il test di rimozione è soggettivo anche se esplicito

Chiedere all'LLM di applicare il test di rimozione non garantisce che lo applichi rigorosamente. Può marcarlo pro-forma. Mitigazione: il prompt richiede **output esplicito** del test ("il sistema... [resta/collassa/si impoverisce]"). Un'analisi qualitativa a campione verifica la qualità del ragionamento.

### C2 — I 3 tier sono una scelta arbitraria

Potrebbero essere 2 (Nucleare/Non-nucleare), 4 (con un livello "core" distinto da NUCLEAR), o una scala continua. La scelta dei 3 è motivata dalla semplicità e dall'allineamento con il modello a cerchi concentrici della teoria (nucleo + profondità + confini), ma è una decisione di design.

### C3 — Il prompt severo potrebbe sotto-identificare

Spingendo verso la parsimonia nel NUCLEAR, si rischia che tutti e 3 gli LLM marchino pochissime primitive come NUCLEAR — producendo κ sul NUCLEAR alto artificialmente (accordo su "assente" per la maggior parte delle primitive). Mitigazione: riportare anche il **numero medio di primitive marcate NUCLEAR** per ogni LLM e per sistema. Se la media è < 2 o > 10, il tier è mal calibrato e i risultati vanno letti con cautela.

### C4 — Lo stesso dataset dell'A può produrre memoria

I 3 LLM sono chiamati in API, stateless. Nessuna memoria di sessione. Tuttavia, se l'autore o Claude Code ha pubblicato i 10 sistemi in forma indicizzata da motori di ricerca, c'è un rischio teorico di leakage nei modelli training successivi. Per questa esecuzione il rischio è basso (pubblicazione avvenuta 2026-04-18, 24h prima).

### C5 — LLM ≠ umani (come nell'A)

Mitigazione invariata dall'A.

---

## 10. Commitment di pubblicazione

Il commit di questa pre-registration su GitHub pubblico precede qualsiasi chiamata API con il prompt tiered. Il codice `run_experiment_v2.py` e `analyze_v2.py` sono committati **prima** dell'esecuzione.

I risultati completi vengono committati entro 7 giorni dall'esecuzione, indipendentemente dall'esito.

**Clausola di trasparenza sul fallimento:** se A' produce H0 (ancora), il fatto viene riportato senza ridimensionamenti. Un doppio H0 (A e A') sarebbe un segnale forte contro l'ontologia della teoria nella sua formulazione attuale — o contro il disegno LLM-as-judge per testarla — e va registrato come tale.

---

## 11. Firma

**Giacinto**: commit GPG su GitHub pubblico tramite repo `tsri-experiment-a-inter-rater-llm` (sottocartella `v2_tiered/`).
**Claude Code (Opus 4.7)**: attestazione via cronologia della sessione e commit co-authored.

---

## Appendice A — Log di produzione

- **2026-04-19 ~01:00 UTC** — Esperimento A completato con κ=0.124 (H0). Report pubblicato.
- **2026-04-19 ~01:30 UTC** — Giacinto conferma proseguimento con A' Tiered.
- **2026-04-19 (ora corrente)** — Claude Code scrive questa pre-registration + codice, committa tutto PRIMA di ogni chiamata API.

## Appendice B — Riferimenti

- Esperimento A originale: `../PRE_REGISTRATION.md`, `../REPORT.md`, commit `6d44bdf` del repo `tsri-experiment-a-inter-rater-llm`.
- Sistemi di test: `../TEST_SYSTEMS.md` (invariato, SHA-256 già registrato).
- Dataset teoria: `engine/theory-data.json` SHA-256 `98d277369e0213d54f55910ea8157c86dc3a690e3f8cbb81605fa036b8401b5a`.
- Intuizione originaria di Giacinto: messaggio del 2026-04-18, citato nel §1.
- Proposta A'.1 Tiered: `../REPORT.md` §6.
- Landis J.R., Koch G.G. (1977) per la lettura del κ.
- Cohen J. (1968). *Weighted kappa: Nominal scale agreement with provision for scaled disagreement or partial credit*. — per il κ pesato ordinale.
