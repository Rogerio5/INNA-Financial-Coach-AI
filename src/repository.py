from src.database import get_db_session, init_db
from src.models import DiagnosticoFinanceiro, FeedbackUsuario


def save_diagnostico_db(payload: dict, response: dict) -> None:
    init_db()

    with get_db_session() as session:
        registro = DiagnosticoFinanceiro(
            nome=payload.get("nome", "Usuário"),
            renda_mensal=float(payload.get("renda_mensal", 0)),
            gastos_fixos=float(payload.get("gastos_fixos", 0)),
            gastos_variaveis=float(payload.get("gastos_variaveis", 0)),
            dividas_mensais=float(payload.get("dividas_mensais", 0)),
            reserva_atual=float(payload.get("reserva_atual", 0)),
            objetivo=payload.get("objetivo", ""),
            saldo_estimado=float(response.get("saldo_estimado", 0)),
            comprometimento_renda_percentual=float(
                response.get("comprometimento_renda_percentual", 0)
            ),
            meses_reserva_estimados=float(response.get("meses_reserva_estimados", 0)),
            score_financeiro=int(response.get("score_financeiro", 0)),
            nivel_risco=response.get("nivel_risco", "Indefinido"),
            diagnostico=response.get("diagnostico", ""),
            plano_30_dias=response.get("plano_30_dias", ""),
        )

        session.add(registro)


def save_feedback_db(
    nome: str,
    util: str,
    comentario: str,
    score_financeiro: int,
    nivel_risco: str,
) -> None:
    init_db()

    with get_db_session() as session:
        feedback = FeedbackUsuario(
            nome=nome,
            util=util,
            comentario=comentario,
            score_financeiro=int(score_financeiro),
            nivel_risco=nivel_risco,
        )

        session.add(feedback)


def list_diagnosticos_db(limit: int = 50) -> list[dict]:
    init_db()

    with get_db_session() as session:
        registros = (
            session.query(DiagnosticoFinanceiro)
            .order_by(DiagnosticoFinanceiro.id.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": item.id,
                "data_hora": item.data_hora,
                "nome": item.nome,
                "renda_mensal": item.renda_mensal,
                "gastos_fixos": item.gastos_fixos,
                "gastos_variaveis": item.gastos_variaveis,
                "dividas_mensais": item.dividas_mensais,
                "reserva_atual": item.reserva_atual,
                "objetivo": item.objetivo,
                "saldo_estimado": item.saldo_estimado,
                "comprometimento_renda_percentual": item.comprometimento_renda_percentual,
                "meses_reserva_estimados": item.meses_reserva_estimados,
                "score_financeiro": item.score_financeiro,
                "nivel_risco": item.nivel_risco,
                "diagnostico": item.diagnostico,
                "plano_30_dias": item.plano_30_dias,
            }
            for item in registros
        ]


def list_feedbacks_db(limit: int = 50) -> list[dict]:
    init_db()

    with get_db_session() as session:
        registros = (
            session.query(FeedbackUsuario)
            .order_by(FeedbackUsuario.id.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": item.id,
                "data_hora": item.data_hora,
                "nome": item.nome,
                "util": item.util,
                "comentario": item.comentario,
                "score_financeiro": item.score_financeiro,
                "nivel_risco": item.nivel_risco,
            }
            for item in registros
        ]


def get_diagnostico_by_id_db(diagnostico_id: int) -> dict | None:
    init_db()

    with get_db_session() as session:
        item = (
            session.query(DiagnosticoFinanceiro)
            .filter(DiagnosticoFinanceiro.id == diagnostico_id)
            .first()
        )

        if item is None:
            return None

        return {
            "id": item.id,
            "data_hora": item.data_hora,
            "nome": item.nome,
            "renda_mensal": item.renda_mensal,
            "gastos_fixos": item.gastos_fixos,
            "gastos_variaveis": item.gastos_variaveis,
            "dividas_mensais": item.dividas_mensais,
            "reserva_atual": item.reserva_atual,
            "objetivo": item.objetivo,
            "saldo_estimado": item.saldo_estimado,
            "comprometimento_renda_percentual": item.comprometimento_renda_percentual,
            "meses_reserva_estimados": item.meses_reserva_estimados,
            "score_financeiro": item.score_financeiro,
            "nivel_risco": item.nivel_risco,
            "diagnostico": item.diagnostico,
            "plano_30_dias": item.plano_30_dias,
        }
