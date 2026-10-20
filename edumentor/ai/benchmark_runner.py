"""
Academic Benchmark Runner & Engine Validator (Phase 39).
Evaluates the academic benchmark dataset against human expert judgment,
computing:
- Semantic score (Sentence-Transformers / TF-IDF Vector Cosine)
- LLM score (Rubric-based LLM-as-a-Judge)
- Hybrid score (Calibrated weighted composite)

Calculates correlation (Pearson r, Spearman rho), error rates (MAE, RMSE),
and verdict alignment against human evaluations across 5 CS domains.
"""

import math
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

from edumentor.data.academic_dataset import get_academic_dataset, ACADEMIC_BENCHMARK_DATASET
from edumentor.evaluation import evaluate_recall


def _compute_pearson_r(x: List[float], y: List[float]) -> float:
    """Compute Pearson correlation coefficient r between two vectors."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    arr_x = np.array(x, dtype=np.float64)
    arr_y = np.array(y, dtype=np.float64)
    std_x = np.std(arr_x)
    std_y = np.std(arr_y)
    if std_x == 0.0 or std_y == 0.0:
        return 0.0
    return float(np.corrcoef(arr_x, arr_y)[0, 1])


def _compute_spearman_rho(x: List[float], y: List[float]) -> float:
    """Compute Spearman rank correlation coefficient rho between two vectors."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    # Rank transformation with average ranks for ties
    def rankdata(a: np.ndarray) -> np.ndarray:
        sorter = np.argsort(a)
        inv = np.empty_like(sorter)
        inv[sorter] = np.arange(len(a))
        return inv.astype(np.float64)

    rx = rankdata(np.array(x, dtype=np.float64))
    ry = rankdata(np.array(y, dtype=np.float64))
    return _compute_pearson_r(rx.tolist(), ry.tolist())


def _compute_mae(predictions: List[float], targets: List[float]) -> float:
    """Mean Absolute Error."""
    if not predictions:
        return 0.0
    return float(np.mean(np.abs(np.array(predictions) - np.array(targets))))


def _compute_rmse(predictions: List[float], targets: List[float]) -> float:
    """Root Mean Squared Error."""
    if not predictions:
        return 0.0
    return float(np.sqrt(np.mean((np.array(predictions) - np.array(targets)) ** 2)))


def evaluate_dataset_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single dataset entry through EduMentor's evaluation engine,
    populating semantic_score, llm_score, hybrid_score, and system_verdict.
    """
    concept_payload = {
        "id": entry.get("concept_id", "concept_benchmark"),
        "title": entry.get("concept", "Benchmark Concept"),
        "canonical_explanation": entry.get("reference_explanation", ""),
        "key_points": entry.get("key_points", [])
    }

    result = evaluate_recall(concept_payload, entry.get("student_answer", ""))

    semantic_score = float(result.get("semantic_score", 0.0))
    llm_score = float(result.get("llm_score", 0.0))
    hybrid_score = float(result.get("composite_score", result.get("score", 0.0)))
    system_verdict = str(result.get("verdict", "wrong")).lower().replace(" ", "_")

    entry_copy = dict(entry)
    entry_copy["semantic_score"] = round(semantic_score, 1)
    entry_copy["llm_score"] = round(llm_score, 1)
    entry_copy["hybrid_score"] = round(hybrid_score, 1)
    entry_copy["system_verdict"] = system_verdict
    entry_copy["engine_details"] = {
        "quality_q": result.get("quality_q", 0),
        "correctness": result.get("correctness", 0),
        "completeness": result.get("completeness", 0),
        "missing_points": result.get("missing_points", []),
        "misconceptions": result.get("misconceptions", [])
    }
    return entry_copy


def run_benchmark(dataset: Optional[List[Dict[str, Any]]] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Execute full evaluation engine on all dataset entries,
    and compute statistical alignment metrics against human evaluations.
    """
    if dataset is None:
        dataset = get_academic_dataset()

    evaluated_entries = []
    for item in dataset:
        evaluated = evaluate_dataset_entry(item)
        evaluated_entries.append(evaluated)

    human_scores = [float(e["human_evaluation"]["score"]) for e in evaluated_entries]
    human_verdicts = [str(e["human_evaluation"]["verdict"]).lower().replace(" ", "_") for e in evaluated_entries]

    semantic_scores = [float(e["semantic_score"]) for e in evaluated_entries]
    llm_scores = [float(e["llm_score"]) for e in evaluated_entries]
    hybrid_scores = [float(e["hybrid_score"]) for e in evaluated_entries]
    system_verdicts = [str(e["system_verdict"]).lower().replace(" ", "_") for e in evaluated_entries]

    # Overall statistical correlations
    pearson_hybrid = _compute_pearson_r(hybrid_scores, human_scores)
    pearson_semantic = _compute_pearson_r(semantic_scores, human_scores)
    pearson_llm = _compute_pearson_r(llm_scores, human_scores)
    spearman_hybrid = _compute_spearman_rho(hybrid_scores, human_scores)

    mae_hybrid = _compute_mae(hybrid_scores, human_scores)
    rmse_hybrid = _compute_rmse(hybrid_scores, human_scores)
    mae_semantic = _compute_mae(semantic_scores, human_scores)
    mae_llm = _compute_mae(llm_scores, human_scores)

    # Verdict alignment
    verdict_matches = sum(1 for h, s in zip(human_verdicts, system_verdicts) if h == s)
    total_count = len(evaluated_entries)
    verdict_accuracy = (verdict_matches / total_count * 100.0) if total_count > 0 else 0.0

    # Tolerance agreement (predictions within +-12 points of human judgment)
    tolerant_matches = sum(1 for h, s in zip(human_scores, hybrid_scores) if abs(h - s) <= 12.0)
    tolerance_rate = (tolerant_matches / total_count * 100.0) if total_count > 0 else 0.0

    # Domain-specific breakdowns
    subject_breakdowns: Dict[str, Dict[str, Any]] = {}
    subjects = sorted(list(set(e["subject"] for e in evaluated_entries)))
    for subj in subjects:
        subj_entries = [e for e in evaluated_entries if e["subject"] == subj]
        s_human = [float(e["human_evaluation"]["score"]) for e in subj_entries]
        s_hybrid = [float(e["hybrid_score"]) for e in subj_entries]
        s_h_verdict = [str(e["human_evaluation"]["verdict"]).lower().replace(" ", "_") for e in subj_entries]
        s_sys_verdict = [str(e["system_verdict"]).lower().replace(" ", "_") for e in subj_entries]

        s_matches = sum(1 for hv, sv in zip(s_h_verdict, s_sys_verdict) if hv == sv)
        subject_breakdowns[subj] = {
            "sample_count": len(subj_entries),
            "pearson_r": round(_compute_pearson_r(s_hybrid, s_human), 3),
            "spearman_rho": round(_compute_spearman_rho(s_hybrid, s_human), 3),
            "mae": round(_compute_mae(s_hybrid, s_human), 2),
            "rmse": round(_compute_rmse(s_hybrid, s_human), 2),
            "verdict_accuracy_percent": round((s_matches / len(subj_entries) * 100.0), 1) if subj_entries else 0.0
        }

    metrics = {
        "sample_count": total_count,
        "hybrid_vs_human": {
            "pearson_r": round(pearson_hybrid, 3),
            "spearman_rho": round(spearman_hybrid, 3),
            "mae": round(mae_hybrid, 2),
            "rmse": round(rmse_hybrid, 2),
            "verdict_accuracy_percent": round(verdict_accuracy, 1),
            "tolerance_within_12_percent": round(tolerance_rate, 1)
        },
        "semantic_vs_human": {
            "pearson_r": round(pearson_semantic, 3),
            "mae": round(mae_semantic, 2)
        },
        "llm_vs_human": {
            "pearson_r": round(pearson_llm, 3),
            "mae": round(mae_llm, 2)
        },
        "subject_breakdowns": subject_breakdowns
    }

    return evaluated_entries, metrics


