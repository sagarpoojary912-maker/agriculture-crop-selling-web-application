const crops = [
  {name:'Basmati Rice',icon:'🌾',cat:'Grains',price:85,seller:'Ramesh Kumar, Punjab',badge:'Organic',rating:'★★★★★'},
  {name:'Baby Carrots',icon:'🥕',cat:'Vegetables',price:42,seller:'Gupta Farms, Rajasthan',badge:'Fresh',rating:'★★★★★'},
  {name:'Cherry Tomatoes',icon:'🍅',cat:'Vegetables',price:55,seller:'Singh Farm, Punjab',badge:'Fresh',rating:'★★★★★'},
  {name:'Red Onions',icon:'🧅',cat:'Vegetables',price:18,seller:'Patil Farm, Maharashtra',badge:'Bulk',rating:'★★★★☆'},
  {name:'Green Chillies',icon:'🌶️',cat:'Spices',price:120,seller:'Rao Farm, Andhra',badge:'Organic',rating:'★★★★★'},
  {name:'Sona Masoori Rice',icon:'🍚',cat:'Grains',price:62,seller:'Rao Agro, Andhra',badge:'Premium',rating:'★★★★☆'},
  {name:'Sweet Corn',icon:'🌽',cat:'Vegetables',price:24,seller:'Kumar Farm, UP',badge:'Fresh',rating:'★★★★☆'},
  {name:'Alphonso Mango',icon:'🥭',cat:'Fruits',price:180,seller:'Devgad Farms, MH',badge:'GI Tagged',rating:'★★★★★'},
];
const wishlist = [crops[0], crops[4], crops[7]];

function renderCrops(list, containerId) {
  const g = document.getElementById(containerId);
  g.innerHTML = '';
  list.forEach(c => {
    g.innerHTML += `
      <div class="crop-card">
        <div class="crop-img"><span class="crop-badge2">${c.badge}</span>${c.icon}</div>
        <div class="crop-body">
          <h3>${c.name}</h3>
          <div class="crop-meta2"><span>🧑‍🌾 ${c.seller}</span><span>${c.rating}</span></div>
          <div class="crop-footer2">
            <div class="price2">₹${c.price} <small>/kg</small></div>
            <button class="buy-btn2" onclick="openPayment('${c.name}',${c.price})">Buy Now</button>
          </div>
        </div>
      </div>`;
  });
}
renderCrops(crops, 'cropsGrid');
renderCrops(wishlist, 'wishlistGrid');

function filterCrops() {
  const q = document.getElementById('searchInput').value.toLowerCase();
  const cat = document.getElementById('catFilter').value;
  const filtered = crops.filter(c => (!q || c.name.toLowerCase().includes(q)) && (!cat || c.cat === cat));
  renderCrops(filtered, 'cropsGrid');
}

function openPayment(name, price) {
  const qty = 100;
  const total = price * qty;
  const fee = Math.round(total * 0.02);
  document.getElementById('payModalCrop').textContent = `${name} — ${qty}kg`;
  document.getElementById('osCropPrice').textContent = '₹' + total.toLocaleString();
  document.getElementById('osFee').textContent = '₹' + fee;
  document.getElementById('osTotal').textContent = '₹' + (total + fee).toLocaleString();
  document.getElementById('payModal').classList.add('open');
}

let selPayMethod = 'upi';
function selectPayMethod(m, el) {
  selPayMethod = m;
  document.querySelectorAll('.pay-method').forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  document.querySelectorAll('.pay-section').forEach(s => s.classList.remove('active'));
  document.getElementById('pay-'+m).classList.add('active');
}

function processPayment() {
  if(selPayMethod==='upi' && !document.getElementById('upiId').value) { alert('Please enter your UPI ID'); return; }
  document.getElementById('payModal').classList.remove('open');
  setTimeout(() => document.getElementById('successOverlay').classList.add('open'), 300);
}

function formatCard(input) {
  let v = input.value.replace(/\s+/g,'').replace(/[^0-9]/gi,'');
  let matches = v.match(/\d{4,16}/g);
  let match = matches && matches[0] || '';
  let parts = [];
  for(let i=0,len=match.length;i<len;i+=4) parts.push(match.substring(i,i+4));
  input.value = parts.length ? parts.join(' ') : v;
}

const titles = {dashboard:'Buyer Dashboard',browse:'Browse Crops',orders:'My Orders',wishlist:'My Wishlist',profile:'My Profile'};
function showPage(id, btn) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-'+id).classList.add('active');
  document.getElementById('pageTitle').textContent = titles[id];
  if(btn) { document.querySelectorAll('.sb-link').forEach(l => l.classList.remove('active')); btn.classList.add('active'); }
}