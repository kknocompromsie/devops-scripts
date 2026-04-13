#!/usr/bin/env python3
# slo_tracker.py — calculate SLIs and check against SLOs

from datetime import datetime, timedelta
import random

# Define SLOs
SLOS = {
    'availability': 99.9,    # 99.9% uptime
    'latency_p99':  500,     # p99 < 500ms
    'error_rate':   1.0,     # error rate < 1%
}

def simulate_metrics(hours=24):
    """Simulate 24 hours of metrics"""
    metrics = []
    base_time = datetime.now() - timedelta(hours=hours)

    for i in range(hours * 60):  # one data point per minute
        timestamp = base_time + timedelta(minutes=i)

        # Simulate occasional issues
        is_incident = (400 <= i <= 445)  # 45-min incident

        metrics.append({
            'timestamp':    timestamp,
            'total_requests': random.randint(900, 1100),
            'failed_requests': random.randint(50, 100) if is_incident
                               else random.randint(0, 3),
            'latency_p99':    random.randint(800, 1200) if is_incident
                              else random.randint(100, 400),
            'is_up':          False if is_incident and i < 430
                              else True
        })

    return metrics

def calculate_slis(metrics):
    """Calculate SLIs from metrics"""
    total_minutes  = len(metrics)
    up_minutes     = sum(1 for m in metrics if m['is_up'])
    total_requests = sum(m['total_requests'] for m in metrics)
    failed_requests= sum(m['failed_requests'] for m in metrics)
    avg_latency_p99= sum(m['latency_p99'] for m in metrics) / total_minutes

    return {
        'availability': (up_minutes / total_minutes) * 100,
        'error_rate':   (failed_requests / total_requests) * 100,
        'latency_p99':  avg_latency_p99,
        'total_requests': total_requests,
        'failed_requests': failed_requests,
    }

def check_slos(slis):
    """Check SLIs against SLOs"""
    print("\n" + "=" * 55)
    print("   SLO Compliance Report — Last 24 Hours")
    print("=" * 55)

    results = {}

    # Availability check
    avail = slis['availability']
    avail_ok = avail >= SLOS['availability']
    results['availability'] = avail_ok
    icon = "✅" if avail_ok else "❌"
    print(f"\n{icon} Availability SLI:  {avail:.3f}%")
    print(f"   SLO target:        {SLOS['availability']}%")
    print(f"   Status:            {'PASSING' if avail_ok else 'BREACHED!'}")

    # Error rate check
    err = slis['error_rate']
    err_ok = err <= SLOS['error_rate']
    results['error_rate'] = err_ok
    icon = "✅" if err_ok else "❌"
    print(f"\n{icon} Error Rate SLI:    {err:.3f}%")
    print(f"   SLO target:        < {SLOS['error_rate']}%")
    print(f"   Status:            {'PASSING' if err_ok else 'BREACHED!'}")

    # Latency check
    lat = slis['latency_p99']
    lat_ok = lat <= SLOS['latency_p99']
    results['latency_p99'] = lat_ok
    icon = "✅" if lat_ok else "❌"
    print(f"\n{icon} p99 Latency SLI:   {lat:.0f}ms")
    print(f"   SLO target:        < {SLOS['latency_p99']}ms")
    print(f"   Status:            {'PASSING' if lat_ok else 'BREACHED!'}")

    return results

def calculate_error_budget(slis):
    """Calculate remaining error budget"""
    print("\n" + "=" * 55)
    print("   Error Budget Report")
    print("=" * 55)

    # Monthly budget
    monthly_mins  = 30 * 24 * 60
    allowed_down  = monthly_mins * (1 - SLOS['availability']/100)
    actual_down   = monthly_mins * (1 - slis['availability']/100)
    remaining     = allowed_down - actual_down
    pct_remaining = (remaining / allowed_down) * 100

    print(f"\n📊 Monthly Error Budget:")
    print(f"   Total allowed downtime: {allowed_down:.1f} mins")
    print(f"   Estimated used:         {actual_down:.1f} mins")
    print(f"   Remaining:              {remaining:.1f} mins")
    print(f"   Budget remaining:       {pct_remaining:.1f}%")

    if pct_remaining > 50:
        print(f"\n   🟢 Budget healthy — deploy freely!")
    elif pct_remaining > 10:
        print(f"\n   🟡 Budget low — slow down deployments!")
    else:
        print(f"\n   🔴 Budget critical — freeze deployments!")
        print(f"      Focus only on reliability improvements!")

if __name__ == '__main__':
    print("Simulating 24 hours of metrics...")
    metrics = simulate_metrics(hours=24)

    print("Calculating SLIs...")
    slis = calculate_slis(metrics)

    check_slos(slis)
    calculate_error_budget(slis)

    print("\n✅ SLO tracking complete!")