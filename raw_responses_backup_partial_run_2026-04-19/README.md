# Backup — Partial Run Results from 2026-04-19

Questo folder contiene backup delle risposte da una **esecuzione parziale anomala** avvenuta durante il setup dell'esperimento, prima del fix di `load_dotenv(override=True)` e del fix al parser JSON di Gemini.

## Cosa è successo

Durante il debug della pipeline, un'esecuzione non supervisionata si è avviata producendo:
- **J1_CLAUDE**: 10/10 falliti per errore di autenticazione (la chiave Anthropic non si caricava per override mancante)
- **J2_OPENAI**: 10/10 riusciti — questi file sono il backup qui contenuto
- **J3_GEMINI**: 6/10 falliti per errore di parsing JSON, poi interrotto

## Perché teniamo il backup

Il pre-registration §5 dichiara determinismo: OpenAI con `seed=42` e `temperature=0.0`. Una seconda esecuzione dovrebbe produrre output *quasi identico*. Il confronto tra questo backup e la nuova esecuzione fornisce una **verifica di stabilità intra-modello gratuita** (analisi A.2 della pre-registration, originariamente prevista con GPT ma ora estendibile all'intero panel).

## Valore scientifico

Questi file non entrano nell'analisi principale (che userà la nuova esecuzione completa). Servono per:

1. **Controllo di riproducibilità**: confronto bit-a-bit / primitiva-per-primitiva con la nuova run
2. **Trasparenza**: documentare la cronologia effettiva del setup
3. **Costo risparmiato**: se la nuova run di OpenAI producesse gli stessi output, questo prova che il pre-registration è riproducibile

I file non vengono usati come sostituti della nuova run. Vengono mantenuti come evidenza secondaria.

## Metadati

- Data backup: 2026-04-19 00:49 (locale)
- Versione del codice che li ha prodotti: `run_experiment.py` pre-fix (senza `override=True`, senza fix Gemini)
- Versione del theory-data.json: SHA-256 `98d277369e0213d54f55910ea8157c86dc3a690e3f8cbb81605fa036b8401b5a` (stessa della pre-registration)
- Modello usato: gpt-4o (stesso della nuova run)
- Parametri: temperature=0, seed=42 (stessi della nuova run)
