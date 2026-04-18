"""
Esperimento A — Analisi dei risultati.

Input:
  raw_responses/{J1_CLAUDE, J2_OPENAI, J3_GEMINI}/S*.json
  raw_responses_backup_partial_run_2026-04-19/J2_OPENAI/S*.json (backup)

Output:
  coding_matrix.csv — matrice sistemi × primitive × coder
  results.json — tutte le metriche
  REPORT.md — interpretazione

Pre-registered metrics:
  - Fleiss κ (3 coder × 340 decisioni)
  - Pairwise Cohen κ (3 coppie)
  - Agreement per primitiva
  - Agreement per sistema
  - Recovery rate nuclear FR (T1, M2, CO1, N5)

Bonus analyses:
  - Fleiss κ senza Claude (J2+J3 only)
  - Confronto OpenAI backup vs nuovo run (stabilità intra-modello)
"""
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "raw_responses"
BACKUP_DIR = SCRIPT_DIR / "raw_responses_backup_partial_run_2026-04-19" / "J2_OPENAI"

# Canonical order of the 34 primitives (from theory-data.json, by structure then by ID)
PRIMITIVES_ORDER = [
    # CONTENT (5)
    "C1", "C2", "C3", "C4", "C5",
    # INVENTORY (4)
    "I1", "I2", "I3", "I4",
    # TRANSACTIONS (4)
    "T1", "T2", "T3", "T4",
    # MEMBERSHIP (4)
    "M1", "M2", "M3", "M4",
    # WORKFLOW (4)
    "W1", "W2", "W3", "W4",
    # SCHEDULING (4)
    "S1", "S2", "S3", "S4",
    # COMMUNICATION (4)
    "CO1", "CO2", "CO3", "CO4",
    # TELEMETRY (5)
    "N1", "N2", "N3", "N4", "N5",
]
PRIMITIVES_SET = set(PRIMITIVES_ORDER)
assert len(PRIMITIVES_ORDER) == 34

# Nuclear FR primitives (dichiarate nel trattato)
NUCLEAR_FR = {"T1", "M2", "CO1", "N5"}

# Universal connectors (non usati come positivi nell'Esperimento B, ma identificabili qui)
UNIVERSAL_CONNECTORS = {"W1", "W3", "CO2", "N3"}

SYSTEMS_ORDER = [f"S{i}" for i in range(1, 11)]
LLMS = ["J1_CLAUDE", "J2_OPENAI", "J3_GEMINI"]


def load_coder_data(base_dir: Path, llm: str) -> dict:
    """Carica le 10 risposte di un coder. Ritorna {sid: set(primitive_ids)}."""
    out = {}
    d = base_dir / llm if llm else base_dir
    for sid in SYSTEMS_ORDER:
        f = d / f"{sid}.json"
        if not f.exists():
            out[sid] = set()
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("missing"):
            out[sid] = set()
            continue
        # Estrai gli ID, filtra solo quelli validi (alcuni LLM possono inventarli)
        raw_ids = data.get("primitive_ids", [])
        valid_ids = {i for i in raw_ids if i in PRIMITIVES_SET}
        out[sid] = valid_ids
    return out


def build_binary_matrix(coder_data: dict) -> np.ndarray:
    """Costruisce matrice (n_systems × n_primitives) binaria per un singolo coder."""
    mat = np.zeros((len(SYSTEMS_ORDER), len(PRIMITIVES_ORDER)), dtype=np.int8)
    for i, sid in enumerate(SYSTEMS_ORDER):
        ids = coder_data.get(sid, set())
        for j, pid in enumerate(PRIMITIVES_ORDER):
            mat[i, j] = 1 if pid in ids else 0
    return mat


