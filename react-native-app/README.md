# Basal Temperature Tracker - React Native App

## Overview
This React Native application provides a user-friendly interface for tracking and visualizing basal temperature data related to menstrual cycles. It connects to a Flask backend API to retrieve and analyze data.

## Features
- Interactive temperature charts for cycle visualization
- Cycle analysis with fertility indicators
- Temperature shift detection
- Phase analysis (follicular and luteal phases)
- Unit conversion (°F/°C)
- Cycle history navigation

## Prerequisites
- Node.js (v14+)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)

## Installation
1. Navigate to the project directory:
```
cd /var/www/Basal-Temp-Fertility-Tracker/react-native-app
```

2. Install dependencies:
```
npm install
```

## Running the Application
1. Make sure the Flask backend is running on your server.
2. Start the Expo development server:
```
npm start
```

3. To run on a physical device:
   - Install the Expo Go app on your mobile device
   - Scan the QR code displayed in the terminal or browser
   - The app will connect to the backend API at http://192.168.50.164:5000

## Troubleshooting
- If you can't connect to the API, check that:
  - The Flask backend is running
  - The server IP is correctly set in App.js (`SERVER_URL` constant)
  - Your device is on the same network as the server

## Development Notes
- The app fetches data from the `/api/cycle_analytics` endpoint
- Temperature data is visualized using Victory charts
- Fertile threshold is calculated based on temperature shift 