document.addEventListener('DOMContentLoaded', function() {
    // Check if we have a chart element and data
    var chartDom = document.getElementById('temperature-chart');
    if (!chartDom || !window.initialChartData) return;
    
    var myChart = echarts.init(chartDom);
    var chartData = window.initialChartData;
    
    function updateChart(data) {
        console.log("Updating chart with data:", data);
        
        if (!data || !data.xAxis || !data.tempData || data.xAxis.length === 0) {
            console.error("Invalid chart data:", data);
            chartDom.innerHTML = '<div class="alert alert-warning my-3 p-3">No data available for this selection</div>';
            return;
        }
        
        try {
            // Ensure all temperature values have exactly 2 decimal places
            if (data.tempData && Array.isArray(data.tempData)) {
                data.tempData = data.tempData.map(function(temp) {
                    return parseFloat(parseFloat(temp).toFixed(2));
                });
            }
            
            // Process and clean the data 
            var processedData = processChartData(data);
            
            // If no valid data after processing, show message
            if (!processedData || !processedData.days || processedData.days.length === 0) {
                chartDom.innerHTML = '<div class="alert alert-warning my-3 p-3">No valid data available for this selection</div>';
                return;
            }
            
            var option = {
                title: {
                    text: 'Temperature Chart',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function(params) {
                        try {
                            var dayNum = params[0].axisValue;
                            var dataIndex = processedData.dayToIndexMap[dayNum];
                            
                            if (dataIndex === undefined) {
                                return 'Cycle Day ' + dayNum + '<br/>No data available';
                            }
                            
                            var dateStr = processedData.dates && processedData.dates[dataIndex] || '';
                            var isFertileDay = processedData.fertileDays && processedData.fertileDays.includes(Number(dayNum));
                            var isPeriodDay = processedData.isPeriod && processedData.isPeriod[dataIndex];
                            var isOvulationDay = processedData.ovulationDay && processedData.ovulationDay === Number(dayNum);
                            
                            var statusText = '';
                            if (isOvulationDay) statusText = ' (Ovulation Day)';
                            else if (isFertileDay) statusText = ' (Fertile Window)';
                            if (isPeriodDay) statusText = ' (Period)';
                            
                            // Check if params has valid value
                            var tempValue = params[0].value;
                            var tempStr = typeof tempValue === 'number' ? tempValue.toFixed(2) + '°F' : 'N/A';
                            
                            return 'Cycle Day ' + dayNum + '<br/>Date: ' + dateStr + '<br/>Temp: ' + tempStr + statusText;
                        } catch (e) {
                            console.error("Error in tooltip formatter:", e);
                            return 'Error displaying data';
                        }
                    }
                },
                legend: {
                    data: ['Temperature'],
                    bottom: 10
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '15%',
                    containLabel: true
                },
                toolbox: {
                    feature: {
                        saveAsImage: {},
                        dataZoom: {},
                        restore: {}
                    }
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: processedData.days,
                    name: 'Cycle Day',
                    nameLocation: 'middle',
                    nameGap: 30,
                    axisLabel: {
                        formatter: function(value) {
                            return 'Day ' + value;
                        },
                        interval: 'auto'
                    }
                },
                yAxis: {
                    type: 'value',
                    name: 'Temperature (°F)',
                    nameLocation: 'middle',
                    nameGap: 50,
                    min: processedData.minTemp,
                    max: processedData.maxTemp
                },
                dataZoom: [
                    {
                        type: 'inside',
                        start: 0,
                        end: 100
                    },
                    {
                        start: 0,
                        end: 100
                    }
                ],
                series: [
                    {
                        name: 'Temperature',
                        type: 'line',
                        smooth: true,
                        data: processedData.tempSeries,
                        markArea: {
                            silent: true,
                            itemStyle: {
                                opacity: 0.25,
                                color: '#ff4081'
                            },
                            data: getFertileAreaData(processedData.fertileDays)
                        },
                        markLine: getOvulationMarkLine(processedData.ovulationDay),
                        itemStyle: {
                            // Color points based on period 
                            color: function(params) {
                                try {
                                    var dayIndex = params.dataIndex;
                                    var dayValue = processedData.days[dayIndex];
                                    // Si es el día de ovulación, color específico
                                    if (processedData.ovulationDay && dayValue === processedData.ovulationDay) {
                                        return '#ff9800'; // Color naranja para día de ovulación
                                    }
                                    // Si es día de período
                                    if (dayIndex !== undefined && processedData.isPeriodSeries && processedData.isPeriodSeries[dayIndex]) {
                                        return '#e91e63'; // Period days
                                    }
                                    // Si es día fértil
                                    if (processedData.fertileDays && processedData.fertileDays.includes(dayValue)) {
                                        return '#9c27b0'; // Fertile days
                                    }
                                    return '#7c4dff'; // Regular days
                                } catch (e) {
                                    console.error("Error in color function:", e);
                                    return '#7c4dff'; // Default color
                                }
                            }
                        },
                        lineStyle: {
                            width: 3
                        },
                        symbol: 'circle',
                        symbolSize: function(value, params) {
                            // Si es día de ovulación, hacerlo más grande
                            var dayValue = processedData.days[params.dataIndex];
                            if (processedData.ovulationDay && dayValue === processedData.ovulationDay) {
                                return 12; // Tamaño más grande para el día de ovulación
                            }
                            return 8; // Tamaño normal
                        },
                        connectNulls: true
                    }
                ]
            };
            
            // Check if it's a specific cycle and set the subtitle
            if (processedData.cycleStartDate) {
                option.title.subtext = 'Started: ' + formatDate(processedData.cycleStartDate);
            }
            
            // Handle empty charts
            if (myChart._disposed) {
                myChart = echarts.init(chartDom);
            }
            
            myChart.setOption(option, true);
        } catch (error) {
            console.error("Error creating chart:", error);
            chartDom.innerHTML = '<div class="alert alert-danger my-3 p-3">Error displaying chart: ' + error.message + '</div>';
        }
    }
    
    // Process and clean chart data
    function processChartData(data) {
        // Create a map to track day indices
        var dayToIndexMap = {};
        var processedDays = [];
        var tempSeries = [];
        var isPeriodSeries = [];
        var uniqueDays = new Set();
        
        // Check if data exists and has valid structure
        if (!data || !data.xAxis || !data.tempData || data.xAxis.length === 0) {
            console.error("Invalid data structure:", data);
            return {
                days: [],
                tempSeries: [],
                isPeriodSeries: [],
                dates: [],
                isPeriod: [],
                minTemp: 97.0,
                maxTemp: 99.0,
                fertileDays: [],
                ovulationDay: null,
                cycleStartDate: null,
                dayToIndexMap: {}
            };
        }
        
        // First, identify all unique cycle days
        for (var i = 0; i < data.xAxis.length; i++) {
            var day = Number(data.xAxis[i]);
            // Skip invalid days
            if (isNaN(day)) {
                console.warn("Invalid cycle day value at index", i, ":", data.xAxis[i]);
                continue;
            }
            
            if (!uniqueDays.has(day)) {
                uniqueDays.add(day);
                processedDays.push(day);
                
                // Create a mapping of day to index in our processed arrays
                dayToIndexMap[day] = processedDays.length - 1;
                
                // Add the temperature and period data
                tempSeries.push({
                    value: parseFloat(parseFloat(data.tempData[i]).toFixed(2)),
                    day: day
                });
                
                isPeriodSeries.push(data.isPeriod ? data.isPeriod[i] : false);
            } else {
                console.warn("Duplicate cycle day found:", day, "at index", i);
                // For duplicate days, we'll keep the one with higher temperature
                var existingIndex = processedDays.indexOf(day);
                if (existingIndex >= 0 && data.tempData[i] > tempSeries[existingIndex].value) {
                    tempSeries[existingIndex] = {
                        value: parseFloat(parseFloat(data.tempData[i]).toFixed(2)),
                        day: day
                    };
                    isPeriodSeries[existingIndex] = data.isPeriod ? data.isPeriod[i] : false;
                }
            }
        }
        
        // If no valid days were found, return empty data
        if (processedDays.length === 0) {
            console.error("No valid days found in data");
            return {
                days: [],
                tempSeries: [],
                isPeriodSeries: [],
                dates: [],
                isPeriod: [],
                minTemp: 97.0,
                maxTemp: 99.0,
                fertileDays: [],
                ovulationDay: null,
                cycleStartDate: null,
                dayToIndexMap: {}
            };
        }
        
        // Sort the days in ascending order
        processedDays.sort(function(a, b) { return a - b; });
        
        // Reorder temperature and period data based on sorted days
        var sortedTempSeries = [];
        var sortedIsPeriodSeries = [];
        
        for (var i = 0; i < processedDays.length; i++) {
            var day = processedDays[i];
            var oldIndex = dayToIndexMap[day];
            if (oldIndex !== undefined && tempSeries[oldIndex]) {
                sortedTempSeries.push(tempSeries[oldIndex].value);
                sortedIsPeriodSeries.push(isPeriodSeries[oldIndex]);
                // Update the index mapping
                dayToIndexMap[day] = i;
            } else {
                console.warn("Missing data for day", day);
                sortedTempSeries.push(null);
                sortedIsPeriodSeries.push(false);
            }
        }
        
        // Determine min and max temperatures from the valid data
        var validTemps = sortedTempSeries.filter(function(temp) { return temp !== null; });
        var minTemp = validTemps.length > 0 ? parseFloat((Math.min(...validTemps) - 0.2).toFixed(2)) : 97.0;
        var maxTemp = validTemps.length > 0 ? parseFloat((Math.max(...validTemps) + 0.2).toFixed(2)) : 99.0;
        
        // Get the ovulation day if it exists in the data
        var ovulationDay = data.ovulationDay || null;
        
        return {
            days: processedDays,
            tempSeries: sortedTempSeries,
            isPeriodSeries: sortedIsPeriodSeries,
            dates: data.dates,
            isPeriod: data.isPeriod,
            minTemp: minTemp,
            maxTemp: maxTemp,
            fertileDays: data.fertileDays || [],
            ovulationDay: ovulationDay,
            cycleStartDate: data.cycleStartDate,
            dayToIndexMap: dayToIndexMap
        };
    }
    
    // Generate data for fertile window area
    function getFertileAreaData(fertileDays) {
        // Si no hay días fértiles o el arreglo está vacío, devolver un arreglo vacío
        if (!fertileDays || !Array.isArray(fertileDays) || fertileDays.length === 0) {
            return [];
        }
        
        // Agrupar días fértiles consecutivos en rangos
        var ranges = [];
        var currentRange = [fertileDays[0]];
        
        for (var i = 1; i < fertileDays.length; i++) {
            // Si el día actual es consecutivo al anterior, añadirlo al rango actual
            if (fertileDays[i] === fertileDays[i-1] + 1) {
                currentRange.push(fertileDays[i]);
            } else {
                // Si no es consecutivo, finalizar el rango actual y comenzar uno nuevo
                ranges.push(currentRange);
                currentRange = [fertileDays[i]];
            }
        }
        
        // Añadir el último rango
        if (currentRange.length > 0) {
            ranges.push(currentRange);
        }
        
        // Crear áreas para cada rango de días fértiles
        var areaData = [];
        
        ranges.forEach(function(range) {
            // Si el rango tiene al menos un día
            if (range.length > 0) {
                areaData.push([
                    {
                        xAxis: Math.min(...range) - 0.5,
                        itemStyle: {
                            color: 'rgba(255, 64, 129, 0.4)',  // Color más visible (rosa fuerte con mayor opacidad)
                            borderColor: '#ff4081',
                            borderWidth: 1,
                            shadowBlur: 5,
                            shadowColor: 'rgba(255, 64, 129, 0.5)'
                        }
                    },
                    {
                        xAxis: Math.max(...range) + 0.5,
                        itemStyle: {
                            color: 'rgba(255, 64, 129, 0.4)',
                            borderColor: '#ff4081',
                            borderWidth: 1
                        }
                    }
                ]);
            }
        });
        
        return areaData;
    }
    
    // Función para crear la línea de marcado del día de ovulación
    function getOvulationMarkLine(ovulationDay) {
        if (!ovulationDay) {
            return { silent: true, data: [] };
        }
        
        return {
            silent: true,
            symbol: ['none', 'triangle'],
            symbolSize: [0, 15],
            lineStyle: {
                color: '#ff9800',
                type: 'dashed',
                width: 2
            },
            label: {
                show: true,
                position: 'end',
                formatter: 'Ovulation Day'
            },
            data: [
                {
                    name: 'Ovulation',
                    xAxis: ovulationDay,
                    label: {
                        formatter: 'Ovulation Day',
                        position: 'insideEndTop'
                    }
                }
            ]
        };
    }
    
    // Format date for display
    function formatDate(dateStr) {
        if (!dateStr) return '';
        
        var date = new Date(dateStr);
        if (isNaN(date.getTime())) return dateStr;
        
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
    
    // Initial chart
    updateChart(chartData);
    
    // Handle cycle selector change
    var cycleSelector = document.getElementById('cycle-selector');
    if (cycleSelector) {
        cycleSelector.addEventListener('change', function() {
            var cycleId = this.value;
            
            // Show loading indicator
            myChart.dispose();
            chartDom.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading data...</p></div>';
            
            // Function to handle errors
            function handleError(error) {
                console.error('Error loading cycle data:', error);
                chartDom.innerHTML = '<div class="alert alert-danger my-3 p-3">Error loading data. Please try again later.</div>';
            }
            
            if (cycleId === 'all') {
                // Show all data
                fetch('/api/chart_data/all')
                    .then(function(response) { 
                        if (!response.ok) {
                            throw new Error('Server returned ' + response.status);
                        }
                        return response.json(); 
                    })
                    .then(function(data) {
                        if (data && !data.error) {
                            chartDom.innerHTML = '';
                            myChart = echarts.init(chartDom);
                            updateChart(data);
                        } else {
                            handleError(data.error || 'Invalid data format');
                        }
                    })
                    .catch(handleError);
            } else if (cycleId === 'current') {
                // Fetch current cycle data
                fetch('/api/current_cycle_data')
                    .then(function(response) { 
                        if (!response.ok) {
                            throw new Error('Server returned ' + response.status);
                        }
                        return response.json(); 
                    })
                    .then(function(data) {
                        if (data) {
                            // Format the data for the chart
                            var formattedData = {
                                xAxis: data.days,
                                tempData: data.temperatures,
                                dates: data.dates,
                                isPeriod: data.isPeriod,
                                minTemp: data.minTemp,
                                maxTemp: data.maxTemp,
                                fertileDays: data.fertileDays,
                                cycleStartDate: data.cycleStartDate
                            };
                            chartDom.innerHTML = '';
                            myChart = echarts.init(chartDom);
                            updateChart(formattedData);
                        } else {
                            chartDom.innerHTML = '<div class="alert alert-warning my-3 p-3">No data available for the current cycle</div>';
                        }
                    })
                    .catch(handleError);
            } else {
                // Fetch specific cycle data
                fetch('/api/chart_data/' + cycleId)
                    .then(function(response) { 
                        if (!response.ok) {
                            throw new Error('Server returned ' + response.status);
                        }
                        return response.json(); 
                    })
                    .then(function(data) {
                        if (data && !data.error) {
                            chartDom.innerHTML = '';
                            myChart = echarts.init(chartDom);
                            updateChart(data);
                        } else {
                            chartDom.innerHTML = '<div class="alert alert-warning my-3 p-3">No data available for this cycle</div>';
                        }
                    })
                    .catch(handleError);
            }
        });
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (myChart) myChart.resize();
    });
}); 