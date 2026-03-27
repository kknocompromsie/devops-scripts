#!/bin/bash
THRESHOLD=80
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "===== Disk Monitor Started: $DATE ====="

df -h | grep -vE '^Filesystem|tmpfs' | while read line; do
  # Use% is always second to last column, Mount is last
  USAGE=$(echo $line | awk '{print $(NF-1)}' | sed 's/%//')
  PARTITION=$(echo $line | awk '{print $NF}')

  # Skip if USAGE is not a number
  if ! [[ "$USAGE" =~ ^[0-9]+$ ]]; then
    continue
  fi

  if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "⚠️  ALERT: $PARTITION is ${USAGE}% full!"
  else
    echo "✅ OK: $PARTITION is ${USAGE}% used"
  fi
done

echo "===== Disk Monitor Complete ====="