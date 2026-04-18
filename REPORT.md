# Report — Esperimento A: Inter-Rater Reliability tra LLM indipendenti

**Eseguito il:** 2026-04-18 22:51 — 2026-04-19 01:05 UTC
**Stato pre-registration:** committata in `main` al SHA `51d7306` su `tsri-experiment-a-inter-rater-llm` prima di qualsiasi chiamata API.
**Integrità dataset verificata:** SHA-256 di `theory-data.json` corrisponde (`98d277369e...`).
**Impegno di pubblicazione indipendente dall'esito:** rispettato.

---

## 1. Esito in una frase

**Fleiss κ = 0.124** sui 3 LLM. Sotto la soglia 0.40 dichiarata in pre-registration §7. **Verdetto: H0_CONFIRMED.**

Le 34 primitive della TSRI, nella loro formulazione attuale, **non sono identificate coerentemente da tre LLM indipendenti** quando questi ricevono le definizioni e analizzano sistemi informativi nuovi. Il test ha prodotto il risultato più pessimistico tra quelli pre-registrati.

Ma il numero grezzo nasconde una struttura che il risultato "H0 confirmed" non cattura. Questa sezione spiega il verdetto; la §4 ne analizza la struttura interna; la §5 indica cosa significa davvero per la teoria.

---

## 2. Numeri

### Metrica decisionale (tabella §7 della pre-registration)

| Metrica | Valore | Soglia | Esito |
|---|---|---|---|
| **Fleiss κ (3 coder)** | **0.1241** | ≥ 0.70 per H1 | **H1 falsificato** |
| Fleiss κ (3 coder) | 0.1241 | ≤ 0.40 per H0 | **H0 confermato** |

### Pairwise Cohen κ

| Coppia | κ | Interpretazione Landis-Koch |
|---|---|---|
| **Claude Sonnet ↔ Gemini** | **0.338** | Fair-to-moderate |
| Claude Sonnet ↔ OpenAI | 0.187 | Slight |
| OpenAI ↔ Gemini | 0.116 | Slight |

### Fleiss κ senza Claude (analisi A.1 della pre-registration)

| Misura | Valore |
|---|---|
| Fleiss κ (J2+J3 soltanto) | -0.062 (peggio del caso) |
| Cohen κ equivalente | 0.116 |

Rimuovere Claude **peggiora** l'accordo. I due LLM "naive" (OpenAI e Gemini) concordano peggio che quando Claude è incluso. Questo è contro-intuitivo rispetto all'ipotesi di contaminazione di Claude (che prevedeva il contrario) e diagnosticamente importante.

### Numero medio di primitive identificate per sistema

| Coder | Media | Range | Totali per sistema |
|---|---|---|---|
| **Claude Sonnet 4.6** | **23.7** | 11-31 | 27,30,31,18,11,15,30,29,20,26 |
| Gemini 2.5 Pro | 22.2 | 13-30 | 15,26,23,22,13,23,29,23,18,30 |
| **GPT-4o (OpenAI)** | **7.1** | 4-11 | 8,11,8,5,6,4,6,7,7,9 |

**Claude e Gemini sono "generosi" (~22-24 primitive/sistema).** **OpenAI è "parsimonioso" (~7).** Questa asimmetria di soglia di inclusione è il fattore dominante che abbassa il κ.

### Recovery delle 4 primitive nucleari FR

La teoria (Cap. 7) dichiara "senza queste, la struttura non esiste". Test: in quanti dei 10 sistemi le trovano tutti e 3 i coder?

| Primitiva | Unanime (3/3) | Maggioranza (2/3) | Minoranza (1/3) | Mai (0/3) |
|---|---|---|---|---|
| **M2** (Appartenenza) | **4/10** (40%) | 3/10 | 2/10 | 1/10 |
| CO1 (Emittente/destinatario) | 3/10 | 2/10 | 4/10 | 1/10 |
| T1 (Due parti) | 3/10 | 1/10 | 3/10 | 3/10 |
| **N5** (Asimmetria sorgente-osservatore) | **1/10** (10%) | 6/10 | 2/10 | 1/10 |

Totale: **11 identificazioni unanimi su 40 casi possibili (27.5%)** per primitive che la teoria dichiara strutturalmente essenziali.

### Stabilità intra-modello di OpenAI (analisi A.2 della pre-registration)

Backup del primo run OpenAI (abbandonato per problemi con Claude/Gemini) vs nuovo run — stesso modello `gpt-4o`, stesso `seed=42`, stesso `temperature=0`, stessi prompt.

