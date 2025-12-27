#!/bin/bash
#
# VPS Server Analysis Script
# Собирает информацию о текущем состоянии сервера для планирования развертывания Docker
#
# Использование:
#   1. Скопируйте на VPS: scp vps_check.sh user@vps:/tmp/
#   2. Запустите: ssh user@vps "bash /tmp/vps_check.sh" > vps_report.txt
#   3. Изучите отчет: cat vps_report.txt
#

set -e

echo "=============================================================================="
echo "VPS SERVER ANALYSIS REPORT"
echo "Generated: $(date)"
echo "Hostname: $(hostname)"
echo "=============================================================================="
echo ""

# ============================================================================
# 1. SYSTEM INFO
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. SYSTEM INFORMATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "OS Information:"
cat /etc/os-release | grep -E "^(NAME|VERSION)=" || echo "  N/A"
echo ""
echo "Kernel:"
uname -r
echo ""
echo "CPU:"
lscpu | grep -E "^(Model name|CPU\(s\)|Thread|Core)" || echo "  N/A"
echo ""
echo "Memory:"
free -h
echo ""
echo "Disk Space:"
df -h | grep -E "^(/dev/|Filesystem)"
echo ""

# ============================================================================
# 2. NETWORK & PORTS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. NETWORK & PORTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Listening Ports (TCP):"
sudo netstat -tlnp 2>/dev/null || sudo ss -tlnp 2>/dev/null || echo "  Unable to get port info (netstat/ss not available)"
echo ""
echo "Public IP Address:"
curl -s ifconfig.me 2>/dev/null || echo "  Unable to determine"
echo ""
echo ""

# ============================================================================
# 3. RUNNING SERVICES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. RUNNING SERVICES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Systemd Services (active):"
systemctl list-units --type=service --state=active --no-pager | grep -E "(nginx|apache|postgres|redis|mysql|gunicorn|uwsgi|celery|supervisor)" || echo "  No relevant services found"
echo ""
echo "Supervisor Programs:"
if command -v supervisorctl &> /dev/null; then
    sudo supervisorctl status 2>/dev/null || echo "  Supervisor not running"
else
    echo "  Supervisor not installed"
fi
echo ""

# ============================================================================
# 4. WEB SERVERS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. WEB SERVERS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Nginx
if command -v nginx &> /dev/null; then
    echo "Nginx:"
    echo "  Version: $(nginx -v 2>&1 | cut -d/ -f2)"
    echo "  Status: $(systemctl is-active nginx 2>/dev/null || echo 'unknown')"
    echo "  Config: /etc/nginx/nginx.conf"
    echo ""
    echo "  Nginx Sites Enabled:"
    if [ -d /etc/nginx/sites-enabled ]; then
        ls -1 /etc/nginx/sites-enabled/ 2>/dev/null | sed 's/^/    - /' || echo "    None"
    else
        echo "    Directory not found"
    fi
    echo ""
    echo "  Nginx Server Blocks (listening addresses):"
    sudo nginx -T 2>/dev/null | grep -E "^\s*listen\s+" | sort -u | sed 's/^/    /' || echo "    Unable to parse config"
    echo ""
    echo "  Nginx Server Names:"
    sudo nginx -T 2>/dev/null | grep -E "^\s*server_name\s+" | sort -u | sed 's/^/    /' || echo "    Unable to parse config"
else
    echo "Nginx: Not installed"
fi
echo ""

# Apache
if command -v apache2 &> /dev/null || command -v httpd &> /dev/null; then
    echo "Apache:"
    apache2 -v 2>/dev/null || httpd -v 2>/dev/null || echo "  Version unknown"
    echo "  Status: $(systemctl is-active apache2 2>/dev/null || systemctl is-active httpd 2>/dev/null || echo 'unknown')"
else
    echo "Apache: Not installed"
fi
echo ""

# ============================================================================
# 5. DATABASES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. DATABASES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# PostgreSQL
if command -v psql &> /dev/null; then
    echo "PostgreSQL:"
    echo "  Version: $(psql --version | cut -d' ' -f3)"
    echo "  Status: $(systemctl is-active postgresql 2>/dev/null || echo 'unknown')"
    echo "  Port: $(sudo netstat -tlnp 2>/dev/null | grep postgres | awk '{print $4}' | cut -d: -f2 | head -1 || echo 'unknown')"
    echo "  Databases:"
    sudo -u postgres psql -c "\l" 2>/dev/null | grep -E "^\s+\w+" | sed 's/^/    /' || echo "    Unable to list"
else
    echo "PostgreSQL: Not installed"
fi
echo ""

# MySQL/MariaDB
if command -v mysql &> /dev/null; then
    echo "MySQL/MariaDB:"
    mysql --version
    echo "  Status: $(systemctl is-active mysql 2>/dev/null || systemctl is-active mariadb 2>/dev/null || echo 'unknown')"
