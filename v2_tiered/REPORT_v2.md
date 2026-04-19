# Report — Esperimento A': Inter-Rater Reliability Tiered

**Eseguito il:** 2026-04-18 23:37 — 2026-04-18 ~00:30 UTC
**Pre-registration:** committata al SHA `b8076d0` su `tsri-experiment-a-inter-rater-llm` (sottocartella `v2_tiered/`) prima di ogni chiamata API.
**Integrità `theory-data.json`:** verificata (SHA-256 `98d277369e...`).
**Impegno di pubblicazione indipendente dall'esito:** rispettato.

---

## 1. Esito in una frase

**Verdetto: GRAY_ZONE.** κ(NUCLEAR) = 0.29, κ ordinale pesato = 0.31. Miglioramento rispetto ad A di +0.05 sul binario equivalente. Il tiering ha **leggermente ridotto** il rumore di soglia ma **non lo ha eliminato** — e ha rivelato un dato più serio: **le 4 primitive nucleari FR della teoria (T1, M2, CO1, N5) non sono mai classificate come NUCLEAR da tutti e 3 gli LLM in nessuno dei 10 sistemi**.

## 2. Numeri

### Metriche primarie

| Metrica | Valore | Soglia H1 | Soglia H0 | Esito |
|---|---|---|---|---|
| **Fleiss κ(NUCLEAR)** | **0.294** | ≥ 0.60 | ≤ 0.40 | **Gray zone** |
| **Fleiss κ ordinale pesato (quadratic)** | **0.311** | ≥ 0.50 | ≤ 0.30 | **Gray zone (borderline H0)** |
| Fleiss κ ordinale pesato (linear) | 0.260 | — | ≤ 0.30 | Sotto soglia H0 |

### Metriche secondarie

| Metrica | κ |
|---|---|
| κ(PRESENT+NUCLEAR) | 0.216 |
| κ(almeno INFERRED = qualsiasi identificazione) | **0.175** |

### Confronto A vs A' (analisi dichiarata in §7 della pre-registration)

| Esperimento | Binario misurato | κ |
|---|---|---|
| A | "primitiva presente" | 0.124 |
| A' | "almeno INFERRED" | **0.175** |
| | **Delta** | **+0.051** |

Il tiering produce un miglioramento misurabile del +5% in κ, ma non nell'ordine di grandezza che separerebbe H0 da zona grigia.

### Pairwise Cohen κ per tier

| Coppia | NUCLEAR | PRESENT+NUCLEAR | almeno INFERRED |
|---|---|---|---|
| Claude ↔ Gemini | **0.371** | 0.320 | 0.218 |
| Claude ↔ OpenAI | 0.327 | 0.237 | 0.211 |
| OpenAI ↔ Gemini | 0.223 | 0.227 | 0.263 |

**Pattern diagnostico**: **Claude e Gemini concordano di più sul NUCLEAR** (κ=0.37) che su qualsiasi altra classificazione. OpenAI resta outlier.

### Distribuzione tier per coder — il dato più informativo

| Coder | NUCLEAR | PRESENT | INFERRED | ABSENT |
|---|---|---|---|---|
| **Claude Sonnet** | 89 (26%) | 109 (32%) | 30 (9%) | 112 (33%) |
| **OpenAI** | 22 (**6%**) | 34 (10%) | 18 (5%) | 266 (**78%**) |
| **Gemini** | 90 (27%) | 58 (17%) | 7 (2%) | 185 (54%) |

OpenAI marca ABSENT nel 78% dei casi — è 2-3 volte più parsimonioso degli altri. La calibrazione del tiering (caveat C3 della pre-registration) è **fallita su OpenAI nella direzione stringente e su Gemini nella direzione generosa** (sistema S4 con 16 NUCLEAR, supera la soglia di 15 dichiarata).

### Recovery delle 4 primitive nucleari FR come NUCLEAR

La teoria (Cap. 7) dichiara T1, M2, CO1, N5 come "senza di esse la struttura non esiste". Il test: quanti sistemi vedono queste 4 primitive classificate come NUCLEAR da tutti e 3 i coder?

| Primitiva | 3/3 NUCLEAR | 2/3 | 1/3 | 0/3 |
|---|---|---|---|---|
| T1 | **0/10** | 1/10 | 3/10 | 6/10 |
| M2 | **0/10** | 2/10 | 2/10 | 6/10 |
| CO1 | **0/10** | 1/10 | 3/10 | 6/10 |
| N5 | **0/10** | 0/10 | 3/10 | 7/10 |

**Zero unanimità NUCLEAR su 40 casi possibili.** Scendendo la soglia a "almeno PRESENT" si recuperano alcuni casi (CO1 3/10, M2 2/10, T1 1/10, N5 0/10), ma il dato grezzo è: tre LLM ben informati sulle definizioni della teoria, davanti al test di rimozione esplicito, **non concordano mai** sulla classificazione di essenzialità delle primitive che la teoria dichiara più essenziali.

---

## 3. Interpretazione — tre letture possibili

### 3.1 Lettura letterale (la più pessimistica)