def generate_benchmark_markdown_report(metrics: Dict[str, Any], entries: List[Dict[str, Any]]) -> str:
    """Generate a clean GitHub-style markdown report of the benchmark results."""
    m_hybrid = metrics.get("hybrid_vs_human", {})
    m_sem = metrics.get("semantic_vs_human", {})
    m_llm = metrics.get("llm_vs_human", {})

    lines = [
        "# Academic Benchmark Evaluation Report (Phase 39)",
        f"**Total Samples Evaluated**: {metrics.get('sample_count', 0)} across 5 Academic CS Domains",
        "",
        "## 1. Engine Correlation Against Human Judgment",
        "| Evaluation Signal | Pearson Correlation ($r$) | Mean Absolute Error (MAE) | Verdict Agreement |",
        "| :--- | :---: | :---: | :---: |",
        f"| **Hybrid Engine (Master)** | **{m_hybrid.get('pearson_r', 0.0):.3f}** | **{m_hybrid.get('mae', 0.0):.1f} pts** | **{m_hybrid.get('verdict_accuracy_percent', 0.0):.1f}%** |",
        f"| LLM-as-Judge Alone | {m_llm.get('pearson_r', 0.0):.3f} | {m_llm.get('mae', 0.0):.1f} pts | — |",
        f"| Semantic Similarity Alone | {m_sem.get('pearson_r', 0.0):.3f} | {m_sem.get('mae', 0.0):.1f} pts | — |",
        "",
        f"- **Spearman Rank Correlation (rho)**: {m_hybrid.get('spearman_rho', 0.0):.3f}",
        f"- **Root Mean Squared Error (RMSE)**: {m_hybrid.get('rmse', 0.0):.2f}",
        rf"- **Tolerance Match (±12 pts)**: {m_hybrid.get('tolerance_within_12_percent', 0.0):.1f}%",
        "",
        "## 2. Domain Breakdown",
        "| Academic Subject | Samples | Pearson $r$ | Spearman $\rho$ | MAE | Verdict Accuracy |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |"
    ]

    for subj, stats in metrics.get("subject_breakdowns", {}).items():
        lines.append(
            f"| {subj} | {stats['sample_count']} | {stats['pearson_r']:.3f} | "
            f"{stats['spearman_rho']:.3f} | {stats['mae']:.1f} | {stats['verdict_accuracy_percent']:.1f}% |"
        )

    lines.extend([
        "",
        "## 3. Sample Case Evaluations",
        "| ID | Subject | Concept | Human Score | Semantic | LLM | Hybrid | Human Verdict | System Verdict |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    ])

    for e in entries:
        h_score = e["human_evaluation"]["score"]
        h_verd = e["human_evaluation"]["verdict"]
        s_score = e["semantic_score"]
        l_score = e["llm_score"]
        hy_score = e["hybrid_score"]
        sys_verd = e["system_verdict"]
        lines.append(
            f"| `{e['id']}` | {e['subject']} | {e['concept'][:24]} | {h_score:.0f} | {s_score:.1f} | {l_score:.1f} | **{hy_score:.1f}** | `{h_verd}` | `{sys_verd}` |"
        )

    return "\n".join(lines)
