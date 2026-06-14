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
