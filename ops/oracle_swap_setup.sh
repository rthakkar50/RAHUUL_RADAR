#!/usr/bin/env bash
# Oracle Always Free VM.Standard.E2.1.Micro 2GB Swap Creation & Tuning Script

set -e

echo "=== Setting up 2GB Swapfile for Oracle E2 Micro (1GB RAM) ==="

if [ -f /swapfile ]; then
    echo "Swapfile /swapfile already exists. Skipping creation."
else
    sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "2GB Swapfile created and activated successfully."
fi

# Set swappiness to 10 for optimal low-RAM performance
sudo sysctl vm.swappiness=10
if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
fi

echo "=== Memory & Swap Status ==="
free -h
