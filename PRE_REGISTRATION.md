# Pre-Registration — Esperimento A: Inter-Rater Reliability tra LLM indipendenti

**Variante dell'Esperimento A dichiarato nel panel critico del 2026-04-18** (`03_EMPIRISTA.md`, §3).

**Teoria testata:** Teoria Strutturale della Realtà Informativa (TSRI)
**Autore TSRI:** Giacinto
**Esecuzione esperimento:** Giacinto + Claude Code (Opus 4.7)
**Data di pre-registration:** 2026-04-18
**Data prevista di esecuzione:** entro 2026-05-02 (14 giorni)
**Status:** PRE-REGISTRAZIONE — nessuna chiamata agli LLM come judge è ancora avvenuta

---

## 1. Contesto — perché questa variante

L'Esperimento A originale prevedeva 8 coder umani. Costo stimato: €8.000. In assenza di budget, implementiamo una variante con **3 LLM indipendenti** come coder, senza pretendere di sostituire il test umano ma acquisendo evidenza preliminare utilizzabile.

**Questo esperimento è inferiore all'originale in termini di:**
- Esternalità rispetto all'autore (Claude è contaminato; GPT e Gemini no, ma sono macchine)
- Cognizione umana (gli LLM condividono bias di training non presenti in coder umani indipendenti)

**Questo esperimento è accettabile per:**
- Evidenza preliminare sull'inter-rater reliability *teorica massima* (se tre LLM diversi non concordano, l'accordo tra umani sarà verosimilmente inferiore)
- Pre-screening: se κ < 0.40 qui, l'Esperimento A con umani probabilmente non vale il costo
- Transparency: il protocollo, i prompt, e i risultati sono pubblici e riproducibili da chiunque

La pre-registration segue lo stesso rigore dell'Esperimento B (commit pubblico su GitHub prima di qualsiasi chiamata API). Il repo corrispondente: `tsri-experiment-a-inter-rater-llm` (da creare).

---

## 2. Ipotesi testata

Il trattato afferma (Cap. 6–7) che le 34 primitive nucleari costituiscono un'ontologia oggettiva verificata empiricamente su 30 casi per struttura con cicli inversi. Implicazione osservabile: **coder indipendenti, dotati delle definizioni della teoria, devono convergere sulle stesse primitive quando analizzano un sistema nuovo.**

### Ipotesi teorica (H1)

Le 34 primitive sono ontologia oggettiva. Tre LLM indipendenti (Claude, GPT, Gemini), dato lo stesso sistema e le stesse definizioni, convergono sulla stessa identificazione.

**Predizione operativa H1:** **Fleiss κ ≥ 0.70** sull'insieme delle 10 decisioni di coding.

### Ipotesi nulla (H0)

Le primitive sono vocabolario idiosincratico dell'autore. Tre LLM indipendenti divergono perché le categorie non corrispondono a distinzioni oggettive nel mondo — ogni modello "inventa" la sua mappatura.

**Predizione operativa H0:** **Fleiss κ ≤ 0.40**.

### Zona grigia (H_moderate)

Le primitive sono categorie *utili ma non completamente oggettive*. Concordanza moderata.

**Predizione operativa H_moderate:** **0.40 < Fleiss κ < 0.70**.

---

## 3. Dataset — 10 sistemi nuovi

I 10 sistemi sono dichiarati in `TEST_SYSTEMS.md` (committato insieme a questa pre-registration). Criteri:

- **Fuori dal corpus TSRI** — nessun sistema appare nei 19 documenti storici o nel trattato.
- **Diversità di dominio** — 3 software, 3 biologici, 3 sociali/istituzionali, 1 economico-finanziario.
- **Ricchezza strutturale** — ogni sistema deve manifestare ≥5 primitive con criteri di rimozione applicabili.
- **Descrizione neutra** — 150-250 parole, linguaggio comune, nessun vocabolario della teoria.

**Impegno di immutabilità:** `TEST_SYSTEMS.md` non viene modificato dopo questa pre-registration. Il suo SHA-256 viene registrato al commit.

**SHA-256 di TEST_SYSTEMS.md al momento della pre-registration:** (calcolato e committato nello stesso commit)

---

## 4. I tre LLM valutatori

