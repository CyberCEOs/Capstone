FROM kalilinux/kali-rolling

# Lightweight Kali image setup for lab use: adds openssh, nmap, sshpass, python3
# Note: metasploit is large; install it manually on the Kali host if needed.

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    sudo \
    nmap \
    sshpass \
    curl \
    python3 \
    python3-pip \
    git \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Create pentester user with password 'kali' (change in production)
RUN useradd -m -s /bin/bash pentester && echo "pentester:kali" | chpasswd && adduser pentester sudo

# Setup SSHD
# Create run dir if missing (use -p to avoid failure if it already exists)
RUN mkdir -p /var/run/sshd || true
# Ensure password authentication is allowed so the lab user can SSH with a password
RUN sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config || true
RUN sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config || true
RUN echo "AllowUsers pentester" >> /etc/ssh/sshd_config || true
EXPOSE 22

# Install linpeas script in /opt
RUN mkdir -p /opt/linpeas && \
    curl -sSL https://raw.githubusercontent.com/carlospolop/PEASS-ng/master/linpeas/linpeas.sh -o /opt/linpeas/linpeas.sh && \
    chmod +x /opt/linpeas/linpeas.sh

# Default command
CMD ["/usr/sbin/sshd", "-D"]
