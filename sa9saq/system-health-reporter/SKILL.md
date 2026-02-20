---
description: Generate system health reports with CPU, memory, disk, network diagnostics and recommendations.
---

# System Health Reporter

Comprehensive system health check with severity scoring and actionable recommendations.

## Requirements

- Linux (Ubuntu, Debian, RHEL, Arch)
- Standard tools: `ps`, `top`, `free`, `df`, `uptime`, `systemctl`
- No root required for basic checks (some details need sudo)

## Instructions

### Step 1: Collect metrics

```bash
uname -a && uptime                                    # System info
nproc && cat /proc/loadavg                            # CPU & load
free -h                                               # Memory & swap
df -h --exclude-type=tmpfs --exclude-type=devtmpfs --exclude-type=squashfs  # Disk
ip -brief addr                                        # Network interfaces
ss -tulnp 2>/dev/null | head -20                      # Listening ports
systemctl list-units --state=failed --no-pager 2>/dev/null   # Failed services
ps aux | awk '$8 ~ /Z/ {print}'                       # Zombie processes
ps aux --sort=-%mem | head -6                         # Top memory
ps aux --sort=-%cpu | head -6                         # Top CPU
last -5 2>/dev/null && who                            # Login activity
```

### Step 2: Score each area

| Area | 🟢 Healthy | 🟡 Warning | 🔴 Critical |
|------|-----------|------------|-------------|
| CPU Load | < 0.8 × cores | 0.8–1.5 × cores | > 1.5 × cores |
| Memory | < 80% | 80–95% | > 95% |
| Disk | < 80% | 80–95% | > 95% |
| Services | 0 failed | 1–3 failed | > 3 failed |
| Zombies | 0 | 1+ | N/A |

### Step 3: Generate report

```
## 🏥 System Health Report
**Host:** <hostname> | **OS:** <os> | **Uptime:** <uptime>
**Generated:** <timestamp>

### Overall: 🟢 Healthy / 🟡 Degraded / 🔴 Critical

| Area | Status | Details |
|------|--------|---------|
| CPU | 🟢 | Load 0.5 / 4 cores |
| Memory | 🟡 | 82% (13.1/16 GB) |
| Disk | 🟢 | / at 45% |
| Services | 🟢 | 0 failed |

### ⚠️ Recommendations
1. [High] Consider freeing memory — 82% used
2. [Low] 2 zombie processes detected (PPIDs: 1234, 5678)

### 📊 Top Consumers
- **Memory**: java (2.1 GB), chrome (1.5 GB)
- **CPU**: ffmpeg (45%), node (12%)
```

### Step 4: Save (optional)

Save to `~/system-health-reports/YYYY-MM-DD_HH-MM.md` if requested.

## Edge Cases

- **Container/VM**: Some metrics may be limited. `/proc/cpuinfo` may show host CPU count.
- **No systemctl**: Skip service checks on non-systemd systems. Use `service --status-all` as fallback.
- **macOS**: Use `vm_stat`, `sysctl`, `diskutil` instead of Linux commands.
- **Minimal install**: If `ss` missing, use `netstat -tlnp`.

## Security

- All commands are read-only — no system modifications.
- Login activity (`last`, `who`) may reveal usernames — consider audience before sharing.
- Don't include full process arguments in reports (may contain secrets).
