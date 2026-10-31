'use strict';
const data = window.RFM_DATA;
const $ = id => document.getElementById(id);
const euro = cents => new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(cents/100);
const esc = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let page=0, filtered=[]; const size=12;
if(!data){$('status').textContent='Dataset missing. Run python scripts/build.py --synthetic first.'; throw new Error('Missing data.js');}
for(const s of data.segments){const o=new Option(s.segment,s.segment);$('segment').add(o);}
for(const c of [...new Set(data.customers.map(c=>c.country))].sort())$('country').add(new Option(c,c));
$('period').textContent=`${data.start} to ${data.as_of} (end exclusive)`;
$('data-label').textContent=data.synthetic?'FICTIONAL RETAIL DATA':'CUSTOM DATA — VERIFY PERMISSION BEFORE SHARING';
$('thresholds').textContent=JSON.stringify(data.thresholds,null,2);
const q=data.quality;
$('quality').textContent=`${q.input_orders.toLocaleString()} input orders. ${q.eligible_orders.toLocaleString()} eligible, ${q.cancelled} cancelled, ${q.fully_refunded} fully refunded or zero-net, ${q.outside_window} outside window. ${q.partial_refunds} eligible orders have partial refunds.`;
const maxMonth=Math.max(...data.monthly.map(m=>m.net_cents),1);
$('monthly').innerHTML=data.monthly.map(m=>`<div class="month" title="${m.month}: ${euro(m.net_cents)}"><div class="column" style="height:${Math.round(m.net_cents/maxMonth*140)}px"></div><span>${m.month.slice(2)}</span></div>`).join('');
$('monthly-data').innerHTML='<table><thead><tr><th>Month</th><th>Net sales</th><th>Orders</th></tr></thead><tbody>'+data.monthly.map(m=>`<tr><td>${m.month}</td><td>${euro(m.net_cents)}</td><td>${m.orders}</td></tr>`).join('')+'</tbody></table>';
function render(){
 const query=$('search').value.trim().toLowerCase();
 filtered=data.customers.filter(c=>(!$('segment').value||c.segment===$('segment').value)&&(!$('country').value||c.country===$('country').value)&&c.customer_id.toLowerCase().includes(query));
 const sort=$('sort').value;
 filtered.sort((a,b)=>sort==='customer_id'?a.customer_id.localeCompare(b.customer_id):((sort==='recency_days'?a[sort]-b[sort]:b[sort]-a[sort])||a.customer_id.localeCompare(b.customer_id)));
 page=Math.min(page,Math.max(0,Math.ceil(filtered.length/size)-1));
 const total=filtered.reduce((n,c)=>n+c.monetary_cents,0);
 $('customers').textContent=filtered.length.toLocaleString();$('revenue').textContent=euro(total);
 $('frequency').textContent=filtered.length?(filtered.reduce((n,c)=>n+c.frequency,0)/filtered.length).toFixed(1):'—';
 const rec=filtered.map(c=>c.recency_days).sort((a,b)=>a-b);const mid=Math.floor(rec.length/2);
 $('recency').textContent=rec.length?`${rec.length%2?rec[mid]:((rec[mid-1]+rec[mid])/2)} days`:'—';
 $('status').textContent=`${filtered.length} of ${data.customers.length} customers shown. Customer metrics and segment bars follow your filters; monthly sales remain the full dataset.`;
 $('segments').innerHTML=data.segments.map(s=>{const rows=filtered.filter(c=>c.segment===s.segment);const sales=rows.reduce((n,c)=>n+c.monetary_cents,0);return `<div class="segment-row"><div class="segment-label"><strong>${esc(s.segment)}</strong><span>${rows.length} customers · ${euro(sales)}</span></div><div class="track"><div class="bar" style="width:${total?sales/total*100:0}%"></div></div><p class="action">${esc(s.action)}</p></div>`;}).join('');
 $('rows').innerHTML=filtered.length?filtered.slice(page*size,(page+1)*size).map(c=>`<tr><td><strong>${esc(c.customer_id)}</strong></td><td>${esc(c.country)}</td><td>${c.recency_days}d</td><td>${c.frequency}</td><td>${euro(c.monetary_cents)}</td><td>${c.r_score} / ${c.f_score} / ${c.m_score}</td><td><span class="badge">${esc(c.segment)}</span></td></tr>`).join(''):'<tr><td colspan="7">No customers match these filters. Try Reset.</td></tr>';
 $('page').textContent=filtered.length?`${page*size+1}–${Math.min((page+1)*size,filtered.length)} of ${filtered.length}`:'0 results';
 $('prev').disabled=page===0;$('next').disabled=(page+1)*size>=filtered.length;
}
for(const id of ['segment','country','search','sort'])$(id).addEventListener('input',()=>{page=0;render();});
$('reset').onclick=()=>{for(const id of ['segment','country','search'])$(id).value='';$('sort').value='monetary_cents';page=0;render();};
$('prev').onclick=()=>{page--;render();};$('next').onclick=()=>{page++;render();};
function csvCell(v){let s=String(v);if(/^[=+@\-\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}
$('export').onclick=()=>{const keys=['customer_id','country','recency_days','frequency','monetary_cents','r_score','f_score','m_score','segment'];const csv=[keys,...filtered.map(c=>keys.map(k=>c[k]))].map(r=>r.map(csvCell).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}));const a=document.createElement('a');a.href=url;a.download='customer-segments.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
render();
