// Design-artifact evidence only; no product runner, provider or storage verification.
import {writeFile} from 'node:fs/promises';
const base=new URL('.',import.meta.url), url='http://127.0.0.1:4179/';
const tabs=await(await fetch('http://127.0.0.1:9229/json/list')).json();
const socket=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>socket.addEventListener('open',r,{once:true}));
let id=0;const requests=new Map(),exceptions=[],observations=[];
socket.addEventListener('message',event=>{const m=JSON.parse(event.data);if(m.method==='Runtime.exceptionThrown')exceptions.push(m.params);if(m.id){const p=requests.get(m.id);requests.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}});
const call=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;requests.set(n,{resolve,reject});socket.send(JSON.stringify({id:n,method,params}));});
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function ready(expression){const start=Date.now();while(!await evaluate(expression)){if(Date.now()-start>45000)throw Error('Timed out '+expression+' '+await evaluate('document.body.innerText'));await pause(50);}}
async function select(id,value){await evaluate(`(()=>{const n=document.getElementById(${JSON.stringify(id)});n.value=${JSON.stringify(value)};n.dispatchEvent(new Event('change',{bubbles:true}));})()`);await pause(100);}
async function text(value){await evaluate(`(()=>{const n=document.querySelector('textarea');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(n,${JSON.stringify(value)});n.dispatchEvent(new Event('input',{bubbles:true}));n.focus();})()`);await pause(100);}
async function enter(){await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',text:'\r',windowsVirtualKeyCode:13});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});}
async function capture(name){
 const metrics=await call('Page.getLayoutMetrics');
 const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:metrics.cssContentSize.width,height:metrics.cssContentSize.height,scale:1}});
 await writeFile(new URL(name+'-apply.png',base),Buffer.from(shot.data,'base64'));
 await writeFile(new URL(name+'-apply.dom.html',base),await evaluate('document.documentElement.outerHTML'));
 const state=await evaluate(`(()=>{const a=document.activeElement,r=document.getElementById('recovery-action');return {url:location.href,theme:document.documentElement.dataset.theme,viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,rootFontSize:getComputedStyle(document.documentElement).fontSize,status:document.querySelector('[role=status]').textContent,error:document.querySelector('[role=alert]')?.innerText,draft:document.querySelector('textarea').value,messages:[...document.querySelectorAll('.message')].map(n=>n.innerText),stored:JSON.parse(localStorage.getItem('kaya-design-fixture:'+new URL(location.href).searchParams.get('thread'))||'null'),focus:{tag:a.tagName,id:a.id,text:a.tagName==='BUTTON'?a.textContent:null},recovery:r?{label:r.textContent,busy:r.getAttribute('aria-disabled'),connected:r.isConnected,sameNode:window.captureAction===r}:null};})()`);
 observations.push({name:name+'-apply',...state});console.log(JSON.stringify({name,status:state.status,focus:state.focus,viewport:state.viewport,documentWidth:state.documentWidth}));
}
async function keyboardRecovery(name,success){
 await evaluate("window.captureAction=document.getElementById('recovery-action');window.captureAction.focus()");await capture(name+'-before');
 await enter();await ready("document.getElementById('recovery-action')?.getAttribute('aria-disabled')==='true'");await capture(name+'-busy');
 await ready("!['Preparing local access…','Restoring saved conversation…'].includes(document.querySelector('[role=status]').textContent)");await capture(name+(success?'-success':'-failure'));
}
await call('Page.enable');await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1200,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url});await ready("!!document.querySelector('textarea')||!!window.kayaPrototype?.loadError");
if(await evaluate('!!window.kayaPrototype?.loadError'))throw Error(await evaluate('window.kayaPrototype.loadError'));
await evaluate("localStorage.clear();sessionStorage.clear()");await call('Page.navigate',{url});await ready("document.querySelector('[role=status]')?.textContent==='Ready to send'");
await select('review-theme','light');await text('First successful exchange');await enter();await ready("document.querySelector('[role=status]').textContent.includes('Exchange saved')");await capture('12-light-first-saved');
for(const scenario of ['stale','partial','mismatch','order']){
 await select('send-scenario',scenario);await text('Current turn '+scenario);await enter();await ready("document.querySelector('[role=alert]')?.textContent.includes('Save not confirmed')");await capture('13-light-'+scenario);
 await select('recovery-result','stored');await keyboardRecovery('14-light-'+scenario+'-check',false);
 await select('recovery-result','complete');await keyboardRecovery('15-light-'+scenario+'-check',true);
}
for(const theme of ['light','dark']){
 await select('review-theme',theme);await select('review-text','200');await call('Emulation.setDeviceMetricsOverride',{width:320,height:1000,deviceScaleFactor:1,mobile:false});
 for(const scenario of ['database','provider','auth','network']){
  await select('send-scenario',scenario);await text('Narrow enlarged '+theme+' '+scenario);await enter();await ready("document.querySelector('[role=alert]')!==null && document.querySelector('[role=status]').textContent==='Exchange not complete'");await capture('16-'+theme+'-320-200-'+scenario);
  if(scenario==='database'||scenario==='auth'){
   await select('recovery-result','failure');await keyboardRecovery('17-'+theme+'-320-200-'+scenario,false);
   await select('recovery-result','complete');await keyboardRecovery('18-'+theme+'-320-200-'+scenario,true);
  }
 }
 // Reopen error in each theme, followed by keyboard failure and success.
 await select('restore-scenario','database');await call('Page.reload');await ready("document.querySelector('[role=alert]')?.textContent.includes('Could not restore')");await select('review-text','200');await capture('19-'+theme+'-320-200-restore');
 await keyboardRecovery('20-'+theme+'-320-200-restore',false);
 await select('restore-scenario','success');await keyboardRecovery('21-'+theme+'-320-200-restore',true);
}
await writeFile(new URL('rendered-evidence-apply.json',base),JSON.stringify({capturedAt:new Date().toISOString(),url,browser:await call('Browser.getVersion'),exceptions,observations},null,2)+'\n');
await call('Browser.close');socket.close();
