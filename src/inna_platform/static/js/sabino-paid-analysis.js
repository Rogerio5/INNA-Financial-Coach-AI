const headers = {'Content-Type': 'application/json', 'X-Sabino-Analysis': 'confirmed'};
let busy = false;

function progress(message) {
  const status = document.querySelector('.inna-loading');
  if (status) { status.textContent = message; status.setAttribute('role', 'status'); }
  let summary = document.getElementById('inna-analysis-status');
  const note = document.getElementById('inna-credit-price');
  if (!summary && note) {
    summary = document.createElement('p'); summary.id = 'inna-analysis-status';
    summary.setAttribute('role', 'status'); summary.style.cssText = 'font:14px system-ui;color:#cad3d6;margin:4px 0 12px';
    note.insertAdjacentElement('afterend', summary);
  }
  if (summary) summary.textContent = message;
}

async function requestJSON(url, init = {}, timeout = 60000) {
  const controller = new AbortController();
  const abort = () => controller.abort();
  if (init.signal?.aborted) abort();
  else init.signal?.addEventListener('abort', abort, {once:true});
  const timer = setTimeout(abort, timeout);
  try {
    const response = await fetch(url, {...init, signal:controller.signal});
    const data = await response.clone().json();
    return {response, data};
  } finally {
    clearTimeout(timer);
    init.signal?.removeEventListener('abort', abort);
  }
}

function confirmCost(cost, balance) {
  return new Promise(resolve => {
    const dialog = document.createElement('dialog');
    dialog.style.cssText = 'background:#101718;color:#fff;border:1px solid #e7bd45;border-radius:16px;padding:24px;max-width:440px;font:16px system-ui';
    const title = document.createElement('h2'); title.textContent = 'Confirmar análise da INNA';
    const text = document.createElement('p');
    text.textContent = `Esta análise custa ${cost} créditos. Seu saldo é ${balance} créditos. O custo será reservado ao iniciar e confirmado quando a resposta for concluída.`;
    const policy = document.createElement('p'); policy.textContent = 'Em caso de falha confirmada, os créditos serão devolvidos. Interrupções com resultado incerto ficam em conferência.';
    const cancel = document.createElement('button'); cancel.textContent = 'Cancelar';
    const accept = document.createElement('button'); accept.textContent = `Analisar por ${cost} créditos`;
    for (const button of [cancel, accept]) button.style.cssText = 'padding:12px;margin:8px;border-radius:8px;cursor:pointer';
    const done = value => { dialog.close(); dialog.remove(); resolve(value); };
    cancel.onclick = () => done(false); accept.onclick = () => done(true);
    dialog.oncancel = event => { event.preventDefault(); done(false); };
    dialog.append(title, text, policy, cancel, accept); document.body.append(dialog); dialog.showModal(); cancel.focus();
  });
}

