'use strict';
// Presentation only: no financial calculations, session commands, or random draws.
function openLinkedSection(){
  const section=location.hash.slice(1);
  if(section==='maker' && document.getElementById('mode')){
    document.getElementById('setup').open=true;
    document.getElementById('mode').value='manual_maker';
    document.getElementById('mode').focus();
  } else if(section){
    const tab=[...document.querySelectorAll('[data-tab]')].find(x=>x.dataset.tab===section);
    if(tab)tab.click();
  }
}
window.addEventListener('hashchange',openLinkedSection);
window.addEventListener('DOMContentLoaded',openLinkedSection);

window.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[role="tablist"]').forEach(group=>{
    group.addEventListener('keydown',event=>{
      const tabs=[...group.querySelectorAll('[role="tab"]')];
      const index=tabs.indexOf(event.target);
      if(index<0)return;
      let next;
      if(event.key==='ArrowRight')next=(index+1)%tabs.length;
      else if(event.key==='ArrowLeft')next=(index+tabs.length-1)%tabs.length;
      else if(event.key==='Home')next=0;
      else if(event.key==='End')next=tabs.length-1;
      else return;
      event.preventDefault();tabs[next].click();tabs[next].focus();
    });
  });
});
