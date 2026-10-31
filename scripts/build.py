"""Build deterministic CSV/JSON outputs and a dependency-free dashboard payload."""
import argparse, csv, json, sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from customer_segmentation.analysis import load_orders, analyse

def build(input_path, out_dir, site_dir, as_of, window_days=365, synthetic=False):
    result=analyse(load_orders(input_path),as_of,window_days)
    result['synthetic']=synthetic
    out_dir=Path(out_dir);site_dir=Path(site_dir)
    out_dir.mkdir(parents=True,exist_ok=True);site_dir.mkdir(parents=True,exist_ok=True)
    for name,rows in [('customers',result['customers']),('segments',result['segments']),('monthly',result['monthly'])]:
        with (out_dir/f'{name}.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    payload=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=True)
    (out_dir/'analysis.json').write_text(payload+'\n',encoding='utf-8')
    # HTML imports a JS payload so the static demo also works from file://.
    (site_dir/'data.js').write_text('window.RFM_DATA = '+payload+';\n',encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'data/transactions.csv')
    p.add_argument('--as-of',type=date.fromisoformat,default=date(2026,11,1))
    p.add_argument('--window-days',type=int,default=365)
    p.add_argument('--out',type=Path,default=ROOT/'outputs')
    p.add_argument('--site',type=Path,default=ROOT/'site')
    p.add_argument('--synthetic',action='store_true',help='Label this dataset as fictional; use for supplied sample only.')
    a=p.parse_args()
    try:r=build(a.input,a.out,a.site,a.as_of,a.window_days,a.synthetic)
    except ValueError as e:p.exit(2,str(e)+'\n')
    print(json.dumps(dict(customers=len(r['customers']),net_eur=r['net_cents']/100,quality=r['quality']),indent=2))
