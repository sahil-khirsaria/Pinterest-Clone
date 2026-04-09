#!/bin/bash
set -e

echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y
echo "Updated system packages..."

echo "Installing Docker..."
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Installing AWS CLI..."
sudo apt-get install -y unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws
echo "Installed AWS CLI..."

echo "Adding ubuntu user to docker group..."
sudo usermod -aG docker ubuntu
echo "Added ubuntu user to docker group..."

echo "Creating app directory..."
sudo mkdir -p /home/ubuntu/app/nginx
sudo chown -R ubuntu:ubuntu /home/ubuntu/app
echo "Created app directory..."

echo "Done! Log out and back in for docker group to take effect..."
echo "Then run: docker --version && aws --version && docker compose version"