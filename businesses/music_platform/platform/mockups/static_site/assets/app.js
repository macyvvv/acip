
document.querySelectorAll('[data-disabled]').forEach(el=>{el.setAttribute('aria-disabled','true');el.addEventListener('click',e=>{e.preventDefault();showToast('この操作は現在利用できません。状態を確認してからもう一度試してください。')})});
document.querySelectorAll('.help').forEach(el=>{el.addEventListener('click',e=>{e.stopPropagation();const on=el.getAttribute('aria-expanded')==='true';document.querySelectorAll('.help[aria-expanded="true"]').forEach(o=>{if(o!==el)o.setAttribute('aria-expanded','false')});el.setAttribute('aria-expanded',String(!on))})});
document.addEventListener('click',()=>document.querySelectorAll('.help[aria-expanded="true"]').forEach(el=>el.setAttribute('aria-expanded','false')));
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.querySelectorAll('.modal[open]').forEach(m=>m.removeAttribute('open'));document.querySelectorAll('.help[aria-expanded="true"]').forEach(el=>el.setAttribute('aria-expanded','false'))}});
document.querySelectorAll('[data-modal]').forEach(btn=>btn.addEventListener('click',e=>{e.preventDefault();const m=document.getElementById(btn.dataset.modal);if(m)m.setAttribute('open','')}));
document.querySelectorAll('[data-close-modal]').forEach(btn=>btn.addEventListener('click',()=>btn.closest('.modal')?.removeAttribute('open')));
document.querySelectorAll('[data-toast]').forEach(btn=>btn.addEventListener('click',e=>{e.preventDefault();showToast(btn.dataset.toast)}));
function showToast(text){let t=document.querySelector('.toast');if(!t){t=document.createElement('div');t.className='toast';document.body.appendChild(t)}t.textContent=text;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2600)}
