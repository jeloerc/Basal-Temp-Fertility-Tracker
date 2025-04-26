#!/bin/bash

echo "Starting Basal Temperature Tracker React Native App"
echo "=================================================="
echo "This script will start the React Native application with Expo."
echo "Make sure your Flask backend is running at http://192.168.50.164:5000"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm first."
    exit 1
fi

# Check if Expo CLI is installed
if ! command -v expo &> /dev/null; then
    echo "Expo CLI is not installed. Installing globally..."
    npm install -g expo-cli
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Display server information
echo "API server: http://192.168.50.164:5000"
echo "If your device can't connect, make sure it's on the same network"
echo ""

# Start the Expo server
echo "Starting Expo server..."
echo "Scan the QR code with your Expo Go app when it appears"
echo ""
npm start 