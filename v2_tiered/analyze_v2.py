"""
Esperimento A' — Analisi tiered.

Metriche:
  1. Fleiss κ sul tier NUCLEAR (binarizzato) — PRIMARIA
  2. Fleiss κ pesato ordinale (ABSENT=0, INFERRED=1, PRESENT=2, NUCLEAR=3) — PRIMARIA
  3. Fleiss κ sul tier PRESENT, INFERRED, "almeno INFERRED" — secondarie
  4. Pairwise Cohen κ per ogni tier
  5. Confusion matrix 4×4 tra coppie di coder
  6. Recovery rate nuclear FR (T1, M2, CO1, N5) come NUCLEAR
  7. Confronto con A (sul binario "almeno INFERRED"): il tiering migliora il κ?
"""
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from statsmodels.stats.inter_rater import fleiss_kappa

SCRIPT_DIR = Path(__file__).parent
PARENT_DIR = SCRIPT_DIR.parent
RAW_DIR = SCRIPT_DIR / "raw_responses_v2"

# Same canonical order as A
PRIMITIVES_ORDER = [
    "C1", "C2", "C3", "C4", "C5",
    "I1", "I2", "I3", "I4",
    "T1", "T2", "T3", "T4",
    "M1", "M2", "M3", "M4",
    "W1", "W2", "W3", "W4",
    "S1", "S2", "S3", "S4",
    "CO1", "CO2", "CO3", "CO4",
    "N1", "N2", "N3", "N4", "N5",
]
PRIMITIVES_SET = set(PRIMITIVES_ORDER)
assert len(PRIMITIVES_ORDER) == 34

NUCLEAR_FR = {"T1", "M2", "CO1", "N5"}

SYSTEMS_ORDER = [f"S{i}" for i in range(1, 11)]
LLMS = ["J1_CLAUDE", "J2_OPENAI", "J3_GEMINI"]

# Tier -> numerical level (ordinal)
TIER_LEVELS = {"ABSENT": 0, "INFERRED": 1, "PRESENT": 2, "NUCLEAR": 3}
TIER_FROM_LEVEL = {v: k for k, v in TIER_LEVELS.items()}
VALID_TIERS = {"NUCLEAR", "PRESENT", "INFERRED"}


def load_tiered_data(llm: str) -> dict:
    """Ritorna {sid: {pid: tier}} dove tier ∈ {NUCLEAR, PRESENT, INFERRED} o assente (non presente)."""
    out = {}
    d = RAW_DIR / llm
    for sid in SYSTEMS_ORDER:
        f = d / f"{sid}.json"
        if not f.exists():
            out[sid] = {}
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("missing"):
            out[sid] = {}
            continue
        prims = data.get("primitives_identified", [])
        # Mappa pid -> tier (solo se valido e pid noto)
        tier_map = {}
        for p in prims:
            pid = p.get("id", "").strip()
            tier = p.get("tier", "").strip().upper()
            if pid in PRIMITIVES_SET and tier in VALID_TIERS:
                tier_map[pid] = tier
        out[sid] = tier_map
    return out


def build_ordinal_matrix(coder_data: dict) -> np.ndarray:
    """Matrice (n_systems × n_primitives) con valori 0/1/2/3."""
    mat = np.zeros((len(SYSTEMS_ORDER), len(PRIMITIVES_ORDER)), dtype=np.int8)
    for i, sid in enumerate(SYSTEMS_ORDER):
        tier_map = coder_data.get(sid, {})
        for j, pid in enumerate(PRIMITIVES_ORDER):
            tier = tier_map.get(pid, "ABSENT")
            mat[i, j] = TIER_LEVELS[tier]
    return mat


def binarize(matrix: np.ndarray, threshold: int) -> np.ndarray:
    """Ritorna 1 se level ≥ threshold, 0 altrimenti.

    threshold=3 → solo NUCLEAR
    threshold=2 → NUCLEAR+PRESENT (almeno chiaramente manifestata)
    threshold=1 → NUCLEAR+PRESENT+INFERRED (qualsiasi identificazione)
    """
    return (matrix >= threshold).astype(np.int8)


