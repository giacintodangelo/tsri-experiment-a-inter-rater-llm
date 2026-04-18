# Test Systems — Esperimento A

**Criterio di selezione:**
1. **Fuori dal corpus della TSRI**: il sistema non deve apparire in nessuno dei 19 documenti storici né nel trattato. Evitare: alveare/api, ospedale, palestra, animal shelter, Via della Seta, feudalesimo, rete micoridica, catena alimentare, sistema nervoso, sinapsi/neuroni, monasteri benedettini, forum online, alleanze pre-WWI, tela di Penelope, ragnatele, rete fluviale, arazzo di Bayeux, affresco Sistina, raga indiano, metropolitana Londra, Kubernetes, Neo4j, Spotify, Google PageRank, Facebook.
2. **Ricchezza strutturale**: ogni sistema deve manifestare almeno 5-7 primitive con criteri di rimozione applicabili.
3. **Diversità di dominio**: 3-4 software, 3 biologico/naturale, 3-4 sociale/istituzionale.
4. **Descrizione neutra e atomicamente scritta**: nessun vocabolario tecnico della teoria, nessun "segnale" che orienti l'LLM.

Ogni sistema è descritto in 150-250 parole (~1 paragrafo), linguaggio comune, italiano.

---

## S1 — Sistema di prenotazione voli (tipo Kayak/Skyscanner)

Una piattaforma web permette agli utenti di cercare voli tra coppie di aeroporti in date specifiche. L'utente inserisce aeroporto di partenza, aeroporto di arrivo, date, numero di passeggeri. La piattaforma interroga decine di compagnie aeree e aggregatori, mostra una lista di opzioni ordinabili per prezzo, durata, numero di scali. Ciascuna opzione mostra compagnia, orari, prezzo corrente, disponibilità residua di posti. L'utente può aggiungere filtri (bagaglio incluso, solo diretti, orari specifici). Quando seleziona un'opzione, la piattaforma lo reindirizza al sito della compagnia per il pagamento. La piattaforma non vende direttamente — guadagna una commissione. I prezzi fluttuano nel corso della giornata in base alla domanda e all'algoritmo dinamico delle compagnie. Gli utenti registrati ricevono avvisi email quando il prezzo di una rotta monitorata scende sotto una soglia. Le statistiche di ricerca aggregate vengono vendute alle compagnie come intelligence di mercato.

---

## S2 — Patch Tuesday Microsoft

Ogni secondo martedì del mese, Microsoft rilascia un pacchetto cumulativo di aggiornamenti di sicurezza per Windows, Office e gli altri prodotti della famiglia. Nei 30 giorni precedenti, vulnerabilità vengono segnalate a Microsoft tramite canali ufficiali (Microsoft Security Response Center, MSRC) — dai ricercatori indipendenti, dai vendor di antivirus, dal programma Bug Bounty. Ogni segnalazione riceve un identificativo CVE, viene classificata per gravità (Critical/Important/Moderate/Low), e assegnata a un team interno. Prima della release, le patch vengono testate internamente e con un gruppo di Insider. Il giorno del rilascio, le patch vengono distribuite attraverso Windows Update: i client le scaricano in background, richiedono riavvio, applicano il fix. Gli amministratori aziendali possono posticipare il deploy di 30 giorni tramite WSUS o Intune. Ciascuna patch ha un bollettino pubblico che descrive la vulnerabilità risolta, i sistemi affetti, eventuali workaround temporanei. I nuovi attaccanti, dopo il martedì, reverse-engineerizzano le patch per sfruttare i client non aggiornati — il fenomeno detto "exploit Wednesday".

---

## S3 — Replit (IDE collaborativo live)

Un ambiente di programmazione nel browser dove più persone possono scrivere codice nello stesso file contemporaneamente. Ogni utente ha un cursore colorato visibile agli altri in tempo reale. Il codice viene eseguito su server condivisi — ogni "Repl" ha CPU, memoria, e storage limitati, suddivisi in tier (free, hacker, teams). I file sono versionati automaticamente con checkpoint ogni pochi secondi. Gli utenti possono invitare collaboratori con permessi read/write/admin. Un sistema di chat integrata accompagna il codice. Il Replit ha "Ghostwriter", un assistente AI che suggerisce completamenti e può generare codice da descrizioni. I progetti pubblici sono ricercabili, fork-abili, citabili. Le esecuzioni di programmi usano il quota mensile dell'account; se esaurito, l'esecuzione viene bloccata o rallentata. Un marketplace permette di vendere template. Gli amministratori di un team vedono dashboard con attività dei membri: ore spent, linee di codice, pattern di collaborazione. Quando un Repl non viene modificato per 6 mesi in account free, viene archiviato.

---

## S4 — Regolazione endocrina della glicemia

