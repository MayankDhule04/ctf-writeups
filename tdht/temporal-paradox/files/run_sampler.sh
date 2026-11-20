#!/bin/bash
cd /data
for f in feed_accepted.bin feed_all12.bin feed_rec08.bin feed_region.bin; do
    echo "=== $f ==="
    /data/extracted/usr/local/sbin/r9sampler "$f"
done
# also try feeding it the whole image directly (it reads up to 64k)
echo "=== lane_0.cal ==="
/data/extracted/usr/local/sbin/r9sampler /data/extracted/var/lib/deltaforge/lane_0.cal
echo "=== lane_1.cal ==="
/data/extracted/usr/local/sbin/r9sampler /data/extracted/var/lib/deltaforge/lane_1.cal
