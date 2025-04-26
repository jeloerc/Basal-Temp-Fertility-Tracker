import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  ScrollView, 
  SafeAreaView, 
  ActivityIndicator,
  Dimensions,
  TouchableOpacity
} from 'react-native';
import { 
  VictoryLine, 
  VictoryChart, 
  VictoryAxis, 
  VictoryTheme, 
  VictoryScatter,
  VictoryArea,
  VictoryLegend,
  VictoryTooltip,
  VictoryLabel,
  VictoryVoronoiContainer
} from 'victory-native';
import { Svg, Line, Rect, Circle, Text as SvgText } from 'react-native-svg';

const { width } = Dimensions.get('window');

// Configuration
const SERVER_URL = 'http://192.168.50.164:5000'; // Change this to your server URL
const API_ENDPOINT = '/api/cycle_analytics';

// Colors
const COLORS = {
  follicular: '#7c4dff',  // Purple
  luteal: '#ff4081',      // Pink
  period: '#e91e63',      // Red
  average: '#4caf50',     // Green
  fertile: '#c6ff00',     // Lime
  grid: '#e0e0e0',        // Light Gray
  text: '#424242',        // Dark Gray
  background: '#f8f9fa',  // Light Background
  white: '#ffffff'        // White
};

const App = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [currentCycle, setCurrentCycle] = useState(null);
  const [selectedCycleIndex, setSelectedCycleIndex] = useState(0);
  const [unit, setUnit] = useState('F'); // F or C

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${SERVER_URL}${API_ENDPOINT}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
      
      // Set the current cycle to the most recent one
      if (result.cycles && result.cycles.length > 0) {
        setCurrentCycle(result.cycles[0]);
        setSelectedCycleIndex(0);
      }
      
      setError(null);
    } catch (err) {
      setError(`Failed to fetch data: ${err.message}`);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const convertTemp = (temp) => {
    // Convert between F and C if needed
    return unit === 'C' ? (temp - 32) * 5/9 : temp;
  };

  const formatTemp = (temp) => {
    // Format temperature with proper units
    const convertedTemp = convertTemp(temp);
    return `${convertedTemp.toFixed(1)}°${unit}`;
  };

  const selectCycle = (index) => {
    if (data && data.cycles && data.cycles[index]) {
      setCurrentCycle(data.cycles[index]);
      setSelectedCycleIndex(index);
    }
  };

  // Generate chart data for the current cycle
  const getCurrentCycleData = () => {
    if (!data || !currentCycle) return { temps: [], periodDays: [] };
    
    const startDate = new Date(currentCycle.startDate);
    const endDate = new Date(currentCycle.endDate);
    
    const temps = data.temperatures.filter(t => {
      const date = new Date(t.date);
      return date >= startDate && date <= endDate;
    });
    
    // Sort by cycle day
    temps.sort((a, b) => a.cycleDay - b.cycleDay);
    
    const periodDays = temps.filter(t => t.isPeriod).map(t => t.cycleDay);
    
    // Format data for Victory charts
    const formattedTemps = temps.map(t => ({
      x: t.cycleDay,
      y: convertTemp(t.temp),
      date: t.date,
      isPeriod: t.isPeriod
    }));
    
    // Calculate follicular and luteal phases
    const halfwayPoint = Math.floor(formattedTemps.length / 2);
    const follicularData = formattedTemps.slice(0, halfwayPoint);
    const lutealData = formattedTemps.slice(halfwayPoint);
    
    return { 
      temps: formattedTemps, 
      periodDays,
      follicularData,
      lutealData,
      fertileThreshold: convertTemp(data.stats.avgTemperature + 0.4), // Typical shift is 0.4°F (0.2°C)
    };
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.follicular} />
        <Text style={styles.loadingText}>Loading your cycle data...</Text>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.errorContainer}>
        <Text style={styles.errorText}>Error: {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchData}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  if (!data || !currentCycle) {
    return (
      <SafeAreaView style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No cycle data available.</Text>
      </SafeAreaView>
    );
  }

  const { temps, periodDays, follicularData, lutealData, fertileThreshold } = getCurrentCycleData();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>Basal Temperature Tracker</Text>
          <Text style={styles.subtitle}>
            Cycle {data.cycles.length - selectedCycleIndex} of {data.cycles.length}
          </Text>
        </View>
        
        {/* Cycle Selection */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.cycleSelector}
        >
          {data.cycles.map((cycle, index) => (
            <TouchableOpacity
              key={`cycle-${index}`}
              style={[
                styles.cycleButton,
                selectedCycleIndex === index && styles.selectedCycleButton
              ]}
              onPress={() => selectCycle(index)}
            >
              <Text style={[
                styles.cycleButtonText,
                selectedCycleIndex === index && styles.selectedCycleButtonText
              ]}>
                Cycle {data.cycles.length - index}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        
        {/* Cycle Information */}
        <View style={styles.cycleInfoCard}>
          <View style={styles.cycleInfoRow}>
            <View style={styles.cycleInfoItem}>
              <Text style={styles.cycleInfoLabel}>Start Date</Text>
              <Text style={styles.cycleInfoValue}>{currentCycle.startDate}</Text>
            </View>
            <View style={styles.cycleInfoItem}>
              <Text style={styles.cycleInfoLabel}>End Date</Text>
              <Text style={styles.cycleInfoValue}>{currentCycle.endDate}</Text>
            </View>
          </View>
          <View style={styles.cycleInfoRow}>
            <View style={styles.cycleInfoItem}>
              <Text style={styles.cycleInfoLabel}>Length</Text>
              <Text style={styles.cycleInfoValue}>{currentCycle.length} days</Text>
            </View>
            <View style={styles.cycleInfoItem}>
              <Text style={styles.cycleInfoLabel}>Avg Temp</Text>
              <Text style={styles.cycleInfoValue}>{formatTemp(currentCycle.avgTemp)}</Text>
            </View>
          </View>
          <View style={styles.cycleInfoRow}>
            <View style={styles.cycleInfoItem}>
              <Text style={styles.cycleInfoLabel}>Temp Shift</Text>
              <Text style={styles.cycleInfoValue}>
                {currentCycle.tempShift > 0 
                  ? `+${formatTemp(currentCycle.tempShift).replace('°', '°')}` 
                  : formatTemp(currentCycle.tempShift).replace('°', '°')}
              </Text>
            </View>
            <View style={styles.cycleInfoItem}>
              <Text style={styles.cycleInfoLabel}>Period Days</Text>
              <Text style={styles.cycleInfoValue}>{periodDays.length} days</Text>
            </View>
          </View>
        </View>
        
        {/* Basal Temperature Chart */}
        <View style={styles.chartCard}>
          <Text style={styles.chartTitle}>Basal Temperature Chart</Text>
          
          <View style={styles.chartContainer}>
            {temps.length > 0 ? (
              <VictoryChart
                width={width - 40}
                height={300}
                theme={VictoryTheme.material}
                domainPadding={{ x: 10, y: 15 }}
                padding={{ top: 20, right: 40, bottom: 50, left: 60 }}
                containerComponent={
                  <VictoryVoronoiContainer
                    labels={({ datum }) => `Day ${datum.x}: ${datum.y.toFixed(1)}°${unit}\n${datum.date}`}
                    labelComponent={<VictoryTooltip cornerRadius={5} flyoutStyle={{ fill: 'white' }} />}
                  />
                }
              >
                {/* Background for period days */}
                <VictoryArea
                  data={temps.filter(t => periodDays.includes(t.x))}
                  style={{
                    data: {
                      fill: COLORS.period + '20', // 20% opacity
                      stroke: "transparent"
                    }
                  }}
                />
                
                {/* Fertile threshold line */}
                <VictoryAxis
                  dependentAxis
                  orientation="right"
                  style={{
                    axis: { stroke: "transparent" },
                    ticks: { stroke: "transparent" },
                    tickLabels: { fill: "transparent" }
                  }}
                  tickValues={[fertileThreshold]}
                  tickFormat={() => ''}
                />
                
                {/* Fertile threshold area */}
                <VictoryArea
                  data={[
                    { x: temps[0]?.x || 0, y: fertileThreshold },
                    { x: temps[temps.length - 1]?.x || 14, y: fertileThreshold + 5 }
                  ]}
                  style={{
                    data: {
                      fill: COLORS.fertile + '30', // 30% opacity
                      stroke: "transparent"
                    }
                  }}
                />
                
                {/* X-axis (cycle days) */}
                <VictoryAxis
                  tickFormat={(x) => (periodDays.includes(x) ? `${x}🔴` : x)}
                  label="Cycle Day"
                  axisLabelComponent={<VictoryLabel dy={30} />}
                  style={{
                    axisLabel: { fontSize: 14, padding: 30 },
                    tickLabels: { 
                      fontSize: 10, 
                      padding: 5,
                      fill: (t) => periodDays.includes(t) ? COLORS.period : COLORS.text
                    },
                    grid: { stroke: COLORS.grid, strokeWidth: 0.5 }
                  }}
                />
                
                {/* Y-axis (temperature) */}
                <VictoryAxis
                  dependentAxis
                  label={`Temperature (°${unit})`}
                  axisLabelComponent={<VictoryLabel dy={-40} />}
                  style={{
                    axisLabel: { fontSize: 14, padding: 40 },
                    tickLabels: { fontSize: 10, padding: 5 },
                    grid: { stroke: COLORS.grid, strokeWidth: 0.5 }
                  }}
                />
                
                {/* Fertile threshold line */}
                <VictoryLine
                  data={[
                    { x: temps[0]?.x || 0, y: fertileThreshold },
                    { x: temps[temps.length - 1]?.x || 14, y: fertileThreshold }
                  ]}
                  style={{
                    data: { stroke: COLORS.fertile, strokeWidth: 1, strokeDasharray: '5,5' }
                  }}
                />
                
                {/* Follicular phase line */}
                <VictoryLine
                  data={follicularData}
                  style={{
                    data: { stroke: COLORS.follicular, strokeWidth: 2 }
                  }}
                />
                
                {/* Luteal phase line */}
                <VictoryLine
                  data={lutealData}
                  style={{
                    data: { stroke: COLORS.luteal, strokeWidth: 2 }
                  }}
                />
                
                {/* Data points */}
                <VictoryScatter
                  data={temps}
                  size={5}
                  style={{
                    data: {
                      fill: ({datum}) => datum.isPeriod ? COLORS.period : 
                        (datum.y >= fertileThreshold ? COLORS.luteal : COLORS.follicular),
                      stroke: COLORS.white,
                      strokeWidth: 1
                    }
                  }}
                />
                
                {/* Legend */}
                <VictoryLegend
                  x={width / 2 - 150}
                  y={270}
                  orientation="horizontal"
                  gutter={20}
                  colorScale={[COLORS.follicular, COLORS.luteal, COLORS.period, COLORS.fertile]}
                  data={[
                    { name: "Follicular", symbol: { type: "circle" } },
                    { name: "Luteal", symbol: { type: "circle" } },
                    { name: "Period", symbol: { type: "circle" } },
                    { name: "Fertile Threshold", symbol: { type: "line" } }
                  ]}
                  style={{
                    labels: { fontSize: 8 }
                  }}
                />
              </VictoryChart>
            ) : (
              <View style={styles.noDataContainer}>
                <Text style={styles.noDataText}>No temperature data for this cycle</Text>
              </View>
            )}
          </View>
        </View>
        
        {/* Pattern Analysis */}
        <View style={styles.statsCard}>
          <Text style={styles.statsTitle}>Cycle Analysis</Text>
          
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Avg Cycle Length</Text>
              <Text style={styles.statValue}>{data.stats.avgCycleLength.toFixed(1)} days</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Avg Temperature</Text>
              <Text style={styles.statValue}>{formatTemp(data.stats.avgTemperature)}</Text>
            </View>
          </View>
          
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Follicular Avg</Text>
              <Text style={styles.statValue}>
                {data.phaseAnalysis.follicular.avgTemp 
                  ? formatTemp(data.phaseAnalysis.follicular.avgTemp) 
                  : "N/A"}
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Luteal Avg</Text>
              <Text style={styles.statValue}>
                {data.phaseAnalysis.luteal.avgTemp 
                  ? formatTemp(data.phaseAnalysis.luteal.avgTemp) 
                  : "N/A"}
              </Text>
            </View>
          </View>
          
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Temp Shift</Text>
              <Text style={styles.statValue}>
                {data.stats.tempShift > 0 
                  ? `+${formatTemp(data.stats.tempShift).replace('°', '°')}` 
                  : formatTemp(data.stats.tempShift).replace('°', '°')}
              </Text>
            </View>
            <View style={styles.statItem}>
              <TouchableOpacity 
                style={styles.unitToggle}
                onPress={() => setUnit(unit === 'F' ? 'C' : 'F')}
              >
                <Text style={styles.unitToggleText}>
                  Switch to °{unit === 'F' ? 'C' : 'F'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.text,
    textAlign: 'center',
    marginTop: 5,
  },
  cycleSelector: {
    paddingVertical: 10,
    flexDirection: 'row',
  },
  cycleButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    backgroundColor: COLORS.white,
    borderRadius: 20,
    marginRight: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  selectedCycleButton: {
    backgroundColor: COLORS.follicular,
  },
  cycleButtonText: {
    color: COLORS.text,
    fontWeight: '500',
  },
  selectedCycleButtonText: {
    color: COLORS.white,
  },
  cycleInfoCard: {
    backgroundColor: COLORS.white,
    borderRadius: 10,
    padding: 15,
    marginVertical: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  cycleInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  cycleInfoItem: {
    flex: 1,
  },
  cycleInfoLabel: {
    fontSize: 12,
    color: COLORS.text + '80', // 80% opacity
    marginBottom: 2,
  },
  cycleInfoValue: {
    fontSize: 16,
    fontWeight: '500',
    color: COLORS.text,
  },
  chartCard: {
    backgroundColor: COLORS.white,
    borderRadius: 10,
    padding: 15,
    marginVertical: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 15,
  },
  chartContainer: {
    alignItems: 'center',
  },
  statsCard: {
    backgroundColor: COLORS.white,
    borderRadius: 10,
    padding: 15,
    marginVertical: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 15,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  statItem: {
    flex: 1,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.text + '80', // 80% opacity
    marginBottom: 2,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '500',
    color: COLORS.text,
  },
  unitToggle: {
    backgroundColor: COLORS.follicular + '20', // 20% opacity
    padding: 10,
    borderRadius: 5,
    alignItems: 'center',
  },
  unitToggleText: {
    color: COLORS.follicular,
    fontWeight: '500',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 10,
    color: COLORS.text,
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
    padding: 20,
  },
  errorText: {
    color: COLORS.period,
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: COLORS.follicular,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  },
  retryButtonText: {
    color: COLORS.white,
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  emptyText: {
    color: COLORS.text,
    fontSize: 16,
  },
  noDataContainer: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  noDataText: {
    color: COLORS.text + '80', // 80% opacity
    fontSize: 14,
  },
});

export default App; 