"use strict";
(() => {
 const params=new URLSearchParams(location.search);
 const plans={essencial:"Essencial",evolucao:"Evolução",completo:"Completo"};
 const methods={pix:{name:"Pix",steps:["Abra o aplicativo do seu banco e escolha Pix.","Na versão real, escaneie o QR Code ou use o código copia e cola emitido pelo provedor.","Confira beneficiário e valor antes de confirmar no banco."],title:"QR Code e copia e cola",note:"Nesta demonstração não há QR Code nem código pagável."},card:{name:"Cartão",steps:["Na versão real, você será encaminhado ao checkout seguro do provedor.","Escolha as condições disponíveis e informe os dados somente naquele ambiente.","Revise o valor e aguarde a autorização do pagamento."],title:"Checkout do provedor",note:"Prévia do redirecionamento. Nenhum provedor será aberto e nenhum dado de cartão será solicitado."},boleto:{name:"Boleto bancário",steps:["Na versão real, confira os dados solicitados pelo provedor para emitir o boleto.","Visualize, salve ou imprima o documento emitido.","Pague pelo aplicativo do banco ou canal aceito e aguarde a confirmação."],title:"Seu modelo de boleto",note:"Este modelo pode ser impresso ou salvo em PDF pelo diálogo de impressão. Não pode ser pago."},bitcoin:{name:"Bitcoin",steps:["Na versão real, confira a rede, a cotação e a validade da cobrança no provedor.","Revise o endereço e a quantidade exata antes de enviar pela sua carteira.","Aguarde as confirmações exigidas pelo provedor."],title:"Cobrança em Bitcoin",note:"Nenhum endereço, QR Code ou cotação foi emitido. Não envie criptomoedas."}};
 const creditPurchase=params.get("produto")==="creditos";
 const credits=["100","300","1000"].includes(params.get("creditos"))?params.get("creditos"):"100";
 const own=(obj,key)=>Object.prototype.hasOwnProperty.call(obj,key);
 const method=["pix","bitcoin"].includes(params.get("pagamento"))?params.get("pagamento"):"pix";
 let plan=own(plans,params.get("plano"))?params.get("plano"):"evolucao",step=0;
 const item=methods[method],content=document.getElementById("step-content"),title=document.getElementById("step-title"),description=document.getElementById("step-description"),next=document.getElementById("next"),previous=document.getElementById("previous");
 document.getElementById("method-label").textContent="FINANCEIRO / "+item.name;
 function element(tag,text,className){const e=document.createElement(tag);e.textContent=text;if(className)e.className=className;return e;}
 function render(focus=true){
 content.replaceChildren();document.querySelectorAll(".steps li").forEach((li,index)=>{li.classList.toggle("active",index===step);if(index===step)li.setAttribute("aria-current","step");else li.removeAttribute("aria-current");});
 document.getElementById("change-method").href="/financeiro/contratacao?plano="+plan+"&pagamento="+method;
 previous.textContent=step===0?"Voltar às formas de pagamento":"← Etapa anterior";next.textContent=step===2?"Concluir demonstração":step===3?"Recomeçar":"Continuar →";
 if(step===0){title.textContent="Revise seu plano";description.textContent="Escolha o plano para explorar o pagamento por "+item.name+".";
 const label=element("label","Plano demonstrativo");label.htmlFor="plan-choice";const select=element("select","");select.id="plan-choice";select.className="review-select";for(const [key,name] of Object.entries(plans)){const option=element("option",name);option.value=key;option.selected=key===plan;select.append(option);}select.addEventListener("change",()=>{plan=select.value;document.getElementById("change-method").href="/financeiro/contratacao?plano="+plan+"&pagamento="+method;});content.append(label,select,element("p","Valor e periodicidade: a definir. Cobrança nesta etapa: nenhuma.","notice"));
 }else if(step===1){title.textContent="Como funciona: "+item.name;description.textContent="Conheça as etapas previstas para a integração real.";const list=element("ol", "","instruction-list");item.steps.forEach(text=>list.append(element("li",text)));content.append(list,element("p","Use apenas esta prévia. Não insira dados pessoais ou financeiros.","notice"));
 }else if(step===2){title.textContent=item.title;description.textContent=item.note;
 const ticket=element("section","","ticket");ticket.append(element("strong","DEMONSTRAÇÃO — SEM VALIDADE PARA PAGAMENTO","ticket-mark"),element("h2",creditPurchase?"Sabino.AI · Recarga de "+credits+" créditos":"Sabino.AI · Financeiro "+plans[plan]),element("p","Forma: "+item.name),element("p","Valor: a definir · Nenhuma cobrança emitida"));
 if(method==="boleto"){ticket.append(element("p","Pagador: exemplo demonstrativo — sem dados pessoais"),element("p","Vencimento: não emitido"),element("strong","Linha digitável e código de barras: não emitidos"),element("p","Este documento não é um boleto bancário registrado. Não utilize para pagamento."));const print=element("button","Imprimir / salvar modelo em PDF","button secondary no-print");print.type="button";print.addEventListener("click",()=>window.print());content.append(ticket,print);}else{ticket.append(element("strong",method==="pix"?"Código Pix: não emitido":method==="card"?"Ambiente do provedor: não conectado":"Endereço e cotação: não emitidos"),element("p",item.note));content.append(ticket);}
 }else{title.textContent="Demonstração concluída";description.textContent="Você percorreu as etapas de pagamento por "+item.name+".";content.append(element("p","Nenhum pagamento foi realizado. Seu plano e suas permissões permanecem inalterados.","notice"),element("p","Na versão real, após a emissão, a cobrança ficará aguardando confirmação do provedor. Só uma confirmação validada pelo backend poderá liberar o acesso."));}
 if(creditPurchase){
 document.getElementById("change-method").href="/static/sabino-creditos.html#recharge";
 document.getElementById("method-label").textContent="CRÉDITOS DA INNA / "+item.name;
 if(step===0){title.textContent="Revise sua recarga";description.textContent="Pacote demonstrativo de "+credits+" créditos da INNA.";content.replaceChildren(element("p","Preço e validade a definir. Nenhuma cobrança nesta demonstração.","notice"));}
 if(step===3){content.replaceChildren(element("p","Prévia concluída. Nenhum crédito foi adicionado e nenhum pagamento foi realizado.","notice"),element("p","Na versão real, o backend só adicionará créditos após validar a confirmação do provedor."));}
 }
 if(method==="pix" && step===2){const real=element("a","Abrir pagamento Pix real","button primary no-print");real.href="/static/sabino-pix.html?plano="+encodeURIComponent(plan)+(creditPurchase?"&produto=creditos&creditos="+credits:"");content.append(real); }
 if(focus)title.focus();
 }
 next.addEventListener("click",()=>{step=step===3?0:step+1;render();});previous.addEventListener("click",()=>{if(step===0){location.assign(document.getElementById("change-method").href);return;}step--;render();});render(false);
})();
