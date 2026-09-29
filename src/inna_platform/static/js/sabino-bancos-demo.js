"use strict";
(() => {
 const dialog=document.getElementById("bank-dialog"), connections=new Map();
 let selected="";
 function render(){
  const host=document.getElementById("connections");host.replaceChildren();
  if(!connections.size){host.textContent="Nenhuma conexão simulada. Escolha uma instituição para conhecer o fluxo.";return;}
  connections.forEach((scopes,bank)=>{
   const row=document.createElement("div"),label=document.createElement("p"),button=document.createElement("button");
   label.textContent=bank+" · Conexão simulada · "+scopes.join(" e ");
   button.className="button secondary";button.textContent="Desconectar "+bank;
   button.addEventListener("click",()=>{connections.delete(bank);render();});
   row.append(label,button);host.append(row);
  });
 }
 document.querySelectorAll("[data-bank]").forEach(button=>button.addEventListener("click",()=>{
  selected=button.dataset.bank;
  document.getElementById("bank-title").textContent=selected;
  document.getElementById("balances").checked=false;
  document.getElementById("transactions").checked=false;
  document.getElementById("bank-error").textContent="";
  dialog.showModal();
 }));
 dialog.querySelector(".close").addEventListener("click",()=>dialog.close());
 document.getElementById("connect-demo").addEventListener("click",()=>{
  const scopes=[];
  if(document.getElementById("balances").checked)scopes.push("saldos");
  if(document.getElementById("transactions").checked)scopes.push("transações");
  if(!scopes.length){document.getElementById("bank-error").textContent="Escolha pelo menos uma permissão para a simulação.";return;}
  connections.set(selected,scopes);render();dialog.close();
 });
})();
