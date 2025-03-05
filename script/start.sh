#!/usr/bin/env bash

# Set SSH_USER to root if not provided
SSH_USER=${SSH_USER:-root}

# Check if SSH_USER exists, if not create it
if ! id "$SSH_USER" &>/dev/null; then
    useradd -m $SSH_USER
fi

# Enable or disable password authentication based on SSH_PASSWORD environment variable
if [ -n "$SSH_PASSWORD" ]; then
    sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
    echo "$SSH_USER:$SSH_PASSWORD" | chpasswd
fi

# If a PUBLIC_KEY environment variable is provided, add the key to the SSH_USER
if [ -n "$PUBLIC_KEY" ]; then
    # Determine correct home directory
    HOME_DIR=$(getent passwd "$SSH_USER" | cut -d: -f6)
    mkdir -p $HOME_DIR/.ssh
    echo $PUBLIC_KEY > $HOME_DIR/.ssh/authorized_keys
    chown -R $SSH_USER:$SSH_USER $HOME_DIR/.ssh
    chmod 700 $HOME_DIR/.ssh
    chmod 600 $HOME_DIR/.ssh/authorized_keys
fi

# Start the SSH daemon
/usr/sbin/sshd -D &

# Start Jupyter Lab
echo "🔄 Jupyter Lab başlatılıyor..."
nohup jupyter-lab --allow-root --ip=0.0.0.0 --NotebookApp.token='' --NotebookApp.password='' --notebook-dir=/workspace --NotebookApp.allow_origin='*' --NotebookApp.allow_remote_access=1 &

# Use libtcmalloc for better memory management
TCMALLOC="$(ldconfig -p | grep -Po "libtcmalloc.so.\d" | head -n 1)"
export LD_PRELOAD="${TCMALLOC}"

# RunPod Serverless Handler başlat
echo "🔄 RunPod Handler başlatılıyor..."
python3 -u /workspace/rp_handler.py

# Ensure container doesn't stop by tailing a log or keeping it alive
tail -f /dev/null