export async function askPaid(payload, options = {}) {
  if (busy) throw new Error('Já existe uma análise em andamento nesta página.');
  busy = true;
  try {
    const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(payload)));
    const key = 'sabino.analysis.request.' + Array.from(new Uint8Array(bytes), n => n.toString(16).padStart(2, '0')).join('');
    let requestId = sessionStorage.getItem(key);
    if (!requestId) { requestId = crypto.randomUUID(); sessionStorage.setItem(key, requestId); }
    progress('Consultando o custo da análise...');
    let quoteResponse, quote;
    try {
      ({response:quoteResponse, data:quote} = await requestJSON('/api/inna/quote', {method:'POST', headers, credentials:'same-origin', body:JSON.stringify({...payload, request_id:requestId}), signal:options.signal}));
    } catch (_) {
      throw new Error('Não foi possível consultar o custo agora. A análise não foi iniciada nesta tentativa. Tente novamente em instantes.');
    }
    if (!quoteResponse.ok) throw new Error(quoteResponse.status === 401 ? 'Entre na sua conta para analisar com a INNA.' : quote.detail || 'Não foi possível consultar o custo.');
    if (quote.state === 'quoted') {
      progress('Conferindo seu saldo de créditos...');
      let walletResponse, wallet;
      try {
        ({response:walletResponse, data:wallet} = await requestJSON('/api/platform/credits/wallet', {cache:'no-store', credentials:'same-origin', signal:options.signal}));
      } catch (_) { throw new Error('Não foi possível consultar seu saldo agora. A análise não foi iniciada nesta tentativa.'); }
      if (!walletResponse.ok) throw new Error('Não foi possível consultar seu saldo.');
      if (wallet.balance < quote.cost) throw new Error(`Saldo insuficiente: esta análise custa ${quote.cost} créditos. Acesse Minha carteira para recarregar.`);
      progress('Aguardando sua confirmação de créditos.');
      if (!await confirmCost(quote.cost, wallet.balance)) throw new Error('Análise cancelada. Nenhum crédito foi consumido.');
    }
    const resultURL = '/api/inna/analyses/' + encodeURIComponent(quote.quote_id);
    progress(quote.state === 'completed' ? 'Recuperando a resposta concluída, sem nova cobrança...' : 'Iniciando a análise… Aguardando confirmação da reserva de créditos.');
    let response, result;
    try {
      if (quote.state === 'quoted') {
        ({response, data:result} = await requestJSON('/api/inna/ask', {method:'POST', headers, credentials:'same-origin', body:JSON.stringify({...payload, quote_id:quote.quote_id}), signal:options.signal}, 180000));
      } else {
        ({response, data:result} = await requestJSON(resultURL, {cache:'no-store', credentials:'same-origin', signal:options.signal}));
      }
    } catch (_) {
      // A lost response is not proof of failure: read the same operation, never start another.
      try {
        ({response, data:result} = await requestJSON(resultURL, {cache:'no-store', credentials:'same-origin', signal:options.signal}, 15000));
      } catch (_) {
        throw new Error('Não foi possível confirmar o resultado. Consulte Minha carteira. Reenviar esta mesma pergunta nesta aba consultará a análise existente, sem iniciar outra cobrança.');
      }
    }
    for (let attempt = 0; response.status === 202 && result.billing?.state === 'running' && attempt < 5; attempt++) {
      progress('Analisando… Consultando o andamento sem nova cobrança.');
      await new Promise(resolve => setTimeout(resolve, 2000));
      ({response, data:result} = await requestJSON(resultURL, {cache:'no-store', credentials:'same-origin', signal:options.signal}, 15000));
    }
    // Keep completed requests reusable in this tab. Only a refunded or expired quote can be replaced.
    if (result.billing?.state === 'refunded' || (response.status === 409 && quote.state === 'quoted')) sessionStorage.removeItem(key);
    window.dispatchEvent(new CustomEvent('sabino:credits:updated'));
    if (response.status === 202) throw new Error(result.detail || 'Análise em andamento. Consulte Minha carteira sem nova cobrança.');
    if (result.billing?.state === 'completed') progress('Concluído. Resposta disponível; reenviar esta mesma pergunta nesta aba não cobra novamente.');
    else if (result.billing?.state === 'refunded') progress('Falhou — os créditos foram devolvidos.');
    else if (!response.ok) progress(typeof result.detail === 'string' ? result.detail : 'Não foi possível iniciar a análise. Consulte Minha carteira.');
    return response;
  } catch (error) {
    progress(error.message || 'Não foi possível confirmar a análise. Consulte Minha carteira.');
    throw error;
  } finally { busy = false; }
}

async function showPrice() {
  const input = document.getElementById('innaInput');
  if (!input || document.getElementById('inna-credit-price')) return;
  const note = document.createElement('p'); note.id = 'inna-credit-price';
  note.style.cssText = 'font:14px system-ui;color:#f1cf70;padding:8px 0;margin:0';
  const link = document.createElement('a'); link.href = '/static/sabino-carteira.html'; link.textContent = 'Minha carteira e histórico'; link.style.color = 'inherit';
  const target = document.querySelector('.chat-header');
  (target || input.parentElement).insertAdjacentElement('afterend', note);
  try {
    const {response, data:price} = await requestJSON('/api/inna/pricing', {cache:'no-store'});
    note.textContent = response.status === 401 ? 'Entre na sua conta para consultar o custo e usar a INNA. '
      : response.ok && price.enabled ? `Análise: ${price.cost} créditos, com confirmação antes de iniciar. `
      : 'Análises com créditos temporariamente indisponíveis. Seu saldo está preservado. ';
  } catch (_) { note.textContent = 'Não foi possível consultar o custo. '; }
  note.append(link);
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', showPrice); else showPrice();
