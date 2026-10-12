const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(require('path').resolve(__dirname,'../../../src/inna_platform/static/js/sabino-paid-analysis.js'),'utf8').replace('export async function askPaid','async function askPaid');
const payload={pergunta:'Como organizar meu orçamento?',idioma:'pt-BR',top_k:4};
function setup(handler){
 const storage=new Map(), events=[], calls=[];
 const element=()=>({style:{},append(){},remove(){},close(){},focus(){},setAttribute(){},showModal(){queueMicrotask(()=>this.accept.onclick());}});
 const document={readyState:'loading',addEventListener(){},getElementById(){return null;},querySelector(){return null;},body:{append(){}},createElement(){const el=element();el.append=(...args)=>{el.accept=args.at(-1);};return el;}};
 const context=vm.createContext({document,crypto:require('crypto').webcrypto,TextEncoder,Uint8Array,AbortController,CustomEvent:class{constructor(name){this.type=name}},window:{dispatchEvent:e=>events.push(e.type)},sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},setTimeout:(fn,ms)=>setTimeout(fn,ms===2000?0:ms),clearTimeout,fetch:async(url,init)=>{calls.push({url,init});const result=await handler(url,init);return new Response(JSON.stringify(result.body),{status:result.status||200});}});
 vm.runInContext(source,context);return {ask:p=>context.askPaid(p),storage,calls,events};
}
const done={billing:{state:'completed'},resposta:'Resposta válida'};
const quote=state=>({body:{quote_id:'q',state,cost:5}});
(async()=>{
 let executions=0,state='quoted';
 let s=setup(async url=>{if(url.endsWith('/quote'))return quote(state);if(url.endsWith('/wallet'))return {body:{balance:10}};if(url.endsWith('/ask')){executions++;state='completed';return {body:done};}return {body:done};});
 assert.equal((await (await s.ask(payload)).json()).resposta,'Resposta válida');
 await s.ask(payload);assert.equal(executions,1);assert.equal(s.storage.size,1);
 assert.equal(s.calls.filter(x=>x.url.endsWith('/ask')).length,1);
 // A concurrent click cannot reserve a second analysis.
 let release;const gate=new Promise(r=>release=r);
 s=setup(async url=>{if(url.endsWith('/quote')){await gate;return quote('completed');}return {body:done};});
 const first=s.ask(payload);await assert.rejects(s.ask(payload),/andamento/);release();await first;
 // Lost POST response is recovered via GET, never another POST.
 s=setup(async url=>{if(url.endsWith('/quote'))return quote('quoted');if(url.endsWith('/wallet'))return {body:{balance:10}};if(url.endsWith('/ask'))throw Error('connection lost');return {body:done};});
 await s.ask(payload);assert.equal(s.calls.filter(x=>x.url.endsWith('/ask')).length,1);assert.equal(s.storage.size,1);
 // Refund permits a future explicitly confirmed attempt.
 s=setup(async url=>url.endsWith('/quote')?quote('refunded'):{status:422,body:{billing:{state:'refunded'},detail:'Créditos devolvidos'}});
 assert.equal((await s.ask(payload)).status,422);assert.equal(s.storage.size,0);assert.equal(s.events.length,1);
 // Unknown result stays linked and cannot silently become a fresh request.
 s=setup(async url=>url.endsWith('/quote')?quote('needs_review'):{status:202,body:{billing:{state:'needs_review'},detail:'Aguardando conferência'}});
 await assert.rejects(s.ask(payload),/conferência/);assert.equal(s.storage.size,1);
 // Running analysis is only polled and completes without a POST.
 let polls=0;s=setup(async url=>url.endsWith('/quote')?quote('running'):++polls<2?{status:202,body:{billing:{state:'running'}}}:{body:done});
 await s.ask(payload);assert.equal(polls,2);assert.equal(s.calls.some(x=>x.url.endsWith('/ask')),false);
 // Insufficient balance does not execute.
 s=setup(async url=>url.endsWith('/quote')?quote('quoted'):{body:{balance:0}});
 await assert.rejects(s.ask(payload),/Saldo insuficiente/);assert.equal(s.calls.some(x=>x.url.endsWith('/ask')),false);
 // Expired quote is replaced only after explicit server rejection.
 s=setup(async url=>url.endsWith('/quote')?quote('quoted'):url.endsWith('/wallet')?{body:{balance:10}}:{status:409,body:{detail:'Orçamento expirado'}});
 await s.ask(payload);assert.equal(s.storage.size,0);
 console.log('8 frontend billing scenarios passed');
})().catch(e=>{console.error(e);process.exitCode=1;});