def fleiss_k_binary(matrices: dict) -> dict:
    """Fleiss κ su dati binari per 3 coder."""
    llms = list(matrices.keys())
    n_coders = len(llms)
    n_items = matrices[llms[0]].size
    # per ogni item: (n_no, n_yes)
    flat = {l: matrices[l].flatten() for l in llms}
    table = np.zeros((n_items, 2), dtype=int)
    for i in range(n_items):
        yes = int(sum(flat[l][i] for l in llms))
        table[i] = [n_coders - yes, yes]
    kappa = fleiss_kappa(table, method="fleiss")
    return {"kappa": float(kappa), "n_items": int(n_items), "n_coders": n_coders}


def fleiss_k_ordinal_weighted(matrices: dict) -> dict:
    """Fleiss κ pesato ordinale su 4 categorie (0=ABSENT, 1=INFERRED, 2=PRESENT, 3=NUCLEAR).

    Usiamo Krippendorff-style weights (linear). statsmodels non ha direttamente il weighted Fleiss,
    quindi calcoliamo la media dei Cohen κ pairwise pesati (quadratic weights) come approssimazione
    robusta per dati ordinali.
    """
    llms = list(matrices.keys())
    flat = {l: matrices[l].flatten() for l in llms}
    # Per 3 coder: media dei 3 Cohen κ pairwise con weight='quadratic'
    # (standard per misure ordinali)
    pairwise_ks = []
    for a, b in combinations(llms, 2):
        k = cohen_kappa_score(flat[a], flat[b], weights="quadratic",
                              labels=[0, 1, 2, 3])
        pairwise_ks.append(float(k))
    # Con weight='linear' anche
    pairwise_ks_linear = []
    for a, b in combinations(llms, 2):
        k = cohen_kappa_score(flat[a], flat[b], weights="linear",
                              labels=[0, 1, 2, 3])
        pairwise_ks_linear.append(float(k))
    return {
        "kappa_quadratic_mean": float(np.mean(pairwise_ks)),
        "kappa_quadratic_individual": pairwise_ks,
        "kappa_linear_mean": float(np.mean(pairwise_ks_linear)),
        "kappa_linear_individual": pairwise_ks_linear,
        "pair_order": [f"{a}__{b}" for a, b in combinations(llms, 2)],
    }


def pairwise_cohen_binary(matrices: dict) -> dict:
    llms = list(matrices.keys())
    out = {}
    for a, b in combinations(llms, 2):
        va = matrices[a].flatten()
        vb = matrices[b].flatten()
        out[f"{a}__{b}"] = float(cohen_kappa_score(va, vb))
    return out


def confusion_matrices_4x4(ord_matrices: dict) -> dict:
    llms = list(ord_matrices.keys())
    out = {}
    for a, b in combinations(llms, 2):
        va = ord_matrices[a].flatten()
        vb = ord_matrices[b].flatten()
        cm = confusion_matrix(va, vb, labels=[0, 1, 2, 3]).tolist()
        out[f"{a}__{b}"] = {
            "confusion_matrix": cm,
            "labels": ["ABSENT", "INFERRED", "PRESENT", "NUCLEAR"],
        }
    return out


def tier_distribution(ord_matrices: dict) -> dict:
    """Distribuzione dei tier per ogni coder: quante volte NUCLEAR/PRESENT/INFERRED/ASSENT?"""
    llms = list(ord_matrices.keys())
    out = {}
    for llm in llms:
        total = ord_matrices[llm].size
        dist = {}
        for tier_name, level in TIER_LEVELS.items():
            n = int((ord_matrices[llm] == level).sum())
            dist[tier_name] = {"count": n, "fraction": n / total}
        out[llm] = dist
    return out


def nuclear_fr_at_tier(ord_matrices: dict, min_tier: int = 3) -> dict:
    """Per le 4 nucleari FR: quante volte classificate come tier >= min_tier (default NUCLEAR)?"""
    llms = list(ord_matrices.keys())
    result = {}
    for pid in sorted(NUCLEAR_FR):
        j = PRIMITIVES_ORDER.index(pid)
        by_n_coders = [0, 0, 0, 0]
        per_system = []
        for i, sid in enumerate(SYSTEMS_ORDER):
            n_found = sum(1 for l in llms if ord_matrices[l][i, j] >= min_tier)
            by_n_coders[n_found] += 1
            per_system.append({"system": sid, "n_coders_at_tier": int(n_found),
                               "tiers": {l: TIER_FROM_LEVEL.get(int(ord_matrices[l][i, j]), "ABSENT")
                                         for l in llms}})
        result[pid] = {
            "min_tier_required": TIER_FROM_LEVEL[min_tier],
            "by_all_3_coders": by_n_coders[3],
            "by_exactly_2_coders": by_n_coders[2],
            "by_exactly_1_coder": by_n_coders[1],
            "by_0_coders": by_n_coders[0],
            "unanime_rate": by_n_coders[3] / len(SYSTEMS_ORDER),
            "per_system": per_system,
        }
    return result


