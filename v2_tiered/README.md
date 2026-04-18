# Esperimento A' — Inter-Rater Reliability Tiered

**Follow-up diretto dell'Esperimento A** (H0 confermato, Fleiss κ = 0.124) con prompt modificato per classificare ogni primitiva in tre tier di essenzialità.

## Ipotesi chiave

Se le primitive della TSRI sono oggettive, il tier **NUCLEAR** (primitive essenziali per l'identità del sistema) deve avere accordo alto tra LLM indipendenti, anche se l'accordo totale (tutte le primitive) resta basso.

## Tre tier

- **NUCLEAR**: test di rimozione positivo — senza la primitiva, il sistema non è più quel sistema
- **PRESENT**: chiaramente manifestata, non essenziale
- **INFERRED**: debolmente manifestata, può essere omessa

## Soglie decisionali

| κ(NUCLEAR) | κ ordinale | Verdetto |
|---|---|---|
| ≥ 0.60 | ≥ 0.50 | H1 confermata |
| 0.40-0.60 | 0.30-0.50 | Zona grigia |
| ≤ 0.40 | ≤ 0.30 | H0 confermata |

## Relazione con A

- Stessi 10 sistemi (`../TEST_SYSTEMS.md`)
- Stessi 3 LLM (Claude Sonnet 4.6, GPT-4o, Gemini 2.5 Pro)
- Stessi parametri (temp=0, seed=42, max_tokens=8000)
- **Unica variabile cambiata**: il prompt utente
