"""Generate fictional order-level retail data, reproducibly. No personal data."""
import csv, random
from datetime import date, timedelta
from pathlib import Path

def generate(path, seed=42, customers=600):
    rng = random.Random(seed)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(1, customers+1):
        country = rng.choice(['Ireland','United Kingdom','Germany','France','Netherlands'])
        count = rng.choices([1,3,8,18], [25,30,30,15])[0]
        for _ in range(count):
            amount = rng.randint(1200, 42000)
            refund = rng.choice([0,0,0,0, amount//4, amount])
            rows.append(dict(order_id=f'O{len(rows)+1:06}', customer_id=f'C{i:04}',
                order_date=(date(2025,11,1)+timedelta(days=rng.randrange(365))).isoformat(), country=country,
                amount_eur=f'{amount//100}.{amount%100:02}', refund_eur=f'{refund//100}.{refund%100:02}',
                status='cancelled' if rng.random()<0.04 else 'completed'))
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    return len(rows)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    print(f"Generated {generate(root/'data/transactions.csv')} synthetic orders")