def compute_fleiss(matrices: dict) -> dict:
    """Fleiss κ su 3 coder. Richiede matrice (n_items × n_categories)
    dove ogni cella conta quanti coder hanno scelto quella categoria per quell'item.

    Per dati binari: per ogni (sistema, primitiva) conto quanti coder hanno messo 1 e quanti 0.
    """
    llms = list(matrices.keys())
    n_coders = len(llms)
    n_systems = len(SYSTEMS_ORDER)
    n_prims = len(PRIMITIVES_ORDER)

    # Costruisco la matrice in formato fleiss_kappa: per ogni item binario,
    # (n_no, n_yes). Un "item" qui è una coppia (sistema, primitiva).
    n_items = n_systems * n_prims
    table = np.zeros((n_items, 2), dtype=int)
    for idx, (i, j) in enumerate(((i, j) for i in range(n_systems) for j in range(n_prims))):
        yes = sum(matrices[l][i, j] for l in llms)
        no = n_coders - yes
        table[idx] = [no, yes]
    # fleiss_kappa method='fleiss' (default)
    kappa = fleiss_kappa(table, method="fleiss")
    return {"kappa": float(kappa), "n_items": int(n_items), "n_coders": n_coders}


def compute_pairwise_cohen(matrices: dict) -> dict:
    """Cohen κ pairwise su 3 coppie di coder. Calcolo sulla matrice flat."""
    llms = list(matrices.keys())
    pairs = {}
    for a, b in combinations(llms, 2):
        va = matrices[a].flatten()
        vb = matrices[b].flatten()
        k = cohen_kappa_score(va, vb)
        pairs[f"{a}__{b}"] = float(k)
    return pairs


def per_primitive_agreement(matrices: dict) -> dict:
    """Per ogni primitiva, calcola l'accordo medio tra i 3 coder sui 10 sistemi."""
    llms = list(matrices.keys())
    result = {}
    for j, pid in enumerate(PRIMITIVES_ORDER):
        # vettore di 10 decisioni per coder
        vectors = {llm: matrices[llm][:, j] for llm in llms}
        # unanime positive = tutti 3 dicono sì
        unanime_yes = int(sum(
            1 for i in range(len(SYSTEMS_ORDER))
            if all(vectors[l][i] == 1 for l in llms)
        ))
        # unanime negative = tutti 3 dicono no
        unanime_no = int(sum(
            1 for i in range(len(SYSTEMS_ORDER))
            if all(vectors[l][i] == 0 for l in llms)
        ))
        # any disagreement
        mixed = len(SYSTEMS_ORDER) - unanime_yes - unanime_no
        # presence count per coder
        presence = {llm: int(matrices[llm][:, j].sum()) for llm in llms}
        # pairwise kappa su questa primitiva
        pw = {}
        for a, b in combinations(llms, 2):
            va = matrices[a][:, j]
            vb = matrices[b][:, j]
            # Se nessuno dice mai sì (o sempre sì), kappa è NaN. Gestisco.
            if len(set(va) | set(vb)) < 2:
                pw[f"{a}__{b}"] = None
            else:
                try:
                    pw[f"{a}__{b}"] = float(cohen_kappa_score(va, vb))
                except Exception:
                    pw[f"{a}__{b}"] = None
        result[pid] = {
            "unanime_yes": unanime_yes,
            "unanime_no": unanime_no,
            "mixed": mixed,
            "agreement_rate": (unanime_yes + unanime_no) / len(SYSTEMS_ORDER),
            "presence_by_coder": presence,
            "pairwise_kappa": pw,
        }
    return result


def per_system_agreement(matrices: dict) -> dict:
    """Per ogni sistema, calcola quante primitive hanno accordo unanime / maggioranza / disaccordo."""
    llms = list(matrices.keys())
    result = {}
    for i, sid in enumerate(SYSTEMS_ORDER):
        unanime_yes = int(sum(
            1 for j in range(len(PRIMITIVES_ORDER))
            if all(matrices[l][i, j] == 1 for l in llms)
        ))
        unanime_no = int(sum(
            1 for j in range(len(PRIMITIVES_ORDER))
            if all(matrices[l][i, j] == 0 for l in llms)
        ))
        mixed = len(PRIMITIVES_ORDER) - unanime_yes - unanime_no
        counts_per_coder = {llm: int(matrices[llm][i, :].sum()) for llm in llms}
        result[sid] = {
            "unanime_yes": unanime_yes,
            "unanime_no": unanime_no,
            "mixed": mixed,
            "agreement_rate_over_present": (
                unanime_yes / (len(PRIMITIVES_ORDER) - unanime_no)
                if (len(PRIMITIVES_ORDER) - unanime_no) > 0 else 0.0
            ),
            "primitives_identified_per_coder": counts_per_coder,
        }
    return result


