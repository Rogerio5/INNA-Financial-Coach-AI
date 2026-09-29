"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const select = byId("product"), generate = byId("generate"), status = byId("status");
  const money = cents => (cents / 100).toLocaleString("pt-BR", {style:"currency", currency:"BRL"});
  const labels = new Map();
  let activeOrder = null, imageUrl = null, enabled = false, creating = false;
  let loading = false, timer = null, hasPending = false, requestVersion = 0;
  const panel = document.createElement("section"); panel.className = "panel";
  const heading = document.createElement("h2"); heading.textContent = "Meus pedidos Pix";
  const refresh = document.createElement("button"); refresh.className = "button secondary"; refresh.textContent = "Atualizar pedidos";
  const notice = document.createElement("p"); notice.setAttribute("role", "status");
  const list = document.createElement("div");
  panel.append(heading, refresh, notice, list); document.querySelector("main").append(panel);

  function link(label, href) {
    const item = document.createElement("a"); item.className = "button secondary";
    item.textContent = label; item.href = href; return item;
  }
  function clearPayment() {
    byId("payment").hidden = true;
    byId("code").value = ""; byId("key").textContent = "";
    byId("qr").removeAttribute("src");
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    imageUrl = null;
  }
  function showInstructions(order) {
    activeOrder = order;
    if (order.status === "verified" || order.status === "cancelled") { syncActive(order); return; }
    clearPayment();
    byId("summary").textContent = (order.label || labels.get(order.product_code) || order.product_code) + " — " + money(order.amount_cents);
    byId("recipient").textContent = "Recebedor configurado: " + order.receiver;
    byId("reference").textContent = "Pedido: " + order.order_id;
    byId("code").value = order.payload;
    byId("key").textContent = "Chave Pix: " + order.key;
    imageUrl = URL.createObjectURL(new Blob([order.svg], {type:"image/svg+xml"}));
    byId("qr").src = imageUrl; byId("payment").hidden = false;
    select.disabled = true; generate.disabled = true; schedule();
    status.textContent = "Pedido emitido. Aguardando conferência manual. Se já pagou, não pague novamente. O status será atualizado automaticamente.";
  }
  function syncActive(order) {
    if (!activeOrder || activeOrder.order_id !== order.order_id) return;
    activeOrder = {...activeOrder, ...order};
    if (order.status !== "verified" && order.status !== "cancelled") return;
    clearPayment();
    select.disabled = false; generate.disabled = !enabled || creating;
    status.textContent = order.status === "verified"
      ? "Pagamento conferido. Benefícios liberados. Acesse sua carteira ou sua assinatura abaixo. Não pague este pedido novamente."
      : "Pedido cancelado. Não pague o código deste pedido.";
  }
  function schedule() {
    clearTimeout(timer);
    if ((hasPending || activeOrder?.status === "awaiting_manual_verification") && !document.hidden) timer = setTimeout(loadOrders, 15000);
  }
  async function loadOrders() {
    if (loading) return;
    loading = true; refresh.disabled = true;
    try {
      const response = await fetch("/api/platform/pix/orders", {cache:"no-store", credentials:"same-origin"});
      if (!response.ok) {
        if (response.status === 401) {
          clearPayment(); activeOrder = null; list.replaceChildren(); hasPending = false;
          notice.replaceChildren(document.createTextNode("Entre na sua conta para consultar seus pedidos. "), link("Entrar", "/static/sabino-login-gateway.html"));
        } else notice.textContent = "Não foi possível atualizar. O status exibido pode estar desatualizado; não repita o pagamento.";
        return;
      }
      const data = await response.json();
      hasPending = data.orders.some(order => order.status === "awaiting_manual_verification");
      notice.textContent = hasPending ? "Atualização automática a cada 15 segundos enquanto esta página estiver visível. A aprovação continua manual." : "Pedidos atualizados.";
      list.replaceChildren();
      if (!data.orders.length) list.textContent = "Nenhum pedido emitido.";
      for (const order of data.orders) {
        syncActive(order);
        const row = document.createElement("article"); row.className = "panel";
        const text = document.createElement("p");
        const state = order.status === "verified" ? "Pagamento conferido · benefícios liberados" : order.status === "cancelled" ? "Cancelado" : "Aguardando conferência";
        text.textContent = `${labels.get(order.product_code) || order.product_code} · ${money(order.amount_cents)} · ${state}`;
        const reference = document.createElement("p"); reference.textContent = "Pedido: " + order.order_id;
        row.append(text, reference);
        if (order.status === "verified") {
          row.append(link(order.product_code.startsWith("credits_") ? "Ver saldo na carteira" : "Ver minha assinatura", order.product_code.startsWith("credits_") ? "/static/sabino-carteira.html" : "/financeiro/meu-plano"), link("Abrir INNA", "/inna"));
        } else if (order.status === "awaiting_manual_verification") {
          const view = document.createElement("button"); view.className = "button secondary"; view.textContent = "Ver instruções";
          view.onclick = async () => {
            const version = ++requestVersion; view.disabled = true;
            try {
              const response = await fetch(`/api/platform/pix/orders/${encodeURIComponent(order.order_id)}`, {cache:"no-store"});
              if (!response.ok) throw Error();
              const details = await response.json();
              if (version !== requestVersion || !row.isConnected) return;
              showInstructions(details); await loadOrders();
            } catch (_) { notice.textContent = "Não foi possível consultar as instruções. Atualize os pedidos antes de pagar."; }
            finally { view.disabled = false; }
          };
          row.append(view);
        }
        list.append(row);
      }
    } catch (_) { notice.textContent = "Falha de conexão. Atualize antes de pagar; não repita um pagamento já realizado."; }
    finally { loading = false; refresh.disabled = false; schedule(); }
  }
  async function init() {
    try {
      const response = await fetch("/api/platform/pix/catalog", {cache:"no-store"});
      if (!response.ok) throw Error();
      const data = await response.json(); enabled = data.enabled === true;
      const params = new URLSearchParams(location.search);
      const selected = params.get("produto") === "creditos" ? "credits_" + params.get("creditos") : params.get("plano");
      for (const [code, product] of Object.entries(data.products)) {
        labels.set(code, product.label);
        const option = document.createElement("option"); option.value = code;
        option.textContent = product.label + " — " + money(product.amount_cents);
        option.selected = code === selected; select.append(option);
      }
      generate.disabled = !enabled;
      status.textContent = enabled ? "Confira o produto e o valor antes de gerar. É necessário estar conectado à sua conta." : "Emissão em preparação. Nenhum Pix gerado.";
    } catch (_) { status.textContent = "Pix indisponível. Tente novamente mais tarde."; }
    await loadOrders();
  }
  generate.onclick = async () => {
    if (creating || !enabled) return;
    creating = true; generate.disabled = true; select.disabled = true; ++requestVersion;
    status.textContent = "Gerando instruções…";
    try {
      const response = await fetch("/api/platform/pix/orders", {method:"POST", credentials:"same-origin", headers:{"Content-Type":"application/json", "X-Sabino-Pix":"manual"}, body:JSON.stringify({product_code:select.value})});
      if (!response.ok) {
        status.textContent = response.status === 401 ? "Entre na sua conta antes de gerar o Pix." : "Não foi possível confirmar a emissão. Consulte seus pedidos antes de tentar novamente.";
        if (response.status >= 400 && response.status < 500) { generate.disabled = !enabled; select.disabled = false; }
        return;
      }
      showInstructions(await response.json());
    } catch (_) { status.textContent = "Não foi possível confirmar a emissão. Consulte seus pedidos; não pague sem código e referência."; }
    finally { creating = false; await loadOrders(); }
  };
  async function copy(value) {
    if (!activeOrder || activeOrder.status === "verified" || activeOrder.status === "cancelled" || byId("payment").hidden) return;
    try { await navigator.clipboard.writeText(value); status.textContent = "Copiado. Se já pagou, aguarde a conferência e não pague novamente."; }
    catch (_) { status.textContent = "Não foi possível copiar. Selecione e copie o texto exibido."; }
  }
  byId("copy-code").onclick = () => activeOrder && copy(activeOrder.payload);
  byId("copy-key").onclick = () => activeOrder && copy(activeOrder.key);
  refresh.onclick = loadOrders;
  document.addEventListener("visibilitychange", () => { if (!document.hidden) loadOrders(); else clearTimeout(timer); });
  window.addEventListener("focus", loadOrders);
  window.addEventListener("pagehide", () => { clearTimeout(timer); if (imageUrl) URL.revokeObjectURL(imageUrl); });
  init();
})();
