#!/usr/bin/env python3
# incident_simulator.py — simulate incident detection + response

import time
import random
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime('%H:%M:%S')

def check_metrics():
    """Simulate metric collection"""
    return {
        'error_rate':    random.uniform(0, 15),
        'latency_p99':   random.randint(100, 2000),
        'cpu_percent':   random.randint(20, 95),
        'availability':  random.uniform(95, 100),
    }

def evaluate_severity(metrics):
    """Determine incident severity"""
    if metrics['error_rate'] > 10 or metrics['availability'] < 97:
        return 'P1', '🔴 CRITICAL — all hands on deck!'
    elif metrics['error_rate'] > 5 or metrics['latency_p99'] > 1500:
        return 'P2', '🟠 HIGH — team lead + engineer'
    elif metrics['error_rate'] > 1 or metrics['cpu_percent'] > 85:
        return 'P3', '🟡 MEDIUM — engineer investigates'
    else:
        return None, None

def run_incident_simulation():
    print("=" * 55)
    print("   Incident Response Simulator")
    print("=" * 55)
    print("\nMonitoring system metrics...\n")

    incident_active = False
    incident_start  = None
    check_count     = 0

    for i in range(10):
        check_count += 1
        metrics = check_metrics()
        severity, description = evaluate_severity(metrics)

        print(f"[{get_timestamp()}] Check #{check_count}")
        print(f"  Error rate:  {metrics['error_rate']:.1f}%  "
              f"| Latency p99: {metrics['latency_p99']}ms  "
              f"| CPU: {metrics['cpu_percent']}%")

        if severity and not incident_active:
            incident_active = True
            incident_start  = datetime.now()
            print(f"\n  🚨 INCIDENT DETECTED!")
            print(f"  Severity:    {severity} — {description}")
            print(f"  Time:        {get_timestamp()}")
            print(f"  Action:      Alertmanager → PagerDuty → On-call engineer")
            print(f"  IC assigned: @on-call-engineer")
            print(f"  War room:    #incident-{severity.lower()}-{i}")
            print()

        elif not severity and incident_active:
            incident_active = False
            duration = (datetime.now() - incident_start).seconds
            print(f"\n  ✅ INCIDENT RESOLVED!")
            print(f"  Duration:    {duration} seconds")
            print(f"  Next step:   Schedule blameless postmortem")
            print(f"  Template:    confluence/postmortem-template")
            print()

        time.sleep(0.5)

    print("\n" + "=" * 55)
    print("Five Whys — Root Cause Analysis Template")
    print("=" * 55)
    whys = [
        ("Why did the service fail?",
         "Error rate exceeded 10% threshold"),
        ("Why did error rate spike?",
         "Database connection pool exhausted"),
        ("Why was pool exhausted?",
         "New feature increased DB queries by 300%"),
        ("Why wasn't this caught?",
         "No load testing before deployment"),
        ("Why no load testing?",
         "Not defined in deployment checklist → ROOT CAUSE"),
    ]
    for i, (question, answer) in enumerate(whys, 1):
        print(f"\nWhy #{i}: {question}")
        print(f"  → {answer}")

    print("\n\nAction Items:")
    actions = [
        ("Add load testing to CI/CD pipeline",
         "@dev-lead",    "3 days"),
        ("Add DB connection pool alerts",
         "@sre-team",    "1 day"),
        ("Update deployment checklist",
         "@eng-manager", "2 days"),
        ("Write runbook for DB issues",
         "@sre-team",    "5 days"),
    ]
    print(f"\n{'Action':<40} {'Owner':<15} {'Due'}")
    print("-" * 65)
    for action, owner, due in actions:
        print(f"{action:<40} {owner:<15} {due}")

    print("\n✅ Postmortem complete — action items assigned!")

if __name__ == '__main__':
    run_incident_simulation()