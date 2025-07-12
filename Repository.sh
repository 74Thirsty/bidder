#!/bin/bash

# Prompt for GitHub username and repository name
echo "Enter your GitHub username:"
read username

echo "Enter the repository name:"
read repository

# Generate SSH key
echo "Generating SSH key..."
ssh-keygen -t rsa -b 4096 -C "$username@github.com" -f "$HOME/.ssh/id_rsa" -N ""

# Start the SSH agent
echo "Starting the SSH agent..."
eval "$(ssh-agent -s)"

# Add the SSH key to the agent
echo "Adding SSH key to the agent..."
ssh-add ~/.ssh/id_rsa

# Copy the public key to the clipboard (display it so user can copy it)
echo "Public key generated. Please copy the following and add it to your GitHub account:"
cat ~/.ssh/id_rsa.pub

# Keep the script on screen and ask to continue after key is added to GitHub
echo "Press any key after adding the SSH key to GitHub."
read -n 1 -s

# Test SSH connection to GitHub
echo "Testing SSH connection to GitHub..."
ssh -T git@github.com

# Clone the repository to test the setup
echo "Cloning the repository $repository..."
git clone git@github.com:$username/$repository.git

echo "GitHub SSH key setup is complete and the repository has been cloned!"