La teoria ha un problema serio. Le primitive **dichiarate** nucleari non sono **riconosciute** nucleari da tre lettori indipendenti. Il claim "senza T1, M2, CO1, N5 la struttura non esiste" non si traduce in identificazione condivisa. Le definizioni sono insufficientemente discriminanti o genuinamente ambigue.

### 3.2 Lettura metodologica (Giacinto, durante l'esecuzione)

Durante l'esperimento l'autore ha formulato una critica strutturale:

> *"il 'ben addestrati' che base ha? gli LLM hanno davvero compreso la teoria? o stanno semplicemente leggendo delle etichette e li associano per somiglianza? cioè la teoria è molto più sfumata di 'tre righe di descrizione di un sistema complesso' = numero esatto di primitive che lo compongono"*

Questa critica è **epistemicamente corretta**. Il test LLM-as-judge misura la capacità di tre classificatori in-context di convergere su labeling da descrizioni di 150-250 parole con sole definizioni nel prompt. Non misura la capacità della teoria di spiegare, predire, generare. La teoria fa claim strutturali (attrazioni, regolarità, relatività, polimorfismo del tempo) che **nessuna parte di questo test tocca**.

Quando un esperto identifica C1 in un sistema, applica simultaneamente: definizione + conoscenza del dominio + esempi passati + storia di casi studiati + contesto di altre primitive vicine + test di rimozione nel senso *fenomenologico*, non solo linguistico. L'LLM applica: definizione + pattern matching con descrizione + heuristics di severità dal prompt.

**Il test è più povero di quello che la teoria richiede.** Un risultato negativo qui non è, da solo, una falsificazione della teoria — è la misura di una sua proiezione su uno strumento semplice.

### 3.3 Lettura mediana (la più onesta)

Sia la lettura letterale sia quella metodologica sono *in parte* vere. I dati sostengono entrambe:

- **A favore della lettura letterale**: le definizioni nel `theory_primitives_prompt.txt` sono ricche (16.841 caratteri, ogni primitiva con 3-5 aspetti). Un lettore che le studia attentamente *dovrebbe* poterle applicare. Il fatto che tre LLM capaci non convergano suggerisce che le definizioni, per quanto ricche, lasciano margini interpretativi significativi. Questo è rilevante *anche* se volessimo sostituire gli LLM con coder umani senza training — avrebbero lo stesso problema.

- **A favore della lettura metodologica**: gli LLM non hanno visto i 30 casi di validazione per ogni primitiva (doc 004). Non hanno praticato il test di rimozione nel laboratorio semantico. La teoria, come ogni sistema concettuale ricco (pensa alla chimica organica, alla diagnosi medica, al diritto civile), richiede **pratica** — non solo lettura.

La verità è che **entrambi i meccanismi concorrono**: le definizioni sono parzialmente ambigue, e il test è parzialmente insensibile a gradi di maestria che la teoria probabilmente richiede.

---

## 4. Cosa rivelano i dati sulla struttura del problema

### 4.1 L'asimmetria si è spostata al NUCLEAR

Nell'A, OpenAI era parsimonioso nell'**includere** (7 primitive/sistema vs Claude+Gemini 22-24). In A', OpenAI è ancora parsimonioso, ma ora lo è nel classificare come **NUCLEAR** (6% vs Claude+Gemini 26-27%). Il tiering non ha risolto l'asimmetria — l'ha spostata.

Questo è, ironicamente, un segnale che gli LLM hanno **preso seriamente** il prompt: "Sii severo su NUCLEAR, preferisci PRESENT nel dubbio". OpenAI l'ha interiorizzato molto di più di Claude e Gemini.

### 4.2 Claude e Gemini convergono moderatamente sul NUCLEAR

Cohen κ(Claude↔Gemini) sul tier NUCLEAR = 0.37. Non è un accordo forte, ma è il più alto dell'esperimento. Due modelli con pre-training diversi, prompt identici, temperature=0, convergono sul 37% del NUCLEAR in modo non-casuale. Questo è un **piccolo segnale positivo** per la teoria, oscurato dall'outlier OpenAI.

### 4.3 Lo "spread" tiered rivela primitive sistematicamente contese

Nell'output c'è un pattern: alcune primitive hanno spread medio di ~2 tier (massima divergenza possibile). Esempi tipici: Claude dice NUCLEAR, OpenAI dice ABSENT, Gemini dice PRESENT. Queste primitive contese sono candidate naturali per revisione delle definizioni.

L'analisi `per_primitive_tier_agreement` in `results_v2.json` contiene il dettaglio per tutte le 34.

---

## 5. Il problema del ground truth — caveat fondamentale dichiarato

**Un risultato informativo richiede un baseline di confronto che non esiste in questo esperimento.**

Il κ = 0.29 è "basso" o "alto"? La risposta dipende dalla **intra-rater reliability di un esperto della teoria**. Se un coder umano addestrato avesse κ = 0.85 su compiti analoghi, il nostro 0.29 è severo. Se anche un coder umano addestrato avesse κ = 0.50 (comune in ontologie complesse), il nostro 0.29 è comprensibile e il gap è solo -0.21.

