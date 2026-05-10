function showTab(name){
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'))
  document.getElementById('tab-'+name).classList.add('active')
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'))
}