"use strict";
(() => {
 const plans={essencial:"Essencial",evolucao:"Evolução",completo:"Completo"};
 const options={
  pix:{title:"Pix",heading:"Pague pelo aplicativo do seu banco.",description:"Na integração real, o provedor emitirá um QR Code e um código Pix. O acesso só será liberado após confirmação do pagamento.",art:"◇ DEMONSTRAÇÃO PIX",note:"Nenhum QR Code ou código de pagamento foi gerado."},
  card:{title:"cartão",heading:"Seus dados de cartão ficam no checkout do provedor.",description:"A opção prevista é um checkout hospedado, como o Mercado Pago. Não coletamos dados de cartão nesta demonstração.",art:"▤ CHECKOUT DEMONSTRATIVO",note:"Nenhum cartão será solicitado ou cobrado."},
  boleto:{title:"boleto",heading:"Boleto com acompanhamento de status.",description:"Na integração real, você poderá gerar o boleto, consultar o vencimento e aguardar a confirmação do provedor. Emitir um boleto não significa pagamento aprovado.",art:"▥ BOLETO SEM VALIDADE",note:"Não existe linha digitável ou código de barras pagável nesta demonstração."},
  bitcoin:{title:"Bitcoin",heading:"Uma opção adicional, com integração própria.",description:"O pagamento real dependerá de um provedor cripto, cotação com validade e confirmação da transação. Esses recursos ainda não estão conectados.",art:"₿ DEMONSTRAÇÃO BITCOIN",note:"Nenhum endereço de carteira foi gerado. Não envie criptomoedas."}
 };
 const dialog=document.getElementById("payment-dialog");
 let selected="pix";
 document.querySelectorAll("[data-plan]").forEach(button=>button.addEventListener("click",()=>{
  location.assign("/financeiro/contratacao?plano="+encodeURIComponent(button.dataset.plan));
 }));
 const checkout=location.pathname.includes("/contratacao");
 document.getElementById("plans-view").hidden=checkout;
 document.getElementById("checkout-view").hidden=!checkout;
 const code=new URLSearchParams(location.search).get("plano");
 document.getElementById("selected-plan").textContent=plans[code]||plans.evolucao;
 function select(method){
  selected=method;
  document.querySelectorAll("[data-method]").forEach(button=>{
   const active=button.dataset.method===method;
   button.classList.toggle("selected",active);
   button.setAttribute("aria-pressed",String(active));
  });
  const detail=document.getElementById("method-detail");
  detail.replaceChildren();
  const h=document.createElement("h3"),p=document.createElement("p");
  h.textContent=options[method].heading;p.textContent=options[method].description;
  detail.append(h,p);
  document.getElementById("simulate").textContent="Visualizar demonstração de "+options[method].title+" →";
 }
 document.querySelectorAll("[data-method]").forEach(button=>button.addEventListener("click",()=>select(button.dataset.method)));
 document.getElementById("simulate").addEventListener("click",()=>{
  location.assign("/static/sabino-pagamento.html?pagamento="+encodeURIComponent(selected)+"&plano="+encodeURIComponent(Object.prototype.hasOwnProperty.call(plans,code)?code:"evolucao"));
 });
 dialog.querySelectorAll(".close,.close-action").forEach(button=>button.addEventListener("click",()=>dialog.close()));
 const requestedMethod=new URLSearchParams(location.search).get("pagamento");
 select(["pix","bitcoin"].includes(requestedMethod)?requestedMethod:"pix");
})();