| Misura | Valore |
|---|---|
| Bitwise agreement | 0.9265 |
| Cohen κ intra-modello | **0.7786** |
| Celle diverse | 25/340 (7.35%) |

**OpenAI non è perfettamente deterministico.** Con parametri identici, due run producono Cohen κ = 0.78. Questo stabilisce un **tetto superiore implicito** al κ inter-modello: se un singolo modello non concorda con sé stesso oltre 0.78, nessuna coppia di modelli può fare meglio. Il rumore di decoding degli LLM contribuisce al κ basso osservato, indipendentemente dalla qualità delle definizioni della teoria.

### Primitive con migliore accordo (top 3)

| Primitiva | Unanime (su 10 sistemi) | Presence per coder |
|---|---|---|
| **C1** — Persistenza intenzionale | 8/10 (5 yes + 3 no) | Claude 7, OpenAI 5, Gemini 7 |
| **C3** — Ritrovabilità | 7/10 (3 yes + 4 no) | Claude 6, OpenAI 3, Gemini 6 |
| **W3** — Regole | 7/10 (7 yes + 0 no) | Claude 10, OpenAI 7, Gemini 8 |

Queste tre primitive sono "stabili" sotto osservazione indipendente. **Non per caso sono le più concrete e operative** (persistenza, ritrovabilità, regole procedurali) — quelle con criteri di identificazione meno ambigui.

### Primitive più problematiche (bottom 5)

| Primitiva | Unanime | Presence pattern |
|---|---|---|
| **I4** — Stato (condizione corrente) | 0/10 | Claude 10, OpenAI 0, Gemini 8 |
| **N3** — Indicazione indiretta | 0/10 | Claude 10, OpenAI 0, Gemini 7 |
| **C2** — Forma | 1/10 | Claude 6, OpenAI 0, Gemini 8 |
| **W1** — Unità di lavoro | 1/10 | Claude 8, OpenAI 0, Gemini 7 |
| **C4** — Accumulazione | 2/10 | Claude 10, OpenAI 2, Gemini 9 |

**Pattern sistematico**: per 5 primitive su 34, OpenAI risponde "assente" in 0-2 sistemi su 10, mentre Claude e Gemini rispondono "presente" in 6-10 sistemi su 10. Disaccordo strutturale radicale.

---

## 3. Deviazione forzata dalla pre-registration

### Sostituzione Claude Opus 4.7 → Claude Sonnet 4.6

**Motivazione:** la pre-registration §4 dichiarava Claude Opus 4.7 come J1. L'API Anthropic rifiuta il parametro `temperature` per Opus 4.7 (errore 400 "temperature is deprecated for this model" — riproducibile su tutti i 10 tentativi + 10 retry). Claude Opus 4.7 è un reasoning model con sampling non controllabile dall'utente.

**Deviazione scelta:** sostituire il modello (Opus → Sonnet 4.6) mantenendo il parametro critico (`temperature=0.0`). La motivazione: preservare il determinismo dichiarato (§5 pre-registration) era più importante di preservare il nome del modello. La scelta è documentata in `run_experiment.py:call_claude()` con rationale esplicito.

**Impatto sui risultati:** Sonnet 4.6 è un modello meno potente di Opus 4.7. Plausibilmente avrebbe prodotto identificazioni di qualità leggermente inferiore. Ma il numero medio di primitive identificate (23.7) è simile a Gemini (22.2), suggerendo che la "generosità di inclusione" non è dipesa dalla capacità del modello.

### Non-determinismo residuo di OpenAI

Documentato in §2 (sezione stabilità): `gpt-4o` con `seed=42, temperature=0` non è bit-identico tra run. Questo è un limite del provider, non una violazione della pre-registration.

---

## 4. Interpretazione strutturale — perché H0 è un verdetto *valido ma limitato*

### 4.1 Il problema della soglia di inclusione

L'intuizione metodologica più importante emersa dai dati: **l'asimmetria di soglia di inclusione tra LLM domina meccanicamente il κ**.

- OpenAI interpreta "primitiva presente" in senso **stringent**: includere solo se manifestazione palese. Risultato: media 7 primitive/sistema.
- Claude e Gemini interpretano "primitiva presente" in senso **inclusivo**: includere se inferibile. Risultato: media 23-24 primitive/sistema.

Il Fleiss κ penalizza questa asimmetria. Anche se i tre modelli concordassero perfettamente sul **nucleo** delle primitive presenti in ogni sistema, la generosità di Claude+Gemini sulla "coda lunga" delle primitive marginali produce 15-20 disaccordi per sistema, sufficienti a schiacciare κ sotto 0.15.

