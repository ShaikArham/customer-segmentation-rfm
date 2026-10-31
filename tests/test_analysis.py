import csv, sys, tempfile, unittest
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from customer_segmentation.analysis import analyse, cents, load_orders, score, segment, thresholds
from generate_data import generate
from build import build

def order(oid='1',cid='A',day='2026-10-20',gross=10000,refund=0,status='completed'):
    return dict(order_id=oid,customer_id=cid,date=date.fromisoformat(day),country='Ireland',gross=gross,refund=refund,status=status)

class AnalysisTests(unittest.TestCase):
    def test_money_exact(self):
        self.assertEqual(cents('19.99'),1999)
        for invalid in ['NaN','Infinity','-1','1.999','oops']:
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):cents(invalid)
    def test_order_window_is_end_exclusive(self):
        r=analyse([order('1',day='2025-11-01'),order('2',day='2026-11-01'),order('3',day='2025-10-31')],date(2026,11,1))
        self.assertEqual(r['quality']['eligible_orders'],1)
        self.assertEqual(r['customers'][0]['recency_days'],365)
    def test_refunds_cancellations_and_frequency(self):
        r=analyse([order('1'),order('2',gross=5000,refund=2000),order('3',refund=10000),order('4',status='cancelled')],date(2026,11,1))
        self.assertEqual(r['net_cents'],13000)
        self.assertEqual(r['customers'][0]['frequency'],2)
        self.assertEqual(r['quality']['fully_refunded'],1)
    def test_no_eligible_orders(self):
        with self.assertRaises(ValueError):analyse([order(status='cancelled')],date(2026,11,1))
    def test_ties_are_equal(self):
        self.assertEqual(thresholds([1]*10),[1]*4)
        self.assertEqual(score(1,[1]*4),1)
        self.assertEqual(score(1,[1]*4,True),5)
    def test_recency_direction(self):
        cuts=thresholds([10,20,30,40,50])
        self.assertGreater(score(10,cuts,True),score(50,cuts,True))
    def test_rule_precedence(self):
        self.assertEqual(segment(5,5,5),'Champions')
        self.assertEqual(segment(1,5,5),'At risk')
        self.assertEqual(segment(5,1,5),'New customers')
    def write_csv(self,path,rows):
        with open(path,'w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['order_id','customer_id','order_date','country','amount_eur','refund_eur','status']);w.writeheader();w.writerows(rows)
    def test_duplicate_order_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'orders.csv';r=dict(order_id='1',customer_id='A',order_date='2026-10-01',country='Ireland',amount_eur='10',refund_eur='0',status='completed')
            self.write_csv(p,[r,r])
            with self.assertRaisesRegex(ValueError,'duplicate order_id'):load_orders(p)
    def test_inconsistent_country_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'orders.csv';r=dict(order_id='1',customer_id='A',order_date='2026-10-01',country='Ireland',amount_eur='10',refund_eur='0',status='completed')
            self.write_csv(p,[r,dict(r,order_id='2',country='France')])
            with self.assertRaisesRegex(ValueError,'inconsistent country'):load_orders(p)
    def test_invalid_refund_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'orders.csv';r=dict(order_id='1',customer_id='A',order_date='2026-10-01',country='Ireland',amount_eur='10',refund_eur='20',status='completed')
            self.write_csv(p,[r])
            with self.assertRaisesRegex(ValueError,'refund exceeds'):load_orders(p)
            self.write_csv(p,[dict(r,refund_eur='0',status='unknown')])
            with self.assertRaisesRegex(ValueError,'status must'):load_orders(p)
    def test_revenue_and_population_reconcile(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'orders.csv';generate(p,customers=100)
            r=analyse(load_orders(p),date(2026,11,1))
            self.assertEqual(sum(s['customers'] for s in r['segments']),len(r['customers']))
            self.assertEqual(sum(s['net_cents'] for s in r['segments']),r['net_cents'])
            self.assertEqual(sum(s['net_cents'] for s in r['monthly']),r['net_cents'])
            self.assertEqual(sum(c['frequency'] for c in r['customers']),r['quality']['eligible_orders'])
    def test_pipeline_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'orders.csv';generate(p,customers=30)
            first=p.read_bytes();generate(p,customers=30);self.assertEqual(first,p.read_bytes())
            r=build(p,root/'out',root/'site',date(2026,11,1),synthetic=True)
            first=(root/'out/analysis.json').read_bytes()
            build(p,root/'out',root/'site',date(2026,11,1),synthetic=True)
            self.assertEqual(first,(root/'out/analysis.json').read_bytes())
            self.assertTrue(r['synthetic'])
            self.assertTrue((root/'site/data.js').is_file())

if __name__=='__main__':unittest.main()
