// Design-artifact capture only. Uses installed Chrome + Node's built-in WebSocket.
// Not a product runner, SDK test, provider probe or UAT certification.
import {writeFile} from 'node:fs/promises';
const base = new URL('.', import.meta.url);
const tabs = await (await fetch('http://127.0.0.1:9228/json/list')).json();
const tab = tabs.find(tab => tab.type === 'page');
const socket = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise(resolve => socket.addEventListener('open', resolve, {once:true}));
let id = 0;
const pending = new Map(), browserErrors = [];
socket.addEventListener('message', event => {
 const message = JSON.parse(event.data);
 if(message.method === 'Runtime.exceptionThrown') browserErrors.push(message.params.exceptionDetails);
 if(message.id) {
  const promise = pending.get(message.id); pending.delete(message.id);
  message.error ? promise.reject(message.error) : promise.resolve(message.result);
 }
});
const call = (method, params={}) => new Promise((resolve,reject) => {
 const current=++id; pending.set(current,{resolve,reject}); socket.send(JSON.stringify({id:current,method,params}));
});
const evaluate = async expression => {
 const result=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
 if(result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
 return result.result.value;
};
const pause = ms => new Promise(resolve=>setTimeout(resolve,ms));
const ready = async condition => {
 const started=Date.now();
 while(!await evaluate(condition)) {
  if(Date.now()-started>45000) throw new Error('Capture wait timed out: '+condition+'; '+await evaluate('document.body.innerText'));
  await pause(100);
 }
};
await call('Page.enable'); await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1200,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:4178/'});
await ready("!!document.querySelector('textarea') || !!window.kayaPrototype?.loadError");
const substrate=await evaluate('window.kayaPrototype');
if(substrate?.loadError) throw new Error('Astryx CDN load failed: '+substrate.loadError);
await ready("document.querySelector('[role=status]').textContent.includes('Ready to send')");
const observations=[];
async function capture(name){
 const metrics = await call('Page.getLayoutMetrics');
 const screenshot = await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:metrics.cssContentSize.width,height:metrics.cssContentSize.height,scale:1}});
 await writeFile(new URL(name+'.png',base),Buffer.from(screenshot.data,'base64'));
 await writeFile(new URL(name+'.dom.html',base),await evaluate('document.documentElement.outerHTML'));
 const observation = await evaluate(`(() => {
  const style=selector=>{const element=document.querySelector(selector);if(!element)return null;const value=getComputedStyle(element);return {color:value.color,background:value.backgroundColor,fontSize:value.fontSize,lineHeight:value.lineHeight,border:value.borderColor};};
  return {url:location.href,viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,rootFontSize:getComputedStyle(document.documentElement).fontSize,theme:document.documentElement.dataset.theme,mainCount:document.querySelectorAll('main').length,h1:document.querySelector('h1')?.textContent,status:document.querySelector('[role=status]')?.textContent,error:document.querySelector('[role=alert]')?.textContent||null,messages:[...document.querySelectorAll('.message')].map(node=>node.innerText),activeElement:document.activeElement?.tagName,styles:{body:style('body'),surface:style('.conversation'),transcriptText:style('.message .body'),muted:style('.muted'),status:style('.status'),textarea:style('textarea'),send:style('button[type=submit]'),error:style('.error'),errorText:style('.error p'),link:style('.thread a')},substrate:window.kayaPrototype};
 })()`);
 observations.push({name,...observation}); console.log(JSON.stringify({name,status:observation.status,viewport:observation.viewport,documentWidth:observation.documentWidth}));
}
async function select(id,value){await evaluate(`(() => {const node=document.getElementById(${JSON.stringify(id)});node.value=${JSON.stringify(value)};node.dispatchEvent(new Event('change',{bubbles:true}));})()`);await pause(100);}
async function enter(text){await evaluate(`(() => {const node=document.querySelector('textarea');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(node,${JSON.stringify(text)});node.dispatchEvent(new Event('input',{bubbles:true}));node.focus();})()`);await pause(100);}
async function click(label){await evaluate(`[...document.querySelectorAll('button')].find(node=>node.textContent===${JSON.stringify(label)}).click()`);}
await select('review-theme','light');await capture('01-light-empty');
await enter('Hello Kaya — design review nonce 2026-10-05');
await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
await ready("document.querySelector('[role=status]').textContent.includes('Waiting')");await capture('02-light-pending');
await ready("document.querySelector('[role=status]').textContent.includes('Exchange saved')");await capture('03-light-saved');
await select('review-theme','dark');await call('Page.reload');
await ready("document.querySelector('[role=status]')?.textContent.includes('Conversation restored')");await capture('04-dark-restored');
await select('send-scenario','database');await enter('Show the database confirmation failure');await click('Send');
await ready("document.querySelector('[role=alert]')?.textContent.includes('Save not confirmed')");await capture('05-dark-database-error');
await select('send-scenario','provider');await enter('Show a provider error');await click('Send');
await ready("document.querySelector('[role=alert]')?.textContent.includes('Reply unavailable')");await capture('06-dark-provider-error');
await select('send-scenario','auth');await enter('Show expired local access');await click('Send');
await ready("document.querySelector('[role=alert]')?.textContent.includes('Local access expired')");await capture('07-dark-auth-error');
await click('Renew local access');await ready("document.querySelector('[role=status]').textContent.includes('Ready to send')");
await select('restore-scenario','database');await call('Page.reload');
await ready("document.querySelector('[role=alert]')?.textContent.includes('Could not restore')");await capture('08-dark-restore-error');
await select('restore-scenario','success');await click('Retry restoration');
await ready("document.querySelector('[role=status]').textContent.includes('Conversation restored')");
await select('review-theme','light');await call('Emulation.setDeviceMetricsOverride',{width:320,height:1000,deviceScaleFactor:1,mobile:false});
await capture('09-light-320');await select('review-text','200');await capture('10-light-320-200percent');
await select('review-theme','dark');await capture('11-dark-320-200percent');
function luminance(rgb) {
 const values=rgb.match(/[\d.]+/g).slice(0,3).map(Number).map(value=>value/255).map(value=>value<=.04045?value/12.92:((value+.055)/1.055)**2.4);
 return values[0]*.2126+values[1]*.7152+values[2]*.0722;
}
function ratio(a,b) {const x=luminance(a),y=luminance(b);return Number(((Math.max(x,y)+.05)/(Math.min(x,y)+.05)).toFixed(2));}
const contrast=observations.map(({name,styles:s})=>({name,body:ratio(s.body.color,s.body.background),mutedOnPage:ratio(s.muted.color,s.body.background),mutedOnSurface:ratio(s.muted.color,s.surface.background),statusOnSurface:ratio(s.status.color,s.surface.background),transcript:s.transcriptText?ratio(s.transcriptText.color,s.surface.background):null,textareaBorder:ratio(s.textarea.border,s.textarea.background),link:s.link?ratio(s.link.color,s.surface.background):null,error:s.errorText?ratio(s.errorText.color,s.error.background):null}));
await writeFile(new URL('contrast-evidence.json',base),JSON.stringify(contrast,null,2)+'\n');
await writeFile(new URL('rendered-evidence.json',base),JSON.stringify({capturedAt:new Date().toISOString(),url:'http://127.0.0.1:4178/',browserVersion:await call('Browser.getVersion'),browserErrors,observations},null,2)+'\n');
socket.close();
