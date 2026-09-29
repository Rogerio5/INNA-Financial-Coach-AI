"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const money = cents => (cents / 100).toLocaleString("pt-BR", {style:"currency",currency:"BRL"});
  let selected;
  async function load() {
    byId("orders").replaceChildren();
    byId("status").textContent = "Consultando pendências…";
    try {
      const response = await fetch("/api/platform/pix/review/pending", {cache:"no-store"});
      if (!response.ok) {byId("status").textContent = response.status===401 ? "Entre na sua conta para continuar." : response.status===403 ? "Sua conta não tem permissão para conferir Pix." : "Conferência indisponível. Tente novamente mais tarde."; return;}
      const data = await response.json();
      byId("status").textContent = data.orders.length ? "Selecione o pedido correspondente ao recebimento no banco." : "Nenhum pedido pendente.";
      for (const order of data.orders) {
        const section=document.createElement("section"); section.className="panel";
        const text=document.createElement("p"); text.textContent=`${order.product_code} · ${money(order.amount_cents)} · Pedido ${order.order_id} · Conta ${order.user_id} · Chave recebedora ${order.receiver_key}`;
        const button=document.createElement("button");button.className="button secondary";button.textContent="Conferir";
        button.onclick=()=>{selected=order;byId("form").reset();byId("approve").disabled=false;byId("result").textContent="";byId("selected").textContent=text.textContent;byId("review").hidden=false;byId("bank").focus();};
        section.append(text,button);byId("orders").append(section);
      }
    } catch (_) {byId("status").textContent="Não foi possível consultar os pedidos.";}
  }
  byId("refresh").onclick=load;
  byId("cancel").onclick=()=>{byId("review").hidden=true;};
  byId("form").onsubmit=async event=>{
    event.preventDefault();if(!selected)return;
    const parts=byId("amount").value.trim().replace(",", ".").split(".");
    const received=Number(parts[0])*100+Number((parts[1]||"").padEnd(2,"0"));
    if(!Number.isSafeInteger(received)||received!==selected.amount_cents){byId("result").textContent="O valor recebido deve ser igual ao valor do pedido.";return;}
    byId("approve").disabled=true;byId("result").textContent="Registrando conferência…";
    try{
      const response=await fetch(`/api/platform/pix/review/${encodeURIComponent(selected.order_id)}`,{method:"POST",headers:{"Content-Type":"application/json","X-Sabino-Pix":"manual"},body:JSON.stringify({bank_reference:byId("bank").value.trim(),received_cents:received,reason:byId("reason").value.trim(),bank_verified:byId("verified").checked})});
      const data=await response.json();
      if(!response.ok){byId("result").textContent=typeof data.detail==="string"?data.detail:"Confira os campos e tente novamente.";byId("approve").disabled=false;return;}
      byId("result").textContent="Recebimento registrado. Benefícios liberados uma única vez.";await load();
    }catch(_){byId("result").textContent="Resposta não recebida. Atualize as pendências antes de tentar novamente.";}
  };
  load();
})();
