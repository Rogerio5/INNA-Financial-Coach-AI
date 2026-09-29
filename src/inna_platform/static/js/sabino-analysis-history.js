"use strict";
(() => {
  const host = document.createElement('section'); host.className = 'panel';
  const heading = document.createElement('h2'); heading.textContent = 'Minhas análises da INNA';
  const refresh = document.createElement('button'); refresh.className = 'button secondary'; refresh.textContent = 'Atualizar análises';
  const list = document.createElement('div'); list.setAttribute('aria-live','polite');
  host.append(heading, refresh, list); document.querySelector('main footer').before(host);
  const states = {running:'Em processamento; se persistir, solicite conferência', needs_review:'Aguardando conferência — não execute novamente', completed:'Concluída', refunded:'Falhou — créditos devolvidos'};
  async function load() {
    refresh.disabled = true; list.textContent = 'Consultando análises…';
    try {
      const response = await fetch('/api/inna/analyses', {cache:'no-store'});
      if (!response.ok) throw Error();
      const data = await response.json(); list.replaceChildren();
      if (!data.analyses.length) list.textContent = 'Nenhuma análise com créditos registrada.';
      for (const entry of data.analyses) {
        const row = document.createElement('article');
        const description = document.createElement('p'); description.textContent = `${new Date(entry.created_at).toLocaleString('pt-BR')} · ${entry.cost} créditos · ${states[entry.state] || entry.state} · Referência ${entry.quote_id}`;
        row.append(description);
        if (entry.state === 'completed') {
          const button = document.createElement('button'); button.className = 'button secondary'; button.textContent = 'Ver resposta sem nova cobrança';
          const answer = document.createElement('p'); answer.style.whiteSpace = 'pre-wrap';
          button.onclick = async () => {
            button.disabled = true;
            try {
              const result = await fetch('/api/inna/analyses/' + encodeURIComponent(entry.quote_id), {cache:'no-store'});
              if (!result.ok) throw Error();
              const content = await result.json(); answer.textContent = content.resposta || content.detail;
            } catch (_) { answer.textContent = 'Não foi possível carregar. Tente novamente.'; }
            finally { button.disabled = false; }
          };
          row.append(button, answer);
        }
        list.append(row);
      }
    } catch (_) { list.textContent = 'Histórico indisponível. Entre na sua conta e tente novamente.'; }
    finally { refresh.disabled = false; }
  }
  refresh.onclick = load; load();
})();