else
    echo "MySQL/MariaDB: Not installed"
fi
echo ""

# Redis
if command -v redis-cli &> /dev/null; then
    echo "Redis:"
    echo "  Version: $(redis-cli --version | cut -d' ' -f2)"
    echo "  Status: $(systemctl is-active redis 2>/dev/null || systemctl is-active redis-server 2>/dev/null || echo 'unknown')"
    echo "  Port: $(sudo netstat -tlnp 2>/dev/null | grep redis | awk '{print $4}' | cut -d: -f2 | head -1 || echo 'unknown')"
else
    echo "Redis: Not installed"
fi
echo ""

# ============================================================================
# 6. PYTHON & ENVIRONMENTS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. PYTHON & ENVIRONMENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Python Versions:"
for py in python python3 python3.8 python3.9 python3.10 python3.11; do
    if command -v $py &> /dev/null; then
        echo "  $py: $($py --version 2>&1)"
    fi
done
echo ""
echo "Virtual Environments (common locations):"
for dir in /home/*/venv /home/*/env /opt/*/venv /var/www/*/venv ~/.virtualenvs/*; do
    if [ -d "$dir" ]; then
        echo "  - $dir"
    fi
done 2>/dev/null || echo "  None found in common locations"
echo ""

# ============================================================================
# 7. DOCKER
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. DOCKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if command -v docker &> /dev/null; then
    echo "Docker:"
    echo "  Version: $(docker --version)"
    echo "  Status: $(systemctl is-active docker 2>/dev/null || echo 'unknown')"
    echo ""
    echo "  Running Containers:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "    None or unable to access"
    echo ""
    echo "  Docker Compose:"
    if command -v docker-compose &> /dev/null; then
        echo "    docker-compose: $(docker-compose --version)"
    else
        echo "    docker-compose: Not installed"
    fi
    if docker compose version &> /dev/null; then
        echo "    docker compose: $(docker compose version)"
    else
        echo "    docker compose: Not available"
    fi
else
    echo "Docker: Not installed"
fi
echo ""

# ============================================================================
# 8. APPLICATION PROCESSES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. APPLICATION PROCESSES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Python Web Servers:"
ps aux | grep -E "(gunicorn|uwsgi|django|celery)" | grep -v grep | sed 's/^/  /' || echo "  None found"
echo ""
echo "Node.js Processes:"
ps aux | grep -E "node" | grep -v grep | sed 's/^/  /' || echo "  None found"
echo ""

# ============================================================================
# 9. COMMON APPLICATION DIRECTORIES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. COMMON APPLICATION DIRECTORIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
for dir in /var/www /home/*/projects /home/*/www /opt/apps /srv; do
    if [ -d "$dir" ]; then
        echo "$dir:"
        find "$dir" -maxdepth 2 -name "manage.py" -o -name "wsgi.py" -o -name "docker-compose.yml" 2>/dev/null | sed 's/^/  /' || echo "  No Django/Docker projects found"
    fi
done
echo ""

# ============================================================================
# 10. FIREWALL
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "10. FIREWALL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if command -v ufw &> /dev/null; then
    echo "UFW Status:"
    sudo ufw status verbose 2>/dev/null || echo "  Unable to check"
elif command -v firewall-cmd &> /dev/null; then
    echo "Firewalld Status:"
    sudo firewall-cmd --list-all 2>/dev/null || echo "  Unable to check"
else
    echo "Firewall: No common firewall found (ufw/firewalld)"
fi
echo ""

# ============================================================================
# 11. NGINX CONFIGURATION ANALYSIS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "11. NGINX CONFIGURATION DETAILS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if command -v nginx &> /dev/null; then
    echo "Active Nginx Configurations:"
    echo ""
    for conf in /etc/nginx/sites-enabled/*; do
        if [ -f "$conf" ]; then
            echo "  Configuration: $(basename $conf)"
            echo "  ----------------------------------------"
            cat "$conf" | grep -E "(listen|server_name|location|proxy_pass|root)" | sed 's/^/    /'
            echo ""
        fi
    done
else
    echo "Nginx not installed - skipping configuration analysis"
fi
echo ""

# ============================================================================
# 12. SUMMARY & RECOMMENDATIONS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "12. PORT AVAILABILITY FOR DOCKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Checking common ports for Docker application:"
echo ""
for port in 8000 8001 8080 8081 5432 5433 6379 6380 80 443; do
    if sudo netstat -tln 2>/dev/null | grep -q ":$port " || sudo ss -tln 2>/dev/null | grep -q ":$port "; then
        echo "  Port $port: ✗ IN USE"
    else
        echo "  Port $port: ✓ Available"
    fi
done
echo ""

# ============================================================================
# END
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "END OF REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next Steps:"
echo "  1. Review this report"
echo "  2. Share with deployment team/assistant"
echo "  3. Plan Docker deployment strategy"
echo "  4. Choose available ports for new application"
echo ""