def per_primitive_tier_agreement(ord_matrices: dict) -> dict:
    """Per ogni primitiva, analisi della distribuzione dei tier."""
    llms = list(ord_matrices.keys())
    result = {}
    for j, pid in enumerate(PRIMITIVES_ORDER):
        # Per ogni sistema, la triade di tier dei 3 coder
        triadi = []
        for i, sid in enumerate(SYSTEMS_ORDER):
            triade = tuple(sorted(int(ord_matrices[l][i, j]) for l in llms))
            triadi.append(triade)
        # Accordo unanime (tutti e 3 hanno stesso tier)
        unanime = sum(1 for t in triadi if t[0] == t[2])
        # Distribuzione degli stati per questa primitiva
        max_tier_per_system = [max(int(ord_matrices[l][i, j]) for l in llms)
                              for i in range(len(SYSTEMS_ORDER))]
        min_tier_per_system = [min(int(ord_matrices[l][i, j]) for l in llms)
                              for i in range(len(SYSTEMS_ORDER))]
        # Spread medio (max - min su 4 livelli)
        spread = sum(ma - mi for ma, mi in zip(max_tier_per_system, min_tier_per_system)) / len(SYSTEMS_ORDER)
        result[pid] = {
            "unanime_across_systems": unanime,
            "avg_spread_tiers": float(spread),
        }
    return result


def apply_decision_table(k_nuclear: float, k_ordinal: float) -> dict:
    """Tabella decisionale §7 della pre-registration."""
    T_N_H1 = 0.60
    T_O_H1 = 0.50
    T_N_H0 = 0.40
    T_O_H0 = 0.30

    if k_nuclear >= T_N_H1 and k_ordinal >= T_O_H1:
        return {"verdict": "H1_CONFIRMED", "interpretation":
                "Le primitive essenziali sono oggettivamente riconoscibili e il gradiente di essenzialita' e' condiviso."}
    if k_nuclear >= T_N_H1 and k_ordinal < T_O_H1:
        return {"verdict": "H1_CONFIRMED_PARTIAL", "interpretation":
                "Le primitive essenziali sono riconoscibili ma il gradiente sotto-NUCLEAR e' ambiguo."}
    if k_nuclear < T_N_H1 and k_ordinal >= T_O_H1:
        return {"verdict": "H1_CONFIRMED_ORDINAL_ONLY", "interpretation":
                "C'e' accordo sul gradiente ma non sulle soglie specifiche."}
    if k_nuclear <= T_N_H0 and k_ordinal <= T_O_H0:
        return {"verdict": "H0_CONFIRMED", "interpretation":
                "Nessun tier produce accordo. Il problema non e' di prompt, e' di definizione."}
    return {"verdict": "GRAY_ZONE", "interpretation":
            "Supporto parziale, ne' conferma ne' falsificazione."}


def compare_with_experiment_A() -> dict:
    """Confronto diretto A vs A' sul binario 'almeno INFERRED'.

    L'A misurava presenza binaria con κ = 0.124.
    L'A' sul binario 'almeno INFERRED' (cioè qualsiasi identificazione) dovrebbe essere confrontabile.
    Se κ(A'_almeno_INFERRED) > κ(A), il tiering ha ridotto il rumore di soglia.
    """
    # Carica i dati dell'A (raw_responses/ nella parent dir)
    a_raw_dir = PARENT_DIR / "raw_responses"
    if not a_raw_dir.exists():
        return {"error": "Esperimento A non trovato"}
    a_matrices = {}
    for llm in LLMS:
        coder = {}
        for sid in SYSTEMS_ORDER:
            f = a_raw_dir / llm / f"{sid}.json"
            if not f.exists():
                coder[sid] = set()
                continue
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("missing"):
                coder[sid] = set()
                continue
            ids = data.get("primitive_ids", [])
            coder[sid] = {i for i in ids if i in PRIMITIVES_SET}
        # Build binary matrix
        mat = np.zeros((len(SYSTEMS_ORDER), len(PRIMITIVES_ORDER)), dtype=np.int8)
        for i, sid in enumerate(SYSTEMS_ORDER):
            for j, pid in enumerate(PRIMITIVES_ORDER):
                mat[i, j] = 1 if pid in coder[sid] else 0
        a_matrices[llm] = mat
    a_fleiss = fleiss_k_binary(a_matrices)
    return {"experiment_A_fleiss_kappa_binary": float(a_fleiss["kappa"])}


