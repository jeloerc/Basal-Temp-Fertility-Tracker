# Basal Temperature Tracker with React Native Integration

This project enhances the Basal Temperature Tracker web application by adding React Native mobile app support using Victory charts for data visualization.

## New Features

The React Native mobile app provides all the essential features of the web application, plus:

- **Enhanced Data Visualization**: Interactive charts with Victory for a superior mobile experience
- **Phase Identification**: Visual differentiation between follicular and luteal phases
- **Pattern Recognition**: Automatic detection of temperature shifts and fertile days
- **Multiple Cycle Support**: Easy navigation between different menstrual cycles
- **Detailed Analytics**: Statistical analysis of cycle patterns
- **Temperature Unit Toggle**: Switch between Fahrenheit and Celsius
- **Offline Capabilities**: Cache data for viewing when not connected to the server

## Architecture

The system consists of two main components:

1. **Flask Backend** (existing): Provides data management, cycle calculation, and API endpoints
2. **React Native Frontend** (new): Mobile app for data visualization and user interaction

The backend has been enhanced with a new API endpoint:
- `/api/cycle_analytics`: Provides comprehensive cycle data formatted for the React Native app

## Setup Instructions

### Prerequisites

- Python 3.6+ with Flask
- MySQL or compatible database
- Node.js v14+ with npm
- React Native development environment
- Expo CLI

### Backend Setup (Flask)

The backend is already set up. The new API endpoint is already integrated into the existing Flask application.

To update your existing backend:

1. Pull the latest code
2. Restart your Apache server or Flask application
3. Test the API endpoint with: `curl http://your-server-ip:5000/api/cycle_analytics`

### Mobile App Setup (React Native)

To set up the React Native mobile app:

1. Navigate to the `react-native-app` directory:
   ```
   cd react-native-app
   ```

2. Run the setup script:
   ```
   bash setup.sh
   ```
   This script will check for the required dependencies, install packages, and configure your server address.

3. Start the development server:
   ```
   npm start
   ```

4. Scan the QR code with your mobile device using the Expo Go app (available on iOS App Store and Google Play Store)

## Usage Guidelines

### Data Visualization

The app displays your basal temperature data with the following color coding:

- **Purple Line**: Follicular phase (pre-ovulation)
- **Pink Line**: Luteal phase (post-ovulation)
- **Red Markers**: Period days
- **Lime Green Line**: Fertile threshold
- **Shaded Area**: Potentially fertile zone

### Temperature Shift Detection

The app automatically calculates the temperature shift between the follicular and luteal phases:

- A shift of 0.2°C (0.4°F) or more indicates potential ovulation
- The app highlights this shift and marks the likely fertile days

### Navigating Multiple Cycles

Use the carousel at the top of the screen to navigate between different cycles. For each cycle, you can view:

- Start and end dates
- Cycle length
- Average temperature
- Temperature shift
- Period days

## API Documentation

The backend provides the following API endpoint for the React Native app:

### GET /api/cycle_analytics

Returns comprehensive cycle analytics data formatted for React Native / Victory charts.

**Response:**

```json
{
  "temperatures": [
    {
      "date": "2023-01-01",
      "temp": 97.5,
      "cycleDay": 1,
      "isPeriod": true
    },
    // ... more temperature readings
  ],
  "cycles": [
    {
      "startDate": "2023-01-01",
      "endDate": "2023-01-28",
      "length": 28,
      "avgTemp": 97.8,
      "tempShift": 0.4,
      "periodDays": ["2023-01-01", "2023-01-02", "2023-01-03"]
    },
    // ... more cycles
  ],
  "phaseAnalysis": {
    "follicular": {
      "days": [...],
      "avgTemp": 97.6
    },
    "luteal": {
      "days": [...],
      "avgTemp": 98.0
    }
  },
  "stats": {
    "avgCycleLength": 28.5,
    "avgTemperature": 97.8,
    "tempShift": 0.4
  }
}
```

## Additional Resources

- React Native documentation: https://reactnative.dev/docs/getting-started
- Victory charts documentation: https://formidable.com/open-source/victory/docs
- Expo documentation: https://docs.expo.dev

## Troubleshooting

Common issues and solutions:

1. **API connection errors**: Ensure your server is running and accessible from your mobile device's network.

2. **Chart display issues**: Verify that your temperature data is correctly formatted and has enough points to display.

3. **Missing cycle data**: If no cycles appear, ensure you have marked period days correctly in the web application.

4. **Expo build errors**: Make sure you have the latest version of Expo CLI and all dependencies installed.

## License

This project is licensed under the same terms as the original Basal Temperature Tracker application.

## Acknowledgments

- Victory charts by Formidable Labs
- React Native by Facebook
- Expo for simplified React Native development 