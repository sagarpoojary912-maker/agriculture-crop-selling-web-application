window.addEventListener('load',()=>{
  setTimeout(()=>document.getElementById('loader').classList.add('hidden'),500)
  setTimeout(()=>{document.getElementById('loader').style.display='none'},1200)
})

// Navbar scroll
window.addEventListener('scroll',()=>{
  document.getElementById('navbar').classList.toggle('scrolled',scrollY>50)
})

// Particles
const pc=document.getElementById('particles')
for(let i=0;i<20;i++){
  const p=document.createElement('div')
  p.className='particle'
  p.style.cssText=`left:${Math.random()*100}%;width:${Math.random()*6+2}px;height:${Math.random()*6+2}px;animation-duration:${Math.random()*10+8}s;animation-delay:${Math.random()*10}s`
  pc.appendChild(p)
}

// Scroll reveal
const observer=new IntersectionObserver(entries=>{
  entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add('visible')})
},{threshold:.1})
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el))

// Counter animation
const counters=document.querySelectorAll('.counter')
const countObserver=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      const el=e.target,target=+el.dataset.target
      let cur=0;const step=target/60
      const timer=setInterval(()=>{
        cur=Math.min(cur+step,target)
        el.textContent=Math.floor(cur).toLocaleString('en-IN')+(target>999?'+':'')
        if(cur>=target)clearInterval(timer)
      },25)
      countObserver.unobserve(el)
    }
  })
},{threshold:.5})
counters.forEach(c=>countObserver.observe(c))

// Flash auto-dismiss
document.querySelectorAll('.alert').forEach(a=>{
  setTimeout(()=>a.style.opacity='0',4000)
  setTimeout(()=>a.remove(),4500)
})

// Order modal
let cropPrice=0,cropUnit=''
function openOrder(id,name,price,unit){
  cropPrice=price;cropUnit=unit
  document.getElementById('modalCropId').value=id
  document.getElementById('modalCropName').textContent=name
  document.getElementById('modalCropPrice').textContent='₹'+price.toFixed(2)+' / '+unit
  document.getElementById('modalQty').value=''
  document.getElementById('totalDisplay').textContent='Total: ₹0.00'
  document.getElementById('orderModal').classList.add('open')
}
function closeModal(){document.getElementById('orderModal').classList.remove('open')}
function calcTotal(){
  const qty=parseFloat(document.getElementById('modalQty').value)||0
  document.getElementById('totalDisplay').textContent='Total: ₹'+(qty*cropPrice).toFixed(2)
}
document.getElementById('orderModal').addEventListener('click',e=>{if(e.target===e.currentTarget)closeModal()})

// Category filter
function filterCategory(cat){
  document.getElementById('categoryFilter').value=cat
  searchCrops()
}

// Search
async function searchCrops(){
  const q=document.getElementById('searchInput').value
  const cat=document.getElementById('categoryFilter').value
  const res=await fetch(`/api/crops?search=${encodeURIComponent(q)}&category=${encodeURIComponent(cat)}`)
  const crops=await res.json()
  const grid=document.getElementById('cropsGrid')
  const icons={'Grains':'🌾','Vegetables':'🥦','Fruits':'🍎','Pulses':'🫘','Spices':'🌶️','Oilseeds':'🌻'}
  if(!crops.length){grid.innerHTML='<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--gray)"><div style="font-size:4rem">🌱</div><div>No crops found</div></div>';return}
  grid.innerHTML=crops.map(c=>`
    <div class="crop-card reveal visible">
      <div class="crop-img">${icons[c.category]||'🌿'}<div class="crop-badge">${c.category}</div></div>
      <div class="crop-body">
        <div class="crop-name">${c.name}</div>
        <div class="crop-seller"><i class="fas fa-user-circle"></i> ${c.seller_name} · ${c.location||'India'}</div>
        <div class="crop-meta">
          <div class="crop-price">₹${parseFloat(c.price).toFixed(2)}/${c.unit}</div>
          <div class="crop-qty">${c.quantity} ${c.unit} avail.</div>
        </div>
        <button class="order-btn" onclick="openOrder(${c.id},'${c.name}',${c.price},'${c.unit}')"><i class="fas fa-cart-plus"></i> Order Now</button>
      </div>
    </div>`).join('')
}