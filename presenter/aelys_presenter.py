#!/usr/bin/env python3
from __future__ import annotations

class PresenterError(RuntimeError):
    pass

def compose(question: str, evidence_refs: list[str] | None = None, *, evidence_level: str="UNVERIFIED") -> dict:
    q=(question or "").strip()
    if not q:
        raise PresenterError("EMPTY_QUESTION")
    refs=evidence_refs or []
    return {
      "schema":"F173_AELYS_PRESENTATION_V1",
      "status":"READY" if refs else "HOLD",
      "question":q,
      "text":"",
      "evidence_refs":refs,
      "evidence_level":evidence_level,
      "claim_ceiling":"NO_FACTUAL_PRESENTATION_TEXT_UNTIL_EVIDENCE_BACKED_CONTEXT_IS_SUPPLIED",
      "training_executed":False,
      "weights_changed":False
    }