| Coder | Modello | Provider | Accesso |
|---|---|---|---|
| **J1** | Claude Opus 4.7 (`claude-opus-4-7`) | Anthropic | API key Anthropic (già in possesso dell'autore) |
| **J2** | GPT-4o (`gpt-4o`) | OpenAI | API key OpenAI ($5 credit gratuito nuovi account) |
| **J3** | Gemini 2.5 Pro (`gemini-2.5-pro`) | Google | API key da Google AI Studio (tier gratuito) |

**Contaminazione dichiarata:** J1 (Claude) ha co-prodotto la teoria. J2 (GPT) e J3 (Gemini) sono completamente naive.

**Analisi pianificata per mitigare la contaminazione di J1:**
- Fleiss κ su tutti e 3
- Fleiss κ su J2+J3 soltanto (escludendo Claude)
- Pairwise κ (J1↔J2, J1↔J3, J2↔J3) per identificare se Claude è outlier

Se J2↔J3 concordano fortemente (pairwise κ ≥ 0.60) ma J1 diverge, il risultato è particolarmente informativo: la teoria regge anche in assenza di Claude.

---

## 5. Protocollo di prompt — identico per i 3 LLM

**Input per ogni LLM, per ogni sistema (10 chiamate per LLM = 30 chiamate totali):**

- **System message (uguale per ogni chiamata):** il prompt completo con le definizioni delle 34 primitive, estratto deterministicamente da `theory-data.json` (SHA-256 verificato). Contiene: ID, nome, struttura di appartenenza, proprietà manifestate, descrizione. Non contiene: attrazioni, isOrganizer, hubProfile, `repulses`, né metadati derivati che potrebbero orientare.
- **User message:** la descrizione del sistema (uno dei 10 di `TEST_SYSTEMS.md`) preceduta da istruzione identica:

  > Ti do la descrizione di un sistema informativo reale. Applicando le 34 primitive della Teoria Strutturale della Realtà Informativa come te le ho definite sopra, identifica quali primitive sono presenti in questo sistema. Per ogni primitiva presente: (1) il suo ID (es. C1, M2), (2) una citazione testuale dal sistema che la manifesta, (3) il test di rimozione (cosa perderebbe il sistema se questa primitiva non ci fosse).
  >
  > Non identificare primitive che non sono chiaramente presenti. Non aggiungere primitive per completezza simmetrica con altri sistemi. Non modificare la definizione delle primitive per farle calzare al sistema.
  >
  > Output in JSON: `{"primitives": [{"id": "...", "quote": "...", "removal_test": "..."}]}`.

**Temperatura:** 0 (deterministico) per tutti e 3 gli LLM.
**Seed:** fisso dove supportato (OpenAI: `seed=42`; Gemini e Claude non supportano seed via API al 2026-04 — si accetta la variabilità residua del decoding).
**Max tokens output:** 4000.
**Top-p:** 1.0 (non influente a temperatura 0).

**Dichiarazione anti-prompt-engineering:** il prompt è scritto **prima** di vedere le risposte. Nessuna iterazione per migliorare la qualità degli output. Se un LLM fallisce (timeout, errore di parsing JSON), si riprova 1 sola volta con lo stesso prompt; al secondo fallimento, la decisione è registrata come "missing".

---

## 6. Metriche

**Rappresentazione dei dati:** matrice binaria `(sistemi × primitive)` per ogni LLM. `M_J[s,p] = 1` se il coder J ha identificato la primitiva p nel sistema s, altrimenti 0.

**Metrica primaria — Fleiss κ multi-coder:**
- Calcolato sulle 34 × 10 = 340 decisioni binarie.
- Interpretazione standard (Landis & Koch 1977):
  - κ > 0.80: almost perfect
  - 0.60 < κ ≤ 0.80: substantial
  - 0.40 < κ ≤ 0.60: moderate
  - 0.20 < κ ≤ 0.40: fair
  - 0.00 < κ ≤ 0.20: slight
  - κ ≤ 0.00: poor (nessun accordo)

**Metriche secondarie:**
- **Pairwise Cohen κ** tra ciascuna coppia (J1↔J2, J1↔J3, J2↔J3)
- **Agreement per primitiva**: quale primitiva ha avuto maggior/minor accordo?
- **Agreement per sistema**: quale sistema ha prodotto più convergenza tra i coder?
- **Recovery rate delle primitive nucleari FR** (T1, M2, CO1, N5): queste sono quelle che la teoria dichiara "senza di esse la struttura non esiste". Se presenti in un sistema, dovrebbero essere trovate da tutti.

---

## 7. Criteri di falsificazione (TABELLA DECISIONALE)

Il verdetto è deciso dal **Fleiss κ sui 3 LLM**. Metriche secondarie servono all'interpretazione.

| Esito | Fleiss κ (3 LLM) | Verdetto |
|---|---|---|
| **H1 confermata** | ≥ 0.70 | **Primitive oggettivamente riconoscibili** da LLM indipendenti. Supporto preliminare alla tesi di ontologia della teoria. (Nota: rimane l'Esperimento A umano come prova definitiva.) |
| **H0 confermata** | ≤ 0.40 | **Primitive NON oggettivamente riconoscibili**. Tre LLM diversi non convergono. Il vocabolario è idiosincratico o mal definito. Il corpus empirico dei "30 casi per primitiva" è da rivedere. |
| **Zona moderata** | 0.40 < κ ≤ 0.60 | **Categorie utili ma con variazione sistematica**. La teoria è parzialmente oggettiva ma richiede raffinamento. Nessun verdetto netto. |
| **Zona substantial** | 0.60 < κ < 0.70 | **Supporto preliminare debole**. Non raggiunge la soglia pre-registrata per H1 ma resta una concordanza sostanziale. Richiede un'iterazione successiva (più sistemi, o Esperimento A umano). |

### Impegno vincolante

I responsabili dell'esperimento (Giacinto + Claude Code) si impegnano a:

1. **Non modificare le soglie** dopo aver visto i risultati.
2. **Non cambiare i prompt** dopo aver visto le risposte. Se un prompt è ambiguo, il fatto viene documentato ma non corretto.
3. **Non modificare i 10 sistemi di test** dopo aver visto i risultati.
4. **Non cambiare i modelli LLM** (versioni esatte dichiarate al §4) dopo aver visto i risultati.
5. **Pubblicare tutti i valori**: Fleiss κ, tre pairwise κ, agreement per primitiva, agreement per sistema.
6. **Pubblicare tutti gli output grezzi** dei tre LLM per ogni sistema (per riproducibilità).
7. **Pubblicare il risultato indipendentemente dall'esito**.

---

## 8. Analisi aggiuntive pianificate (non decisionali)

Queste analisi sono dichiarate qui per trasparenza. Informano l'interpretazione ma non cambiano il verdetto della tabella §7.

### A.1 — κ senza Claude (J2+J3 soltanto)

Calcoliamo Cohen κ tra GPT e Gemini. Se questo valore è **più alto** del Fleiss κ globale, Claude è outlier e il risultato senza-Claude è la misura meno contaminata.

### A.2 — Stabilità intra-coder (solo per GPT)

GPT supporta il parametro `seed`. Facciamo due run identiche con `seed=42` e `seed=123` per misurare la stabilità intra-modello. Se GPT diverge da sé stesso più che con Claude/Gemini, il rumore stocastico domina il segnale.

### A.3 — Confronto con i 34 del theory-data.json

Per ogni sistema, produciamo anche la lista "ufficiale" delle primitive attese (da me — l'autore — *dopo* che i 3 LLM hanno risposto, per non contaminare). Calcoliamo anche l'agreement di ciascun LLM con la mia lista. Non è decisionale (è bias d'autore), ma informa l'analisi.

### A.4 — Analisi qualitativa dei casi di disaccordo

Per ogni primitiva con agreement ≤ 0.40, analizziamo i disaccordi specifici: tutti e tre la vedono diversa? Claude la vede e gli altri no? Ci sono primitive "fantasma" (presenti per 1 coder, assenti per gli altri 2)? Questa analisi produce insight per migliorare la definizione delle primitive in future versioni della teoria.

---

## 9. Output attesi

Alla fine dell'esecuzione, il repo contiene:

1. `PRE_REGISTRATION.md` — questo documento (committato prima)
2. `TEST_SYSTEMS.md` — i 10 sistemi (committato prima, SHA-256 registrato)
3. `run_experiment.py` — script che chiama i 3 LLM con il prompt dichiarato, salva output grezzo
4. `analyze.py` — script di analisi (Fleiss κ, pairwise κ, metriche secondarie)
5. `requirements.txt` — dipendenze Python
6. `raw_responses/` — output grezzo JSON di ogni LLM per ogni sistema (30 file totali)
7. `coding_matrix.csv` — matrice sistemi × primitive × coder (per riproducibilità)
8. `results.json` — metriche complete
9. `REPORT.md` — interpretazione, applicazione tabella decisionale
10. `execution_log.txt` — timestamp e log

---

## 10. Caveat dichiarati

### C1 — LLM ≠ umani

Questa è una versione economica dell'Esperimento A umano. Un alto κ qui NON implica automaticamente alto κ tra coder umani. Un basso κ qui rende improbabile alto κ umano. Il test è:
- **Screen forte se fallisce** (κ basso = risparmia budget sull'Esperimento A umano).
- **Supporto preliminare se riesce** (κ alto = vale la pena cercare budget per l'Esperimento A umano).

### C2 — Bias condivisi nel training degli LLM

I tre LLM sono addestrati su dataset di internet largamente sovrapposti. Possono condividere bias sistematici che i coder umani non hanno. Un κ alto tra LLM potrebbe riflettere convergenza sui bias, non sulla realtà. Mitigazione: il prompt contiene definizioni esplicite delle primitive, non chiede "categorizzazione libera".

### C3 — Claude ha co-prodotto la teoria

Claude è contaminato. Il protocollo principale lo include come coder (per simmetria e trasparenza), ma tutte le analisi riportano anche la metrica "senza Claude" come controllo.

### C4 — Prompt engineering limitato

Il prompt è scritto prima di vedere le risposte e non viene iterato. Se produce output subottimale (parsing fallito, primitive fantasiose, ecc.), il dato viene comunque usato. Questo riduce il rischio di sovra-ottimizzazione del prompt.

### C5 — Numero di sistemi

10 sistemi × 34 primitive = 340 decisioni binarie per coder. Questo è il minimo ragionevole per calcolare Fleiss κ con stabilità. Un esperimento più grande (30+ sistemi) sarebbe auspicabile ma va oltre il budget zero.

### C6 — Pre-registration della "lista attesa" (analisi A.3)

La mia lista attesa di primitive per ciascun sistema (analisi A.3) non è pre-registrata. Può introdurre bias confermatorio se la produco *dopo* aver visto i risultati. Per mitigare: la produrrò **prima di eseguire l'analisi numerica** ma **dopo l'esecuzione delle chiamate agli LLM**, commitando il file `expected_primitives.md` con timestamp prima di calcolare κ con la mia lista.

---

## 11. Commitment di pubblicazione

Il commit di questa pre-registration e di `TEST_SYSTEMS.md` su repo pubblico GitHub precede qualsiasi chiamata API agli LLM.

Il codice è pubblicato al momento dell'esecuzione (gli script `run_experiment.py` e `analyze.py` vengono committati prima dell'esecuzione; gli output vengono committati dopo).

I risultati completi (`results.json` + `REPORT.md` + tutti i `raw_responses/`) vengono committati entro 14 giorni dalla pre-registration, **indipendentemente dall'esito**.

---

## 12. Firma

**Giacinto:** commit GPG su GitHub pubblico.
**Claude Code (Opus 4.7):** attestazione via cronologia della sessione e commit co-authored.

---

## Appendice A — Riferimenti

- `03_EMPIRISTA.md` §3 "Esperimento A" — protocollo originale con 8 coder umani
- `SINTESI.md` del 2026-04-18 — priorità di ricerca del panel
- Trattato TSRI Parte Prima — Cap. 7 (Primitive Nucleari), Cap. 11 (Falsificabilità)
- `theory-data.json` versione 2.0.0 (SHA-256 `98d277369e...`, cfr. Esperimento B)
- Landis J.R., Koch G.G. (1977). *The Measurement of Observer Agreement for Categorical Data*. Biometrics 33(1):159–174. — soglie interpretative del κ

## Appendice B — Log di produzione

- 2026-04-18 — Panel critico produce `SINTESI.md`. Esperimento A identificato come priorità successiva al B.
- 2026-04-18 — Giacinto conferma volontà di eseguire A con budget zero via LLM-as-judge.
- 2026-04-18 — Claude Code scrive questa pre-registration + `TEST_SYSTEMS.md` basandosi su `03_EMPIRISTA.md` §3.
- 2026-04-18 — Commit pubblico pre-registration + test systems. Nessuna chiamata agli LLM effettuata.