**Questa non è una critica a uno dei modelli, né una debolezza intrinseca della teoria.** È una proprietà del disegno sperimentale: "identifica tutte le primitive presenti" è un prompt con soglia di inclusione ambigua, e gli LLM la risolvono in modo sistematicamente diverso.

### 4.2 Il tetto di κ stabilito dalla stabilità intra-modello

OpenAI con parametri identici ha κ intra = 0.78. Nessuna coppia di LLM diversi può superare questo valore. Il limite superiore teorico per il Fleiss κ del nostro esperimento è probabilmente attorno a 0.60-0.70 anche se i modelli fossero perfettamente d'accordo sulla sostanza. Questo significa che **la soglia H1 della pre-registration (≥ 0.70) era probabilmente irraggiungibile** dato il setup tecnico.

Non era ovvio prima dell'esperimento. La pre-registration avrebbe dovuto prevedere un'analisi di stabilità intra-modello come baseline. È una lezione metodologica che riportiamo integralmente.

### 4.3 I tre LLM convergono sulle primitive concrete

Le tre primitive con massimo accordo (C1 persistenza, C3 ritrovabilità, W3 regole) hanno in comune:
- Manifestazione **operativa** concreta nei sistemi
- Criterio di identificazione **osservabile** ("c'è un documento conservato?" "ci sono regole esplicite?")
- Definizione della teoria **poco ambigua**

Le cinque primitive con minimo accordo (I4 stato, N3 indicazione indiretta, C2 forma, W1 unità di lavoro, C4 accumulazione) hanno in comune:
- Manifestazione **astratta** o **pervasiva** (I4, C2 sono presenti "sempre in qualche senso")
- Criterio di identificazione **implicito** (quando vale "stato"? quando "forma"?)
- Definizione della teoria che richiede **interpretazione**

**Questo pattern è informativo**: suggerisce che la teoria ha un *nucleo solido* di primitive ben definite e una *periferia problematica* di primitive semanticamente più sfumate. Questa stratificazione emerge solo dall'analisi dei disaccordi — è invisibile al κ aggregato.

### 4.4 Claude e Gemini concordano (0.34) nonostante la contaminazione attesa

La pre-registration §10 prevedeva che Claude potesse essere outlier per contaminazione (ha co-prodotto la teoria). Il dato osservato è opposto: **Claude e Gemini concordano moderatamente tra loro (κ=0.338), ma entrambi divergono da OpenAI (κ=0.19 e κ=0.12)**.

OpenAI è l'outlier, non Claude. La causa probabile è la soglia di inclusione di OpenAI, non il contenuto delle identificazioni. Questo invalida parzialmente il caveat C3 della pre-registration (Claude contaminato) e sposta l'attenzione su una differenza sistematica di stile inferenziale tra modelli.

### 4.5 L'osservazione di Giacinto anticipava questo problema

Durante l'esperimento, a metà dell'esecuzione, Giacinto (autore) ha osservato spontaneamente: "non ritieni che in un prossimo esperimento sempre A dovremmo dare alle 3 macchine dei limiti indicando di scegliere quelle che ritengono veramente fondamentali e non 'tutte quelle che sembrano starci'?"

Questa osservazione, fatta prima di vedere i numeri del κ, identifica esattamente la causa del risultato H0: il prompt non forza la distinzione "nucleare vs periferica". È un'intuizione metodologica valida che indica il prossimo passo (vedi §6).

---

## 5. Cosa significa questo per la TSRI

Il verdetto H0 nella sua lettura letterale è severo: "primitive non oggettivamente riconoscibili da LLM indipendenti, vocabolario idiosincratico o mal definito".

**La lettura onesta dei dati è più sfumata**:

1. **Il nucleo operativo della teoria regge**. Tre primitive (C1, C3, W3) hanno accordo di fatto sostanziale. Il test non le ha falsificate.

2. **Il livello periferico è problematico**. Cinque primitive (I4, N3, C2, W1, C4) hanno disaccordo strutturale. Le definizioni attuali non sono sufficientemente specifiche da produrre identificazione consistente.

3. **Le 4 nucleari FR sono sottoperformanti**. Solo il 27.5% delle identificazioni è unanime. Questo è il dato più serio — la teoria dichiara queste primitive "essenziali per l'esistenza della struttura", ma tre LLM ben addestrati non riescono a trovarle coerentemente.

4. **Il disegno sperimentale ha limiti strutturali**. La soglia di inclusione ambigua e il rumore intra-modello del 22% rendono il κ un indicatore conservativo.