Il corpo umano mantiene la concentrazione di glucosio nel sangue in una finestra ristretta (~70-100 mg/dL a digiuno). Due ormoni operano in opposizione. L'insulina, prodotta dalle cellule beta del pancreas, viene rilasciata quando il glucosio sale dopo un pasto: si lega a recettori sulle cellule muscolari, adipose e epatiche, che aprono canali e assorbono glucosio dal sangue. Il glucagone, prodotto dalle cellule alfa, fa il contrario: quando il glucosio scende (digiuno, esercizio), stimola il fegato a rilasciare glucosio dalle riserve di glicogeno. Il pancreas riceve il segnale dal glucosio stesso attraverso meccanismi di percezione chimica. Il cervello consuma glucosio esclusivamente: una caduta prolungata porta a confusione, svenimento, coma. Se l'insulina è insufficiente o le cellule sono resistenti (diabete), il glucosio resta elevato nel sangue danneggiando vasi, reni, nervi nel lungo termine. Il test HbA1c misura la glicemia media degli ultimi 3 mesi integrando l'esposizione dei globuli rossi al glucosio.

---

## S5 — Metamorfosi della rana

Una rana nasce come girino acquatico: corpo pesciforme, coda, branchie interne, dieta onnivora basata su alghe e detrito. Per settimane vive in acqua stagnante, cresce, accumula massa. A un certo punto — determinato da temperatura, disponibilità di cibo, livelli ormonali — inizia la metamorfosi. L'ormone tiroideo tirosina scatena una riorganizzazione radicale: spuntano le zampe posteriori, poi le anteriori, si formano i polmoni, le branchie regrediscono, la coda viene riassorbita, il tubo digerente si accorcia e si adatta a dieta carnivora, la pelle cambia struttura. Durante questa fase il girino è vulnerabile — nuota male, non mangia, deve stare vicino alla superficie per respirare con i polmoni in formazione. Quando la metamorfosi è completa, la rana adulta esce dall'acqua, colonizza ambienti umidi terrestri, caccia insetti attivamente. Tornerà all'acqua solo per riprodursi. Il ciclo si ripete: uova → girini → metamorfosi → adulti. Il tempo dal girino all'adulto varia da 8 settimane a 2-3 anni secondo la specie e le condizioni.

---

## S6 — Migrazione verticale del plancton

Ogni giorno, in tutti gli oceani del pianeta, miliardi di piccoli organismi — copepodi, krill, meduse piccole, pesci lanterna — compiono una migrazione verticale. Durante il giorno si rifugiano in profondità (200-1000 metri) dove l'acqua è scura e i predatori visivi non li vedono. Di notte salgono verso la superficie per nutrirsi del fitoplancton che è abbondante nei primi 50 metri. All'alba ridiscendono. Questa migrazione, detta "diel vertical migration", è il più grande movimento di biomassa del pianeta. La discesa mattutina e la salita serale sono sincronizzate dalla luce: l'intensità luminosa scende sotto una soglia di percezione dell'occhio del copepode, innescando il nuoto verso l'alto. Alcune specie aspettano la luna piena e modificano la profondità raggiunta. Altre si fermano a profondità intermedie quando c'è uno strato denso di fitoplancton (deep chlorophyll maximum). La migrazione influisce sulla pompa biologica dell'oceano: i detriti fecali depositati in profondità trasportano carbonio dall'atmosfera al fondale.

---

## S7 — Redazione di un quotidiano cartaceo

Un giornale nazionale ha una sala redazione con 80 giornalisti divisi in desk: politica, cronaca, esteri, economia, cultura, sport. Ogni mattina alle 9, il direttore riunisce i capiredattori: si passano in rassegna le notizie della notte, si decide la "prima pagina", si assegnano i pezzi. Durante la giornata i giornalisti contattano fonti, verificano fatti, scrivono. Ogni pezzo passa per tre livelli di revisione: caporedattore del desk, caposervizio, desk centrale. Nel frattempo la foto-desk cerca immagini e la grafica impagina. Alle 19 c'è la riunione finale: taglio dei pezzi lunghi, decisione della gerarchia di titoli e occhielli. Alle 21 la redazione chiude: il file passa in stampa. I rotativi stampano tra le 23 e le 3 del mattino. Le copie vengono caricate su camion e distribuite alle edicole dalle 5. Le correzioni dell'ultima ora (breaking news, errori gravi) possono richiedere "ribaltate" — una parte della tiratura viene rifatta. L'archivio storico del giornale, digitalizzato, è consultabile dagli abbonati. Le news online seguono un ciclo diverso: pubblicazione continua, aggiornamenti, verifiche meno rigorose, metriche di click che influenzano le promozioni.

---

## S8 — Cooperativa di pescatori di un piccolo porto

