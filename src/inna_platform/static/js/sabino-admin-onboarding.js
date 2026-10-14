(() => {
 'use strict';
 const byId=id=>document.getElementById(id), list=byId('participants'), status=byId('status');
 const names={account_reviewed:'Conferir a conta',platforms_explored:'Conhecer as plataformas',inna_analysis:'Concluir a primeira análise com a INNA'};
 const labels={active:'Ativos · últimos 7 dias',not_started:'Não começaram',inactive:'Sem atividade recente',help:'Com dificuldade',withdrawn:'Desistência confirmada',blocked:'Impedimento registrado',account_inactive:'Conta inativa',unknown:'Dados indisponíveis'};
 const colors={active:'#85cba0',not_started:'#91b4ed',inactive:'#bdad88',help:'#f4ca64',withdrawn:'#e99c92',blocked:'#c6a0df',account_inactive:'#a3aab5',unknown:'#e1e3e7'};
 const reasons={difficulty:'Dificuldade de uso',technical:'Problema técnico',time:'Falta de tempo',price:'Preço',access:'Impedimento de acesso',other:'Outro motivo',resolved:'Acompanhamento resolvido'};
 let offset=0,total=0,generation=0,appliedSearch='',appliedSituation='all';
 function text(tag,value){const el=document.createElement(tag);el.textContent=value;return el;}
 function date(value){return value?new Date(value).toLocaleString('pt-BR'):'Sem registro';}
 function button(label,fn){const el=text('button',label);el.type='button';el.addEventListener('click',fn);return el;}
 function select(options,value){const el=document.createElement('select');Object.entries(options).forEach(([key,label])=>{const option=text('option',label);option.value=key;el.append(option);});el.value=value;return el;}
 function field(label,control){const el=text('label',label);el.append(control);return el;}
 function renderSummary(summary){
   byId('overview').hidden=false;byId('metrics').replaceChildren();
   [['Participantes',summary.total],['Ativos · 7 dias',summary.situations.active],['Com dificuldade',summary.situations.help],['Primeiros passos concluídos',summary.completed],['Com plano pago ativo',summary.paid_plan]].forEach(([label,value])=>{const metric=document.createElement('div');metric.append(text('span',label),text('strong',String(value)));byId('metrics').append(metric);});
   const donut=byId('donut');donut.replaceChildren();const ring=document.createElement('div');ring.className='sb-ring';
   let angle=0;const slices=[];
   Object.entries(labels).forEach(([key])=>{const end=angle+(summary.total?summary.situations[key]/summary.total*360:0);if(end>angle)slices.push(`${colors[key]} ${angle}deg ${end}deg`);angle=end;});
   ring.style.background=slices.length?`conic-gradient(${slices.join(',')})`:'#34362f';
   ring.setAttribute('role','img');ring.setAttribute('aria-label',summary.total?Object.entries(labels).map(([key,label])=>`${label}: ${summary.situations[key]}`).join('; '):'Nenhum participante');
   const center=document.createElement('div');center.append(text('strong',String(summary.total)),text('span','participantes'));ring.append(center);donut.append(ring);
   const legend=byId('legend');legend.replaceChildren();
   Object.entries(labels).forEach(([key,label])=>{const row=button('',()=>{byId('filter').value=key;apply();});row.className='sb-legend-item';const dot=text('span','●');dot.style.color=colors[key];dot.setAttribute('aria-hidden','true');row.append(dot,text('span',label),text('strong',String(summary.situations[key])));row.setAttribute('aria-label',`${label}: ${summary.situations[key]}. Filtrar lista`);legend.append(row);});
   const bars=byId('reasons');bars.replaceChildren();const entries=Object.entries(summary.reasons).filter(([,count])=>count>0).sort((a,b)=>b[1]-a[1]);const max=Math.max(1,...entries.map(([,count])=>count));
   entries.forEach(([key,count])=>{const item=document.createElement('div');item.className='sb-bar-item';const caption=document.createElement('div');caption.append(text('span',reasons[key]||'Outro motivo'),text('strong',String(count)));const track=document.createElement('div');track.className='sb-bar-track';track.setAttribute('aria-hidden','true');const fill=document.createElement('div');fill.style.width=`${count/max*100}%`;track.append(fill);item.append(caption,track);bars.append(item);});
   if(!entries.length)bars.append(text('p','Nenhum motivo registrado.'));
   byId('updated').textContent=`Resumo de todos os participantes · ${date(summary.as_of)}. Os filtros abaixo alteram somente a lista.`;
 }
 function editor(row){
   const details=document.createElement('details');details.className='sb-editor';details.append(text('summary','Registrar acompanhamento'));
   const form=document.createElement('form');const situation=select({normal:'Situação automática / resolvido',help:'Com dificuldade',withdrawn:'Desistência confirmada',blocked:'Impedimento registrado'},row.followup_situation||'normal');const reason=select(reasons,row.followup?.reason||'resolved');
   const note=document.createElement('textarea');note.maxLength=1000;note.rows=3;note.value=row.followup?.note||'';
   const feedback=text('p','');feedback.setAttribute('role','status');
   situation.addEventListener('change',()=>{reason.value=situation.value==='normal'?'resolved':'difficulty';});
   const save=text('button','Salvar acompanhamento');save.type='submit';
   form.append(field('Situação informada',situation),field('Motivo',reason),field('Observação / como a situação foi confirmada',note),text('p','Registre apenas o necessário. Um impedimento informado aqui não bloqueia o acesso. Desistência e impedimento exigem uma observação.'),save,feedback);
   form.addEventListener('submit',async event=>{event.preventDefault();save.disabled=true;feedback.textContent='Salvando…';
     try{const response=await fetch('/api/sabino/admin/onboarding/followup',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Sabino-Onboarding':'1'},body:JSON.stringify({user_id:row.user_id,situation:situation.value,reason:reason.value,note:note.value.trim()})});
       if(!response.ok)throw new Error(response.status===422?'Confira o motivo e preencha a observação (mínimo de 5 caracteres quando exigida).':'Não foi possível salvar o acompanhamento.');offset=0;await load();
     }catch(error){feedback.textContent=error.message;save.disabled=false;}
   });details.append(form);return details;
 }
 function renderRows(rows){
   list.replaceChildren();rows.forEach(row=>{const article=document.createElement('article');article.className='sb-participant';article.dataset.state=row.situation;
     article.append(text('h2',row.email),text('p',`${labels[row.situation]} · ${row.completed}/${row.total} passos`),text('p',`Próximo passo: ${names[row.next_step]||'Jornada inicial concluída'}`),text('p',`Última atividade registrada: ${date(row.last_activity_at)}`));
     if(row.followup){article.append(text('p',`Acompanhamento: ${reasons[row.followup.reason]} · ${date(row.followup.created_at)}`));if(row.followup.note)article.append(text('p',row.followup.note));}
     article.append(editor(row));list.append(article);
   });
   if(!rows.length)list.append(text('p','Nenhum participante corresponde aos filtros.'));
   byId('page').textContent=total?`${offset+1}–${Math.min(offset+50,total)} de ${total} encontrados`:'Nenhum participante';byId('previous').disabled=offset===0;byId('next').disabled=offset+50>=total;
 }
 async function load(){
   const version=++generation;status.textContent='Carregando participantes…';byId('page').textContent='';list.replaceChildren();byId('overview').hidden=true;byId('previous').disabled=true;byId('next').disabled=true;
   try{const query=new URLSearchParams({offset:String(offset),limit:'50',situation:appliedSituation,search:appliedSearch});const response=await fetch(`/api/sabino/admin/onboarding?${query}`,{credentials:'same-origin',cache:'no-store'});
     if(!response.ok)throw new Error(response.status===403?'Acesso restrito à administração da Sabino.AI.':response.status===401?'Sua sessão expirou. Entre novamente.':'Não foi possível consultar o acompanhamento. Tente novamente.');
     const data=await response.json();if(version!==generation)return;if(!data.pilot_available){
       total=0;byId('page').textContent='';
       status.textContent='Acompanhamento do piloto ainda não disponível';
       const notice=document.createElement('article');notice.className='sb-participant';
       notice.append(text('h2','Prepare a entrada dos participantes'),text('p','O registro do piloto ainda não foi inicializado. Por isso, os totais e os gráficos não são exibidos.'),text('p','Isso não significa que a Sabino.AI não tenha contas cadastradas. Este painel acompanha somente quem ativou o piloto.'),text('p','Próxima etapa: configurar a entrada no piloto. Depois, use Atualizar para consultar os participantes.'));
       list.replaceChildren(notice);return;
     }
     total=data.total;renderSummary(data.summary);renderRows(data.participants);
     if(data.summary.total===0){
       status.textContent='Nenhuma ativação do piloto registrada';
       list.replaceChildren(text('p','Os participantes aparecerão aqui após ativarem o piloto. Os gráficos serão preenchidos com os dados reais de acompanhamento.'));
     }else{status.textContent=total===1?'1 participante encontrado':total+' participantes encontrados';}
   }catch(error){if(version!==generation)return;total=0;list.replaceChildren();byId('overview').hidden=true;byId('page').textContent='';status.textContent=error.message;}
 }
 function apply(){appliedSearch=byId('search').value;appliedSituation=byId('filter').value;offset=0;load();}
 byId('filters').addEventListener('submit',event=>{event.preventDefault();apply();});byId('reload').addEventListener('click',load);byId('previous').addEventListener('click',()=>{offset=Math.max(0,offset-50);load();});byId('next').addEventListener('click',()=>{offset+=50;load();});load();
})();
