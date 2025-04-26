#!/bin/bash

# Basal Temperature Tracker - React Native Setup Script

echo "=== Basal Temperature Tracker - React Native Setup ==="
echo "This script will help you set up the React Native environment"
echo

# Check for Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo "✓ Node.js is installed (version: $NODE_VERSION)"
else
    echo "✗ Node.js is not installed. Please install Node.js v14 or higher."
    echo "  Visit https://nodejs.org to download and install."
    exit 1
fi

# Check for npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    echo "✓ npm is installed (version: $NPM_VERSION)"
else
    echo "✗ npm is not installed. It should come with Node.js."
    echo "  Try reinstalling Node.js from https://nodejs.org"
    exit 1
fi

# Check for Expo CLI
if command -v expo &> /dev/null; then
    EXPO_VERSION=$(expo --version)
    echo "✓ Expo CLI is installed (version: $EXPO_VERSION)"
else
    echo "ⓘ Expo CLI is not installed. Installing now..."
    npm install -g expo-cli
    
    if [ $? -eq 0 ]; then
        echo "✓ Expo CLI has been installed successfully"
    else
        echo "✗ Failed to install Expo CLI. Please try manually:"
        echo "  npm install -g expo-cli"
        exit 1
    fi
fi

# Install local dependencies
echo
echo "Installing project dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies. Please try manually:"
    echo "  npm install"
    exit 1
fi

# Ask for server IP
echo
echo "What is the IP address of your Basal Temperature Tracker server?"
echo "(Default: http://localhost:5000)"
read -p "> " SERVER_IP

if [ -z "$SERVER_IP" ]; then
    SERVER_IP="http://localhost:5000"
fi

# Update App.js with the server IP
sed -i "s|const SERVER_URL = 'http://localhost:5000'|const SERVER_URL = '$SERVER_IP'|g" App.js

echo "✓ Server IP has been set to: $SERVER_IP"

echo
echo "=== Setup Complete ==="
echo 
echo "To start the development server, run:"
echo "  npm start"
echo
echo "Then scan the QR code with your phone's camera or the Expo Go app."
echo "Make sure your phone is on the same network as this computer."
echo

# Make the script executable
chmod +x setup.sh 