Nel porto di un'isola mediterranea operano 22 barche di pescatori, tutte a conduzione familiare. Nel 1962 hanno fondato una cooperativa: pooling della pesca, distribuzione comune ai mercati, acquisto collettivo di reti e carburante a prezzi scontati, gestione condivisa di una cella frigorifera al porto. Ogni mattina alle 4 i pescatori escono (non tutti — a rotazione, e in base al meteo, che un membro anziano valuta). Tornano verso le 10-11 con il pescato. La cooperativa pesa, cataloga per specie e taglia, e prepara i lotti per i mercati del continente (Napoli, Palermo). Una parte del pescato rimane sull'isola per il consumo locale: ristoranti, pescherie, famiglie. I prezzi all'ingrosso variano giornalmente secondo domanda e scorte. I membri ricevono mensilmente la loro quota proporzionalmente al pescato conferito, meno le trattenute per spese comuni. Le decisioni importanti (nuove barche, modifica degli statuti, conflitti tra membri) sono prese in assemblea con un voto per membro. L'ammissione di nuovi pescatori richiede il voto di due terzi. In 60 anni ci sono state 3 espulsioni: tutte per pesca illegale (sottomisura, zone protette).

---

## S9 — Causa di beatificazione nella Chiesa cattolica

Quando una persona cattolica muore in odore di santità, la sua diocesi può avviare una causa di beatificazione. La fase diocesana prevede la raccolta di testimonianze scritte e orali di chi ha conosciuto il candidato: famiglia, amici, confessori, gente comune che afferma di aver ricevuto grazie. Un postulatore (nominato) compila il dossier. Si raccolgono gli scritti del candidato — lettere, diari, omelie — e vengono esaminati da una commissione teologica per escludere eresie. Se la fase diocesana conclude positivamente, il dossier viene inviato a Roma, alla Congregazione delle Cause dei Santi. Qui, una commissione di cardinali e consultori valuta le "virtù eroiche" del candidato. Dopo parere positivo, il Papa firma un decreto che attribuisce il titolo di "Venerabile". Per arrivare alla beatificazione serve un miracolo autenticato — tipicamente una guarigione inspiegabile medicalmente, attestata da una commissione medica e poi teologica. Dopo il primo miracolo: "Beato". Dopo un secondo miracolo (post-beatificazione): "Santo". Il processo può durare decenni o secoli; alcune cause sono archiviate ("sospese") se l'evidenza è insufficiente. Il processo ha regole canoniche codificate (Divinus Perfectionis Magister, 1983).

---

## S10 — Conto corrente bancario

Un cittadino apre un conto corrente presso una banca. Per farlo presenta documento di identità, codice fiscale, referenze lavorative. La banca verifica, assegna un IBAN e una carta. Il cliente deposita stipendi, fa bonifici, paga con carta. Ogni transazione viene registrata: data, importo, controparte, causale, saldo dopo l'operazione. Il saldo può essere positivo (a credito) o negativo se il cliente ha un fido (linea di credito concessa dalla banca). Il fido ha un tasso di interesse: lo scoperto costa. Ogni mese il cliente riceve un estratto conto con tutte le operazioni. Su conto sopra soglia (5000€ di giacenza media annua) matura l'imposta di bollo statale. I bonifici verso IBAN italiani arrivano in giornata (bonifici istantanei in pochi secondi); verso l'estero richiedono più giorni e commissioni. La banca può bloccare transazioni sospette per antiriciclaggio (AML): il cliente viene contattato per chiarire l'origine dei fondi. In caso di decesso del titolare, il conto viene congelato fino alla dichiarazione di successione degli eredi. Il cliente può chiudere il conto in qualsiasi momento; la banca può chiuderlo unilateralmente per inattività (>24 mesi) o violazione dei termini.

---

## Auto-audit sulla selezione

**Diversità di dominio:**
- Software/tech: S1 (Skyscanner), S2 (Patch Tuesday), S3 (Replit) — 3 sistemi
- Biologico: S4 (Glicemia), S5 (Metamorfosi), S6 (Migrazione plancton) — 3 sistemi
- Sociale/istituzionale: S7 (Redazione), S8 (Cooperativa pescatori), S9 (Beatificazione) — 3 sistemi
- Economico-finanziario: S10 (Conto corrente) — 1 sistema

**Sovrapposizione col corpus:** nessuno di questi sistemi appare nei 19 documenti storici o nel trattato. Il più rischioso è S6 (migrazione plancton) — simile concettualmente alle migrazioni uccelli del TOPOLOGY ma con dinamica diversa e non citato.

**Ricchezza prevista:** ogni sistema ha almeno 5 primitive attese. S3 (Replit) e S10 (Conto corrente) sono i più ricchi (probabilmente 12-18 primitive ciascuno). S6 (Plancton) il meno ricco (forse 5-7).