def nuclear_fr_recovery(matrices: dict) -> dict:
    """Quante volte ciascuna primitiva nuclear FR è stata identificata, e da quanti coder."""
    llms = list(matrices.keys())
    result = {}
    for pid in sorted(NUCLEAR_FR):
        j = PRIMITIVES_ORDER.index(pid)
        # Per ogni sistema, quanti coder la identificano
        found_by_n_coders = [0, 0, 0, 0]  # posizione 0..3
        identifications = []
        for i, sid in enumerate(SYSTEMS_ORDER):
            n_found = sum(matrices[l][i, j] for l in llms)
            found_by_n_coders[n_found] += 1
            identifications.append({"system": sid, "n_coders_found": int(n_found)})
        result[pid] = {
            "by_all_3_coders": found_by_n_coders[3],
            "by_exactly_2_coders": found_by_n_coders[2],
            "by_exactly_1_coder": found_by_n_coders[1],
            "by_0_coders": found_by_n_coders[0],
            "unanime_identification_rate": found_by_n_coders[3] / len(SYSTEMS_ORDER),
            "per_system": identifications,
        }
    return result


def openai_stability_check(current_matrix: np.ndarray, backup_matrix: np.ndarray) -> dict:
    """Confronto tra OpenAI backup (primo run) e nuovo run.
    Stesso modello, stesso seed, stesse impostazioni.
    """
    # Differenze cella per cella
    diff = current_matrix != backup_matrix
    n_diff = int(diff.sum())
    total_cells = current_matrix.size
    agreement = 1.0 - (n_diff / total_cells)
    # Differenze per sistema
    per_system = {}
    for i, sid in enumerate(SYSTEMS_ORDER):
        n_current = int(current_matrix[i].sum())
        n_backup = int(backup_matrix[i].sum())
        added = [
            PRIMITIVES_ORDER[j] for j in range(len(PRIMITIVES_ORDER))
            if current_matrix[i, j] == 1 and backup_matrix[i, j] == 0
        ]
        removed = [
            PRIMITIVES_ORDER[j] for j in range(len(PRIMITIVES_ORDER))
            if current_matrix[i, j] == 0 and backup_matrix[i, j] == 1
        ]
        per_system[sid] = {
            "n_current": n_current,
            "n_backup": n_backup,
            "added_in_new_run": added,
            "removed_in_new_run": removed,
        }
    # Cohen kappa tra i due run come misura di stabilità
    kappa = cohen_kappa_score(current_matrix.flatten(), backup_matrix.flatten())
    return {
        "total_cells_differing": n_diff,
        "total_cells": total_cells,
        "bitwise_agreement_rate": float(agreement),
        "cohen_kappa_intra_model": float(kappa),
        "per_system_diff": per_system,
    }


def apply_decision_table(fleiss_k: float) -> dict:
    """Applica la tabella decisionale §7 della pre-registration."""
    if fleiss_k >= 0.70:
        verdict = "H1_CONFIRMED"
        interpretation = (
            "Primitive oggettivamente riconoscibili da LLM indipendenti. "
            "Supporto preliminare alla tesi di ontologia della teoria."
        )
    elif fleiss_k <= 0.40:
        verdict = "H0_CONFIRMED"
        interpretation = (
            "Primitive NON oggettivamente riconoscibili. Tre LLM diversi non convergono. "
            "Il vocabolario è idiosincratico o mal definito. Il corpus empirico dei "
            "'30 casi per primitiva' è da rivedere."
        )
    elif 0.60 < fleiss_k < 0.70:
        verdict = "SUBSTANTIAL_WEAK"
        interpretation = (
            "Supporto preliminare debole. Non raggiunge la soglia pre-registrata per H1 "
            "ma resta una concordanza sostanziale."
        )
    else:
        verdict = "MODERATE"
        interpretation = (
            "Categorie utili ma con variazione sistematica. La teoria è parzialmente "
            "oggettiva ma richiede raffinamento. Nessun verdetto netto."
        )
    return {"fleiss_kappa": fleiss_k, "verdict": verdict, "interpretation": interpretation}


