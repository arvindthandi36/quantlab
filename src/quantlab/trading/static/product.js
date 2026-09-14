/* Product presentation only. Financial values and grading remain in existing Python APIs. */
(()=>{'use strict';
const groups=[...document.querySelectorAll('.ql-nav-group')];
for(const group of groups){
 group.addEventListener('toggle',()=>{if(group.open)for(const other of groups)if(other!==group)other.open=false;});
 group.addEventListener('keydown',event=>{if(event.key==='Escape'){group.open=false;group.querySelector('summary').focus();}});
}
document.addEventListener('click',event=>{if(!event.target.closest('.ql-nav-group'))for(const group of groups)group.open=false;});
// Align the currency sign convention without parsing or rounding the value.
function currencyText(node){
 if(node.nodeType===Node.TEXT_NODE){
  if(!node.parentElement?.closest('script,style,pre,code,textarea')&&node.nodeValue.includes('£-'))node.nodeValue=node.nodeValue.replaceAll('£-','-£');
 }else if(node.nodeType===Node.ELEMENT_NODE&&!node.matches('script,style,pre,code,textarea')){
  for(const child of node.childNodes)currencyText(child);
 }
}
currencyText(document.body);
new MutationObserver(records=>{for(const r of records){if(r.type==='characterData')currencyText(r.target);else for(const node of r.addedNodes)currencyText(node);}}).observe(document.body,{childList:true,subtree:true,characterData:true});
// Give existing chart containers an adjacent readable route to their source values.
for(const canvas of document.querySelectorAll('canvas[aria-label]')){
 const note=document.createElement('p');note.className='ql-chart-alternative';
 note.textContent=canvas.getAttribute('aria-label')+'. Exact current values and records are in the adjacent metrics, tables or report.';
 canvas.after(note);
}
})();