def main():
    # Carica dati v2 (tiered)
    coder_data = {llm: load_tiered_data(llm) for llm in LLMS}
    ord_matrices = {llm: build_ordinal_matrix(coder_data[llm]) for llm in LLMS}

    # Controllo sanita': almeno un LLM ha dati?
    for llm in LLMS:
        n_nonzero = int((ord_matrices[llm] > 0).sum())
        if n_nonzero == 0:
            print(f"WARNING: {llm} ha 0 primitive identificate in tutti i 10 sistemi")

    # Coding matrix CSV
    rows = []
    for llm in LLMS:
        for i, sid in enumerate(SYSTEMS_ORDER):
            for j, pid in enumerate(PRIMITIVES_ORDER):
                level = int(ord_matrices[llm][i, j])
                tier = TIER_FROM_LEVEL[level]
                rows.append({
                    "coder": llm, "system": sid, "primitive": pid,
                    "tier": tier, "level": level,
                })
    df = pd.DataFrame(rows)
    df.to_csv(SCRIPT_DIR / "coding_matrix_v2.csv", index=False)
    print(f"Salvato coding_matrix_v2.csv ({len(df)} righe)")

    # Matrici binarizzate per ciascun threshold
    bin_nuclear = {llm: binarize(ord_matrices[llm], 3) for llm in LLMS}
    bin_present_or_nuclear = {llm: binarize(ord_matrices[llm], 2) for llm in LLMS}
    bin_any = {llm: binarize(ord_matrices[llm], 1) for llm in LLMS}

    # Step 1 — Fleiss κ sul NUCLEAR
    print("\n--- Fleiss κ PRIMARIO 1: solo NUCLEAR ---")
    fk_nuclear = fleiss_k_binary(bin_nuclear)
    print(f"κ(NUCLEAR): {fk_nuclear['kappa']:.4f}")

    # Step 2 — Fleiss κ ordinale pesato
    print("\n--- Fleiss κ PRIMARIO 2: ordinale pesato ---")
    fk_ordinal = fleiss_k_ordinal_weighted(ord_matrices)
    print(f"κ ordinale pesato (quadratic, media pairwise): {fk_ordinal['kappa_quadratic_mean']:.4f}")
    print(f"κ ordinale pesato (linear, media pairwise): {fk_ordinal['kappa_linear_mean']:.4f}")

    # Decision table
    decision = apply_decision_table(fk_nuclear["kappa"], fk_ordinal["kappa_quadratic_mean"])
    print(f"\nVERDETTO: {decision['verdict']}")
    print(f"INTERPRETAZIONE: {decision['interpretation']}")

    # Step 3 — Altre fleiss κ binarizzate
    print("\n--- Fleiss κ secondarie ---")
    fk_present_or_nuclear = fleiss_k_binary(bin_present_or_nuclear)
    fk_any = fleiss_k_binary(bin_any)
    print(f"κ(PRESENT+NUCLEAR): {fk_present_or_nuclear['kappa']:.4f}")
    print(f"κ(almeno INFERRED = qualsiasi identificazione): {fk_any['kappa']:.4f}")

    # Step 4 — Pairwise Cohen κ
    print("\n--- Pairwise Cohen κ per tier ---")
    pw_nuclear = pairwise_cohen_binary(bin_nuclear)
    pw_present_or_nuclear = pairwise_cohen_binary(bin_present_or_nuclear)
    pw_any = pairwise_cohen_binary(bin_any)
    for pair in pw_nuclear:
        print(f"  {pair}:")
        print(f"    NUCLEAR: {pw_nuclear[pair]:.4f}")
        print(f"    PRESENT+NUCLEAR: {pw_present_or_nuclear[pair]:.4f}")
        print(f"    almeno INFERRED: {pw_any[pair]:.4f}")

    # Step 5 — Tier distribution
    print("\n--- Distribuzione tier per coder ---")
    tier_dist = tier_distribution(ord_matrices)
    for llm, dist in tier_dist.items():
        print(f"  {llm}:")
        for tier in ["NUCLEAR", "PRESENT", "INFERRED", "ABSENT"]:
            d = dist[tier]
            print(f"    {tier:<10}: {d['count']:>4} ({d['fraction']:.1%})")

    # Step 6 — Nuclear FR at tier NUCLEAR
    print("\n--- Recovery 4 nucleari FR come NUCLEAR ---")
    nfr_nuclear = nuclear_fr_at_tier(ord_matrices, min_tier=3)
    for pid, data in nfr_nuclear.items():
        print(f"  {pid}: 3/3 in {data['by_all_3_coders']}/10, "
              f"2/3 in {data['by_exactly_2_coders']}/10, "
              f"1/3 in {data['by_exactly_1_coder']}/10, "
              f"0/3 in {data['by_0_coders']}/10")

    # Nuclear FR at tier PRESENT or higher (più permissivo)
    print("\n--- Recovery 4 nucleari FR come almeno PRESENT ---")
    nfr_present = nuclear_fr_at_tier(ord_matrices, min_tier=2)
    for pid, data in nfr_present.items():
        print(f"  {pid}: 3/3 in {data['by_all_3_coders']}/10")

    # Step 7 — Confusion matrices 4x4
    cm = confusion_matrices_4x4(ord_matrices)

    # Step 8 — Per-primitive tier agreement
    per_prim = per_primitive_tier_agreement(ord_matrices)

    # Step 9 — Comparison with A
    print("\n--- Confronto con Esperimento A (binario semplice) ---")
    comp_a = compare_with_experiment_A()
    a_kappa = comp_a.get("experiment_A_fleiss_kappa_binary")
    print(f"κ A (binario 'presente'): {a_kappa:.4f}")
    print(f"κ A' (binario 'almeno INFERRED'): {fk_any['kappa']:.4f}")
    if a_kappa is not None:
        delta = fk_any["kappa"] - a_kappa
        print(f"Delta A' - A: {delta:+.4f} ({'MIGLIORAMENTO' if delta > 0 else 'PEGGIORAMENTO' if delta < 0 else 'INVARIATO'})")

    # Save results
    results = {
        "metadata": {
            "experiment": "Esperimento A' — Inter-Rater Reliability Tiered",
            "llms": {
                "J1_CLAUDE": "claude-sonnet-4-6",
                "J2_OPENAI": "gpt-4o",
                "J3_GEMINI": "gemini-2.5-pro",
            },
            "n_systems": len(SYSTEMS_ORDER),
            "n_primitives": len(PRIMITIVES_ORDER),
            "n_coders": len(LLMS),
            "tier_levels": TIER_LEVELS,
        },
        "primary_metrics": {
            "fleiss_kappa_NUCLEAR": fk_nuclear,
            "fleiss_kappa_ordinal_weighted": fk_ordinal,
        },
        "decision": decision,
        "secondary_fleiss_kappa": {
            "PRESENT_or_NUCLEAR": fk_present_or_nuclear,
            "any_identification": fk_any,
        },
        "pairwise_cohen_kappa": {
            "NUCLEAR": pw_nuclear,
            "PRESENT_or_NUCLEAR": pw_present_or_nuclear,
            "any_identification": pw_any,
        },
        "tier_distribution": tier_dist,
        "nuclear_fr_recovery_NUCLEAR": nfr_nuclear,
        "nuclear_fr_recovery_PRESENT": nfr_present,
        "confusion_matrices_4x4": cm,
        "per_primitive_tier_agreement": per_prim,
        "comparison_with_A": {
            "A_fleiss_kappa_binary": a_kappa,
            "A_prime_fleiss_kappa_any_identification": float(fk_any["kappa"]),
            "delta": (float(fk_any["kappa"]) - a_kappa) if a_kappa is not None else None,
        },
    }
    with open(SCRIPT_DIR / "results_v2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSalvato results_v2.json")


if __name__ == "__main__":
    main()
