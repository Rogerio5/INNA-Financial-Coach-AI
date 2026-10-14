(() => {
  'use strict';
  const root = document.getElementById('sabino-onboarding');
  if (!root) return;
  const definitions = {
    account_reviewed: ['Confira sua conta', 'Revise seu nome e seus dados de acesso.', '/minha-conta', 'Abrir minha conta', 'Já conferi minha conta'],
    platforms_explored: ['Conheça as plataformas', 'Veja o que está disponível na Sabino.AI.', '/modulos', 'Explorar plataformas', 'Já conheci as plataformas'],
    inna_analysis: ['Faça sua primeira análise', 'Converse com a INNA. Confira o custo antes de confirmar uma análise.', '/inna', 'Abrir a INNA']
  };
  function node(tag, text) { const element = document.createElement(tag); if (text) element.textContent = text; return element; }
  async function request(options) {
    const response = await fetch('/api/sabino/onboarding', {credentials:'same-origin', cache:'no-store', ...options});
    if (!response.ok) throw new Error(response.status === 401 ? 'Entre novamente para ver seus primeiros passos.' : 'Não foi possível carregar ou salvar seu progresso.');
    return response.json();
  }
  async function load() {
    root.replaceChildren(node('p', 'Carregando seus primeiros passos…'));
    try { render(await request()); }
    catch (error) {
      const message = node('p', error.message); message.setAttribute('role', 'status');
      const retry = node('button', 'Tentar novamente'); retry.type='button'; retry.addEventListener('click', load);
      root.replaceChildren(message, retry);
    }
  }
  function render(data) {
    const title = node('h2', 'Primeiros passos na Sabino.AI');
    const summary = node('p', `${data.completed} de ${data.total} passos concluídos`);
    const meter = node('progress'); meter.max=data.total; meter.value=data.completed; meter.setAttribute('aria-label',summary.textContent);
    const steps=node('div'); steps.className='sb-steps';
    const feedback=node('p'); feedback.setAttribute('role','status'); feedback.setAttribute('aria-live','polite');
    data.steps.forEach((step,index)=>{
      const definition=definitions[step.id]; if (!definition) return;
      const card=node('article'); card.dataset.complete=String(step.completed);
      card.append(node('span', step.completed?'✓ Concluído':`Passo ${index+1}`),node('h3',definition[0]),node('p',definition[1]));
      const actions=node('div');actions.className='sb-actions';const link=node('a',definition[3]);link.href=definition[2];actions.append(link);
      if (definition[4] && !step.completed) {
        const button=node('button',definition[4]);button.type='button';
        button.addEventListener('click',async()=>{
          button.disabled=true;
          try {await request({method:'POST',headers:{'Content-Type':'application/json','X-Sabino-Onboarding':'1'},body:JSON.stringify({step:step.id})});await load();}
          catch(error){feedback.textContent=error.message;button.disabled=false;}
        }); actions.append(button);
      }
      card.append(actions);
      const note=node('p',step.id==='inna_analysis'?(data.analysis_available?'Conclusão confirmada automaticamente após uma análise bem-sucedida.':'A verificação das análises está indisponível no momento.'):'Conclusão informada por você.');note.className='sb-meta';card.append(note);steps.append(card);
    });
    root.replaceChildren(title,summary,meter,steps,feedback);
    const refresh=node('button','Atualizar progresso');refresh.type='button';refresh.addEventListener('click',load);root.append(refresh);
    if(data.is_admin){const admin=node('a','Acompanhar participantes →');admin.href='/admin/primeiros-passos';const actions=node('div');actions.className='sb-actions';actions.append(admin);root.append(actions);}
  }
  load();
})();
