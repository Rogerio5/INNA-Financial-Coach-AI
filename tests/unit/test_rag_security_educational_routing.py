from __future__ import annotations

import src.rag_engine as rag_engine


def test_pix_educational_question_bypasses_security_fast_path():
    result = rag_engine.answer_security_financeira(
        "Como usar Pix com seguranca?"
    )

    assert result is None


def test_pix_prevention_question_bypasses_security_fast_path():
    result = rag_engine.answer_security_financeira(
        "Como evitar golpe no Pix?"
    )

    assert result is None


def test_pix_wrong_transfer_keeps_security_fast_path():
    result = rag_engine.answer_security_financeira(
        "Fiz um Pix errado, o que faco agora?"
    )

    assert isinstance(result, dict)
    assert result["resposta"]
    assert result["modo"].endswith(
        "_seguranca_financeira"
    )


def test_pix_incident_keeps_security_fast_path():
    result = rag_engine.answer_security_financeira(
        "Cai em golpe no Pix, o que devo fazer?"
    )

    assert isinstance(result, dict)
    assert result["resposta"]
    assert result["modo"].endswith(
        "_seguranca_financeira"
    )
