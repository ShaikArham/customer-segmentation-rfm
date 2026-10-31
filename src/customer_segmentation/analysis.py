"""RFM segmentation. Money is represented as integer cents throughout."""
import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation

COLUMNS = {'order_id', 'customer_id', 'order_date', 'country', 'amount_eur', 'refund_eur', 'status'}
SEGMENTS = ['Champions', 'Loyal customers', 'New customers', 'Potential loyalists', 'At risk', 'Hibernating', 'Needs attention']
ACTIONS = {
    'Champions': 'Test recognition and referral offers against a holdout group.',
    'Loyal customers': 'Test relevant cross-sell offers; monitor repeat purchase rate.',
    'New customers': 'Test onboarding and a second-purchase reminder.',
    'Potential loyalists': 'Test personalised recommendations with a control group.',
    'At risk': 'Test a win-back campaign; cap contact frequency.',
    'Hibernating': 'Check consent and test low-frequency reactivation.',
    'Needs attention': 'Investigate purchase barriers before proposing incentives.',
}

def cents(value):
    try:
        n = Decimal(value)
        if not n.is_finite() or n < 0 or n.as_tuple().exponent < -2:
            raise ValueError('money must be non-negative with at most two decimals')
        return int(n * 100)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError('invalid money') from exc

def load_orders(path):
    """Strict schema, unique orders and stable customer-country attribution."""
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not COLUMNS.issubset(reader.fieldnames or []):
            raise ValueError('missing columns: ' + ', '.join(sorted(COLUMNS - set(reader.fieldnames or []))))
        orders, seen, countries = [], set(), {}
        for line, row in enumerate(reader, 2):
            try:
                if any(row[k] is None or not row[k].strip() for k in COLUMNS):
                    raise ValueError('blank required field')
                oid, cid = row['order_id'].strip(), row['customer_id'].strip()
                if oid in seen:
                    raise ValueError('duplicate order_id')
                seen.add(oid)
                country = row['country'].strip()
                if cid in countries and countries[cid] != country:
                    raise ValueError('customer has inconsistent country')
                countries[cid] = country
                amount, refund = cents(row['amount_eur']), cents(row['refund_eur'])
                if refund > amount:
                    raise ValueError('refund exceeds order amount')
                status = row['status'].strip()
                if status not in {'completed', 'cancelled'}:
                    raise ValueError('status must be completed or cancelled')
                orders.append(dict(order_id=oid, customer_id=cid, date=date.fromisoformat(row['order_date']),
                                   country=country, gross=amount, refund=refund, status=status))
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f'CSV line {line}: {exc}') from exc
    if not orders:
        raise ValueError('input contains no orders')
    return orders

def thresholds(values):
    """Four nearest-rank quintile cutoffs; no tie-breaking by customer ID."""
    from math import ceil
    values = sorted(values)
    return [values[max(0, ceil(len(values) * q / 5) - 1)] for q in range(1, 5)]

def score(value, cuts, reverse=False):
    # Strictly exceeding a cutoff advances the score; identical values stay together.
    n = 1 + sum(value > cut for cut in cuts)
    return 6 - n if reverse else n

def segment(r, f, m):
    if r >= 4 and f >= 4 and m >= 4: return 'Champions'
    if r <= 2 and f >= 4: return 'At risk'
    if r <= 2 and f <= 2: return 'Hibernating'
    if r >= 4 and f <= 2: return 'New customers'
    if r >= 3 and f >= 4: return 'Loyal customers'
    if r >= 3 and f >= 2: return 'Potential loyalists'
    return 'Needs attention'

def analyse(orders, as_of, window_days=365):
    from datetime import timedelta
    if window_days < 1: raise ValueError('window_days must be positive')
    start = as_of - timedelta(days=window_days)
    # Future rows are excluded, not used to compute scores or revenue.
    in_window = [o for o in orders if start <= o['date'] < as_of]
    eligible = [o for o in in_window if o['status'] == 'completed' and o['gross'] > o['refund']]
    if not eligible: raise ValueError('no positive-net completed orders in analysis window')
    groups = defaultdict(list)
    for o in eligible: groups[o['customer_id']].append(o)
    customers = []
    for cid, rows in sorted(groups.items()):
        customers.append(dict(customer_id=cid, country=rows[0]['country'],
                              recency_days=(as_of - max(o['date'] for o in rows)).days,
                              frequency=len(rows), monetary_cents=sum(o['gross'] - o['refund'] for o in rows)))
    cuts = {k: thresholds([c[k] for c in customers]) for k in ('recency_days','frequency','monetary_cents')}
    for c in customers:
        c['r_score'] = score(c['recency_days'], cuts['recency_days'], True)
        c['f_score'] = score(c['frequency'], cuts['frequency'])
        c['m_score'] = score(c['monetary_cents'], cuts['monetary_cents'])
        c['segment'] = segment(c['r_score'], c['f_score'], c['m_score'])
    monthly = defaultdict(lambda: {'net_cents': 0, 'orders': 0})
    for o in eligible:
        item = monthly[o['date'].strftime('%Y-%m')]
        item['net_cents'] += o['gross'] - o['refund']; item['orders'] += 1
    summary = []
    for name in SEGMENTS:
        rows = [c for c in customers if c['segment'] == name]
        summary.append(dict(segment=name, customers=len(rows), net_cents=sum(c['monetary_cents'] for c in rows), action=ACTIONS[name]))
    return dict(as_of=as_of.isoformat(), start=start.isoformat(), window_days=window_days,
                synthetic=True, customers=customers, segments=summary, thresholds=cuts,
                monthly=[dict(month=k, **v) for k,v in sorted(monthly.items())],
                quality=dict(input_orders=len(orders), in_window=len(in_window), eligible_orders=len(eligible),
                    outside_window=len(orders)-len(in_window), cancelled=sum(o['status']=='cancelled' for o in in_window),
                    fully_refunded=sum(o['status']=='completed' and o['gross']==o['refund'] for o in in_window),
                    partial_refunds=sum(o['refund']>0 for o in eligible)),
                net_cents=sum(o['gross']-o['refund'] for o in eligible))