def main():
    # === Step 1: carica dati dei 3 coder ===
    coder_data = {llm: load_coder_data(RAW_DIR, llm) for llm in LLMS}
    matrices = {llm: build_binary_matrix(coder_data[llm]) for llm in LLMS}

    # === Step 2: costruisci coding_matrix.csv ===
    rows = []
    for llm in LLMS:
        for i, sid in enumerate(SYSTEMS_ORDER):
            for j, pid in enumerate(PRIMITIVES_ORDER):
                rows.append({
                    "coder": llm,
                    "system": sid,
                    "primitive": pid,
                    "present": int(matrices[llm][i, j]),
                })
    df = pd.DataFrame(rows)
    df.to_csv(SCRIPT_DIR / "coding_matrix.csv", index=False)
    print(f"Salvato coding_matrix.csv ({len(df)} righe)")

    # === Step 3: Fleiss κ globale ===
    print("\n--- Fleiss κ (3 coder) ---")
    fleiss = compute_fleiss(matrices)
    print(f"Fleiss κ: {fleiss['kappa']:.4f} (n_items={fleiss['n_items']}, n_coders={fleiss['n_coders']})")
    decision = apply_decision_table(fleiss["kappa"])
    print(f"VERDETTO: {decision['verdict']}")
    print(f"INTERPRETAZIONE: {decision['interpretation']}")

    # === Step 4: Fleiss κ senza Claude (J2 + J3) ===
    matrices_no_claude = {k: v for k, v in matrices.items() if k != "J1_CLAUDE"}
    # Fleiss κ con 2 soli coder = Cohen κ
    # Calcoliamo entrambe le metriche: Fleiss (che tecnicamente funziona anche con 2 coder)
    # e Cohen (più standard per 2)
    fleiss_no_claude = compute_fleiss(matrices_no_claude)
    # Cohen κ J2↔J3
    va = matrices["J2_OPENAI"].flatten()
    vb = matrices["J3_GEMINI"].flatten()
    cohen_no_claude = float(cohen_kappa_score(va, vb))
    print(f"\n--- Senza Claude (J2 + J3) ---")
    print(f"Fleiss κ (2 coder, equivalente a Cohen): {fleiss_no_claude['kappa']:.4f}")
    print(f"Cohen κ (OpenAI ↔ Gemini): {cohen_no_claude:.4f}")

    # === Step 5: Pairwise Cohen κ ===
    print("\n--- Pairwise Cohen κ ---")
    pairwise = compute_pairwise_cohen(matrices)
    for pair, k in pairwise.items():
        print(f"  {pair}: {k:.4f}")

    # === Step 6: per-primitive ===
    per_prim = per_primitive_agreement(matrices)
    print("\n--- Primitive con massimo accordo (unanime ≥ 7/10 sistemi) ---")
    high_agreement = [
        (pid, data) for pid, data in per_prim.items()
        if (data["unanime_yes"] + data["unanime_no"]) >= 7
    ]
    high_agreement.sort(key=lambda x: -(x[1]["unanime_yes"] + x[1]["unanime_no"]))
    for pid, data in high_agreement[:10]:
        unan = data["unanime_yes"] + data["unanime_no"]
        print(f"  {pid}: unanime {unan}/10 (yes={data['unanime_yes']}, no={data['unanime_no']}), presence {data['presence_by_coder']}")
    print("\n--- Primitive più problematiche (unanime ≤ 3/10) ---")
    low_agreement = [
        (pid, data) for pid, data in per_prim.items()
        if (data["unanime_yes"] + data["unanime_no"]) <= 3
    ]
    low_agreement.sort(key=lambda x: (x[1]["unanime_yes"] + x[1]["unanime_no"]))
    for pid, data in low_agreement[:15]:
        unan = data["unanime_yes"] + data["unanime_no"]
        print(f"  {pid}: unanime {unan}/10, mixed {data['mixed']}, presence {data['presence_by_coder']}")

    # === Step 7: per-system ===
    per_sys = per_system_agreement(matrices)
    print("\n--- Per sistema: primitive identificate e accordo ---")
    for sid in SYSTEMS_ORDER:
        d = per_sys[sid]
        print(f"  {sid}: counts={d['primitives_identified_per_coder']}, unanime_yes={d['unanime_yes']}, mixed={d['mixed']}")

    # === Step 8: nuclear FR recovery ===
    nfr = nuclear_fr_recovery(matrices)
    print("\n--- Recovery delle 4 primitive nucleari FR ---")
    for pid, data in nfr.items():
        print(
            f"  {pid}: 3/3 in {data['by_all_3_coders']}/10, "
            f"2/3 in {data['by_exactly_2_coders']}/10, "
            f"1/3 in {data['by_exactly_1_coder']}/10, "
            f"0/3 in {data['by_0_coders']}/10"
        )

    # === Step 9: OpenAI stability check ===
    stability = None
    if BACKUP_DIR.exists():
        backup_data = load_coder_data(BACKUP_DIR.parent, "J2_OPENAI")
        backup_matrix = build_binary_matrix(backup_data)
        stability = openai_stability_check(matrices["J2_OPENAI"], backup_matrix)
        print(f"\n--- OpenAI stability check (backup vs new run) ---")
        print(f"  Agreement bitwise: {stability['bitwise_agreement_rate']:.4f}")
        print(f"  Cohen κ intra-modello: {stability['cohen_kappa_intra_model']:.4f}")
        print(f"  Celle diverse: {stability['total_cells_differing']}/{stability['total_cells']}")

    # === Step 10: summary stats ===
    summary_stats = {
        "primitives_per_system": {
            llm: {
                "mean": float(np.mean(matrices[llm].sum(axis=1))),
                "std": float(np.std(matrices[llm].sum(axis=1))),
                "min": int(matrices[llm].sum(axis=1).min()),
                "max": int(matrices[llm].sum(axis=1).max()),
                "totals_per_system": [int(n) for n in matrices[llm].sum(axis=1)],
            }
            for llm in LLMS
        }
    }

    # === Save results.json ===
    results = {
        "metadata": {
            "experiment": "Esperimento A — Inter-Rater Reliability tra LLM indipendenti",
            "llms": {
                "J1_CLAUDE": "claude-sonnet-4-6 (DEVIAZIONE da pre-registrato Claude Opus 4.7 — vedi REPORT.md)",
                "J2_OPENAI": "gpt-4o",
                "J3_GEMINI": "gemini-2.5-pro",
            },
            "n_systems": len(SYSTEMS_ORDER),
            "n_primitives": len(PRIMITIVES_ORDER),
            "n_coders": len(LLMS),
            "n_decisions": len(LLMS) * len(SYSTEMS_ORDER) * len(PRIMITIVES_ORDER),
        },
        "summary_stats": summary_stats,
        "fleiss_kappa_all_3": fleiss,
        "fleiss_kappa_without_claude": fleiss_no_claude,
        "cohen_kappa_openai_gemini": cohen_no_claude,
        "pairwise_cohen_kappa": pairwise,
        "decision": decision,
        "per_primitive": per_prim,
        "per_system": per_sys,
        "nuclear_fr_recovery": nfr,
        "openai_stability_check": stability,
    }
    with open(SCRIPT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSalvato results.json")


if __name__ == "__main__":
    main()
