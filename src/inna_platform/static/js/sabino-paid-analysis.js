const headers = {'Content-Type': 'application/json', 'X-Sabino-Analysis': 'confirmed'};
let busy = false;

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
    const quoteResponse = await fetch('/api/inna/quote', {method: 'POST', headers, credentials:'same-origin', body:JSON.stringify({...payload, request_id:requestId})});
    const quote = await quoteResponse.json();
    if (!quoteResponse.ok) throw new Error(quoteResponse.status === 401 ? 'Entre na sua conta para analisar com a INNA.' : quote.detail || 'Não foi possível consultar o custo.');
    if (quote.state === 'quoted') {
      const walletResponse = await fetch('/api/platform/credits/wallet', {cache:'no-store', credentials:'same-origin'});
      if (!walletResponse.ok) throw new Error('Não foi possível consultar seu saldo.');
      const wallet = await walletResponse.json();
      if (wallet.balance < quote.cost) throw new Error(`Saldo insuficiente: esta análise custa ${quote.cost} créditos. Acesse Minha carteira para recarregar.`);
      if (!await confirmCost(quote.cost, wallet.balance)) throw new Error('Análise cancelada. Nenhum crédito foi consumido.');
    }
    let response;
    try {
      response = await fetch('/api/inna/ask', {method:'POST', headers, credentials:'same-origin', body:JSON.stringify({...payload, quote_id:quote.quote_id}), signal:options.signal});
    } catch (_) {
      throw new Error('Conexão interrompida. Consulte o histórico de análises na carteira antes de tentar novamente.');
    }
    const result = await response.clone().json();
    if (result.billing?.state === 'completed' || result.billing?.state === 'refunded' || response.status === 409) sessionStorage.removeItem(key);
    if (response.status === 202) throw new Error(result.detail + ' Consulte Minha carteira.');
    window.dispatchEvent(new CustomEvent('sabino:credits:updated'));
    return response;
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
    const response = await fetch('/api/inna/pricing', {cache:'no-store'});
    const price = await response.json();
    note.textContent = response.status === 401 ? 'Entre na sua conta para consultar o custo e usar a INNA. '
      : response.ok && price.enabled ? `Análise: ${price.cost} créditos, com confirmação antes de iniciar. `
      : 'Análises com créditos temporariamente indisponíveis. Seu saldo está preservado. ';
  } catch (_) { note.textContent = 'Não foi possível consultar o custo. '; }
  note.append(link);
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', showPrice); else showPrice();