**Chi è questo esperto umano?** Non l'autore della teoria (sarebbe sicofanzia su sé stesso — come Giacinto ha giustamente rilevato durante l'esecuzione). Deve essere **un terzo umano addestrato alla teoria**: uno studente, un dottorando, un ricercatore interessato reclutato dalla community. Questo è l'unico ground truth che produce evidenza non circolare.

Senza questo baseline, il risultato dell'A' è **epistemicamente limitato**: sappiamo che 3 LLM non convergono, non sappiamo se 3 umani addestrati convergerebbero. Entrambi potrebbero fallire per ragioni diverse.

---

## 6. Cosa cambia rispetto al REPORT dell'A

Tre cose cambiano nell'interpretazione:

1. **Il tiering funziona, ma poco**. +0.05 di κ è un segnale reale ma insufficiente a spostare il verdetto. La predizione "κ(NUCLEAR) ≥ 0.60" è falsificata.

2. **Le nucleari FR hanno un problema grave**. Zero unanimità NUCLEAR su 40 casi. Questo era già visibile nell'A (solo 11/40 unanimi sulla presenza), ma A' lo aggrava: anche quando presenti, non sono mai riconosciute come *essenziali* da tutti e 3 gli LLM.

3. **La critica dell'autore all'esperimento stesso è ora un caveat formale**. Il REPORT dell'A parlava solo di "asimmetria di soglia di inclusione". Il REPORT dell'A' riconosce il problema più profondo: **il test LLM-as-judge è una proiezione della teoria su uno strumento superficiale**. I risultati H0/gray sono quindi doppiamente ambigui.

---

## 7. Aree aperte e proposta A''

### 7.1 Baseline umano esterno

**Priorità #1**. Reclutare 1-3 volontari esterni (studenti, ricercatori, community TSRI se esiste, tesisti) da addestrare alla teoria e ripetere l'identificazione sui 10 stessi sistemi, con prompt identico. Misurare:

- Intra-rater reliability (stesso coder, due sessioni separate)
- Inter-rater reliability tra coder umani
- Confronto con κ(LLM) per capire se il gap è "teoria" o "strumento"

Costo: zero monetario, richiede ~10h di volontariato + ~2h di formazione per coder.

### 7.2 Esperimento A'' — con esempi in-context

Ritentare con lo stesso setup degli LLM ma aggiungere al prompt **3-5 esempi paradigmatici per ogni primitiva** (dai 30 casi del doc 004). Questo avvicina gli LLM a "con pratica" invece di "solo definizione". Predizione: κ dovrebbe migliorare significativamente se il problema principale è la povertà del test, non le definizioni.

Costo: tempo di selezione degli esempi + stesso costo API (~$2). Il prompt cresce a ~30-50K caratteri — ancora gestibile.

### 7.3 Analisi qualitativa dei disaccordi

Estrarre dagli output grezzi le **ragioni di classificazione** (il `removal_test` in ogni record) per le primitive più contese. Questo produce qualitative insight su come i 3 LLM interpretano il test di rimozione. Da fare in una sessione dedicata.

### 7.4 Revisione mirata delle definizioni

Per le 5 primitive con spread maggiore (da `results_v2.json`), riscrivere definizioni più severe/discriminanti nella teoria. Questo è un intervento sulla teoria stessa, non sul test. Nuovo run misura se il delta migliora.

---

## 8. Pubblicazione e trasparenza

In ottemperanza all'impegno §11 della pre-registration:

- Pre-registration committata al SHA `b8076d0` — prima di ogni chiamata API
- Codice (`run_experiment_v2.py`, `analyze_v2.py`) pubblico
- 30 output grezzi degli LLM in `raw_responses_v2/`
- Matrice ordinale 1020×5 in `coding_matrix_v2.csv`
- Metriche complete in `results_v2.json`
- Log di esecuzione in `execution_log_v2.txt`

Verdetto GRAY_ZONE pubblicato con la stessa evidenza con cui sarebbe stato pubblicato H1.

---

## 9. Nota finale

Questo esperimento è servito a **spostare il fuoco della domanda**. L'A chiedeva "gli LLM concordano?". L'A' ha risposto "sì ma poco, e il tier esplicito non aiuta molto". La domanda che emerge è più profonda:

> *Che tipo di comprensione della teoria serve per identificare le primitive in modo riproducibile?*

Non solo definizioni (abbondanti). Non solo severità (esplicita nel prompt). Ma qualcosa di più — pratica? esempi? conoscenza del contesto? una gestalt che si costruisce solo lavorando con la teoria per mesi?

Se la risposta è sì (la teoria richiede maestria), allora il risultato GRAY_ZONE qui non dice nulla di decisivo. Dice solo che coder naive non convergono bene, il che è prevedibile per qualsiasi sistema concettuale complesso.

Se la risposta è no (la teoria dovrebbe essere usabile da lettore addestrato), allora κ = 0.29 è un verdetto **moderatamente severo** sulla formulazione attuale.

Per distinguere le due letture, serve un baseline umano esterno addestrato. **Questo è il prossimo passo indispensabile.**
