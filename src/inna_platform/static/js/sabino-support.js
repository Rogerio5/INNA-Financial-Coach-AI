(() => {
'use strict';
const el=id=>document.getElementById(id), admin=location.pathname.startsWith('/admin/');
const states={new:'Novo',in_progress:'Em atendimento',resolved:'Resolvido'};
const categories={technical:'Suporte técnico',access:'Acesso e cadastro',question:'Dúvidas e orientações',suggestion:'Sugestões e melhorias'};
let offset=0, total=0, selected=null, listVersion=0, threadVersion=0, firstMessage=null, shown=0, messageCount=0;
let createId=crypto.randomUUID(), replyId=crypto.randomUUID();
const node=(tag,value)=>{const n=document.createElement(tag);n.textContent=value;return n;};
const date=value=>new Date(value).toLocaleString('pt-BR');
const url=(suffix='')=>'/api/sabino/support'+suffix;
const scoped=path=>path+(path.includes('?')?'&':'?')+'admin='+admin;
async function request(path,method='GET',body){
 const r=await fetch(path,{method,credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json','X-Sabino-Support':'1'},...(body?{body:JSON.stringify(body)}:{})});
 const data=await r.json().catch(()=>({}));
 if(!r.ok)throw Error(r.status===401?'Sua sessão expirou. Entre novamente na Sabino.AI.':typeof data.detail==='string'?data.detail:r.status===422?'Confira os campos e os limites de texto.':'Não foi possível concluir. Tente novamente.');
 return data;
}
async function loadList(){
 const version=++listVersion;el('list-status').textContent='Carregando chamados…';el('tickets').replaceChildren();el('previous').disabled=true;el('next').disabled=true;el('page').textContent='';
 try{
  const q=new URLSearchParams({admin:String(admin),offset:String(offset)});if(el('filter').value)q.set('state',el('filter').value);
  const data=await request(url()+'?'+q);if(version!==listVersion)return;
  total=data.total;el('admin-link').hidden=admin||!data.is_admin;
  for(const row of data.tickets){const b=node('button','');b.type='button';b.className='ticket';b.append(node('strong',row.subject),node('span',states[row.state]+' · '+categories[row.category]),node('span',(row.email?row.email+' · ':'')+'Atualizado em '+date(row.updated_at)));b.addEventListener('click',()=>openThread(row.id));el('tickets').append(b);}
  el('list-status').textContent=total?total+' chamado(s) encontrado(s)':el('filter').value?'Nenhum chamado nesta situação.':'Nenhum chamado por enquanto.';
  el('page').textContent=total?`${offset+1}–${Math.min(offset+25,total)} de ${total}`:'';el('previous').disabled=offset===0;el('next').disabled=offset+25>=total;
 }catch(e){if(version===listVersion)el('list-status').textContent=e.message;}
}
function message(m){const box=node('article','');box.className='message';box.dataset.role=m.actor_role;box.append(node('strong',m.actor_role==='admin'?'Equipe Sabino.AI':'Cliente'),node('small',' · '+date(m.created_at)),node('p',m.body));return box;}
async function openThread(id,focus=true){
 if(selected!==id){el('reply-form').reset();replyId=crypto.randomUUID();}
 selected=id;const version=++threadVersion;el('thread').hidden=false;el('thread-status').textContent='Carregando conversa…';el('reply-form').hidden=true;el('state-form').hidden=true;el('older').hidden=true;el('messages').replaceChildren();el('thread-title').textContent='Chamado';el('protocol').textContent='';el('thread-state').textContent='';
 try{const row=await request(scoped(url('/'+id)));if(version!==threadVersion)return;
  el('thread-title').textContent=row.subject;el('protocol').textContent='Protocolo: '+row.id+' · Aberto em '+date(row.created_at);el('thread-state').textContent=states[row.state]+' · '+categories[row.category];
  row.messages.forEach(m=>el('messages').append(message(m)));shown=row.messages.length;messageCount=row.message_count;firstMessage=row.messages[0]?.id;el('older').hidden=shown>=messageCount;
  el('state-form').hidden=!admin;el('state').value=row.state;el('reply-form').hidden=row.state==='resolved';
  el('thread-status').textContent=row.state==='resolved'?'Chamado resolvido. '+(admin?'Você pode reabrir alterando a situação.':'Para um novo problema, abra outro chamado.') : '';
  if(focus){el('thread-title').focus();el('thread').scrollIntoView({behavior:'smooth',block:'start'});}
 }catch(e){if(version===threadVersion)el('thread-status').textContent=e.message;}
}
el('older').addEventListener('click',async()=>{const id=selected,version=threadVersion;el('older').disabled=true;try{const data=await request(scoped(url('/'+id+'/messages?before='+firstMessage)));if(version!==threadVersion)return;const frag=document.createDocumentFragment();data.messages.forEach(m=>frag.append(message(m)));el('messages').prepend(frag);shown+=data.messages.length;firstMessage=data.messages[0]?.id;el('older').hidden=!data.messages.length||shown>=messageCount;}catch(e){el('thread-status').textContent=e.message;}finally{el('older').disabled=false;}});
el('create-form').addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,b=form.querySelector('button'),fields=new FormData(form);b.disabled=true;el('create-status').textContent='Enviando…';try{const row=await request(url(),'POST',{request_id:createId,category:fields.get('category'),subject:fields.get('subject').trim(),body:fields.get('body').trim()});createId=crypto.randomUUID();form.reset();el('create-status').textContent='Chamado criado. Guarde o protocolo: '+row.id;offset=0;el('filter').value='';await loadList();await openThread(row.id);}catch(e){el('create-status').textContent=e.message;}finally{b.disabled=false;}});
el('reply-form').addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,b=form.querySelector('button'),id=selected;const body=form.elements.body.value.trim();if(!body)return;b.disabled=true;el('thread-status').textContent='Enviando…';try{await request(scoped(url('/'+id+'/messages')),'POST',{request_id:replyId,body});replyId=crypto.randomUUID();if(selected===id){form.reset();await openThread(id,false);}await loadList();}catch(e){el('thread-status').textContent=e.message;}finally{b.disabled=false;}});
el('state-form').addEventListener('submit',async event=>{event.preventDefault();const b=event.currentTarget.querySelector('button'),id=selected;b.disabled=true;try{await request(url('/'+id+'/state'),'PATCH',{state:el('state').value});if(selected===id)await openThread(id,false);await loadList();}catch(e){el('thread-status').textContent=e.message;}finally{b.disabled=false;}});
el('filter').addEventListener('change',()=>{offset=0;loadList();});el('refresh').addEventListener('click',loadList);el('previous').addEventListener('click',()=>{offset=Math.max(0,offset-25);loadList();});el('next').addEventListener('click',()=>{offset+=25;loadList();});el('refresh-thread').addEventListener('click',()=>openThread(selected,false));
if(admin){el('title').textContent='Atendimentos';document.title='Atendimentos | Administração Sabino.AI';el('intro').textContent='Acompanhe e responda às solicitações dos clientes.';el('list-title').textContent='Todos os chamados';el('new-ticket').hidden=true;el('admin-back').hidden=false;}
loadList();
})();
