function showTab(n){
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'))
  document.getElementById('tab-'+n).classList.add('active')
  document.querySelectorAll('.nav-item').forEach(i=>i.classList.remove('active'))
  event.target.closest('.nav-item').classList.add('active')
}
function filterTable(input,tableId){
  const q=input.value.toLowerCase()
  document.querySelectorAll('#'+tableId+' tr:not(:first-child)').forEach(row=>{
    row.style.display=row.textContent.toLowerCase().includes(q)?'':'none'
  })
}