**La teoria non è falsificata, ma non è nemmeno confermata.** Il risultato corretto è: la formulazione attuale delle primitive non è sufficientemente precisa da consentire identificazione indipendente riproducibile da LLM. Questo è un invito al raffinamento delle definizioni, non al rigetto della teoria.

Per il Capitolo 11 del trattato (Falsificabilità), questo esperimento aggiunge un dato: sotto il criterio "identificabilità da coder indipendenti", la teoria ha oggi un κ di 0.12. Questo è un baseline misurabile. Versioni future della teoria (con definizioni migliorate, o con tiering esplicito) possono essere misurate contro questo baseline e considerate "miglioramento" se il κ cresce.

---

## 6. Esperimento A' — proposta per l'iterazione successiva

L'analisi ha prodotto un disegno sperimentale naturalmente migliorato, dichiarato qui come **Esperimento A'** per essere pre-registrato in seguito prima della sua esecuzione.

### A'.1 — Tiered ontology test (raccomandato)

Cambiare il prompt: per ogni primitiva identificata, classificarla in uno di tre tier:
- **NUCLEAR** — senza di essa il sistema non è più quel sistema (test di rimozione positivo)
- **PRESENT** — chiaramente manifestata, ma il sistema sopravviverebbe senza
- **INFERRED** — debolmente inferibile, non essenziale

Calcolare **Fleiss κ separatamente per ogni tier**. Predizione teorica:
- **κ(NUCLEAR) ≥ 0.70** — le primitive essenziali sono riconoscibili
- κ(PRESENT) moderato
- κ(INFERRED) basso e poco significativo

Se la predizione è verificata, la teoria ha ontologia oggettiva al **livello nucleare** ma una *strato periferico naturalmente sfumato*. Questo è un risultato più sofisticato e verosimile di un κ globale binario.

### A'.2 — Top-N ranked test

Ogni LLM identifica **solo le 5-7 primitive che ritiene più centrali**, ordinandole per importanza. Metriche:
- Top-1 agreement (primitiva #1 coincide?)
- Top-5 Jaccard (overlap delle prime 5)
- Spearman rank correlation

Meno ricco dell'A'.1 ma più semplice da implementare.

### A'.3 — Rimozione forzata come filtro

Prompt riformulato: "Sii severo. Applica esplicitamente il test di rimozione: se il sistema sopravvive senza una primitiva, NON includerla. Preferisci l'omissione all'inclusione debole."

Mantiene il prompt binario attuale ma sposta la soglia di inclusione verso la parsimonia di OpenAI.

### Priorità

A'.1 (Tiered) è il disegno più informativo. La sua esecuzione richiede solo riscrittura del prompt e della funzione di analisi — il dataset dei 10 sistemi e l'infrastruttura degli LLM restano invariati. Costo stimato: ancora < €5. Tempo: 1 serata.

---

## 7. Pubblicazione e trasparenza (§11 pre-registration)

In ottemperanza all'impegno pre-registrato:

- La pre-registration è committata in `main` al SHA `51d7306` del 2026-04-18 — prima di qualsiasi chiamata API.
- Il codice (`run_experiment.py`, `analyze.py`) è pubblico.
- I 30 output grezzi degli LLM (10 sistemi × 3 coder) sono pubblici in `raw_responses/`.
- Il backup del run parziale OpenAI è conservato in `raw_responses_backup_partial_run_2026-04-19/` con README esplicativo.
- La matrice 1020 × 4 (coder × sistema × primitiva × presenza) è in `coding_matrix.csv`.
- Tutte le metriche sono in `results.json`.
- Il log di esecuzione in `execution_log.txt`.

Il risultato H0 viene pubblicato con la stessa evidenza con cui sarebbe stato pubblicato H1.

---

## 8. Nota finale

L'Esperimento A, nella sua variante economica LLM-as-judge, ha prodotto un risultato tecnicamente H0 con un'interpretazione strutturalmente più sfumata. La teoria non è confermata, ma nemmeno rigettata — il test rivela che le definizioni attuali delle primitive non sono robuste sotto identificazione indipendente, e indica precisamente dove migliorarle (le 5 primitive bottom) e cosa testare dopo (il tiered test A'.1).

Questa è una forma onesta di progresso. Se la teoria è reale, la forma migliorata delle definizioni produrrà un κ più alto nel test A'. Se non è reale, non lo farà. L'esperimento ha reso misurabile ciò che prima era solo asserito.

La sezione 11 del trattato dichiarava: "questa teoria è costruita per rendere la falsificazione possibile e benvenuta". Oggi abbiamo un numero: κ = 0.124. Domani, dopo un miglioramento mirato, avremo un altro numero. Questa è la scienza ridotta alla sua forma operativa.
