function selectRole(r){
  document.getElementById('roleInput').value=r
  document.getElementById('sellerBtn').classList.toggle('active',r==='seller')
  document.getElementById('buyerBtn').classList.toggle('active',r==='buyer')
}
// Pre-select from URL param
const params=new URLSearchParams(location.search)
if(params.get('role')==='seller')selectRole('seller')