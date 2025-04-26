/**
 * Initializes the menstrual cycle phase charts
 * @param {object} cycleData - Menstrual cycle data
 */
function initPhasesCharts(cycleData) {
    try {
        // Separate cycle data into phases
        const cyclePhases = separateCyclePhases(cycleData);
        console.log("Cycle phases:", cyclePhases);
        
        // Check that containers exist before initializing charts
        const follicularChartDom = document.getElementById('follicular-phase-chart');
        const lutealChartDom = document.getElementById('luteal-phase-chart');
        
        if (!follicularChartDom || !lutealChartDom) {
            console.error("Chart containers not found");
            return;
        }
        
        // Initialize follicular phase chart
        initFollicularChart(follicularChartDom, cyclePhases.follicular);
        
        // Initialize luteal phase chart
        initLutealChart(lutealChartDom, cyclePhases.luteal);
        
    } catch (error) {
        console.error("Error initializing phase charts:", error);
    }
}

/**
 * Initializes the follicular phase chart
 * @param {HTMLElement} container - Chart container
 * @param {object} follicularData - Follicular phase data
 */
function initFollicularChart(container, follicularData) {
    if (!follicularData || !follicularData.days || follicularData.days.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Not enough data for follicular phase</div>';
        return;
    }
    
    // Create data for follicular chart
    const chartData = follicularData.days.map((day, idx) => {
        return {
            day: day,
            temp: follicularData.temps[idx]
        };
    });
    
    // Sort data by day
    chartData.sort((a, b) => a.day - b.day);
    
    // Create chart
    const follicularChart = echarts.init(container);
    
    const follicularOption = {
        title: {
            text: 'Follicular Phase',
            left: 'center',
            subtext: 'Average: ' + follicularData.avg.toFixed(2) + '°F'
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return 'Day ' + params[0].name + ': ' + params[0].value.toFixed(2) + '°F';
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: chartData.map(item => item.day),
            name: 'Cycle Day',
            nameLocation: 'middle',
            nameGap: 30,
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: 'Temperature (°F)',
            min: function(value) {
                const minTemp = Math.min(...follicularData.temps);
                return Math.floor((minTemp - 0.2) * 10) / 10;
            },
            max: function(value) {
                const maxTemp = Math.max(...follicularData.temps);
                return Math.ceil((maxTemp + 0.2) * 10) / 10;
            },
            axisLabel: {
                formatter: '{value}°F'
            }
        },
        series: [
            {
                name: 'Temperature',
                type: 'line',
                data: chartData.map(item => item.temp),
                color: '#2196f3',
                symbol: 'circle',
                symbolSize: 8,
                markLine: {
                    silent: true,
                    lineStyle: {
                        color: '#2196f3',
                        type: 'dashed',
                        width: 1
                    },
                    data: [
                        {
                            yAxis: follicularData.avg,
                            name: 'Average',
                            label: {
                                formatter: 'Average: {c}°F',
                                position: 'insideEndTop'
                            }
                        }
                    ]
                }
            }
        ]
    };
    
    follicularChart.setOption(follicularOption);
    
    // Resize when window size changes
    window.addEventListener('resize', function() {
        follicularChart.resize();
    });
}

/**
 * Initializes the luteal phase chart
 * @param {HTMLElement} container - Chart container
 * @param {object} lutealData - Luteal phase data
 */
function initLutealChart(container, lutealData) {
    if (!lutealData || !lutealData.days || lutealData.days.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Not enough data for luteal phase</div>';
        return;
    }
    
    // Create data for luteal chart
    const chartData = lutealData.days.map((day, idx) => {
        return {
            day: day,
            temp: lutealData.temps[idx]
        };
    });
    
    // Sort data by day
    chartData.sort((a, b) => a.day - b.day);
    
    // Create chart
    const lutealChart = echarts.init(container);
    
    const lutealOption = {
        title: {
            text: 'Luteal Phase',
            left: 'center',
            subtext: 'Average: ' + lutealData.avg.toFixed(2) + '°F'
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return 'Day ' + params[0].name + ': ' + params[0].value.toFixed(2) + '°F';
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: chartData.map(item => item.day),
            name: 'Cycle Day',
            nameLocation: 'middle',
            nameGap: 30,
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: 'Temperature (°F)',
            min: function(value) {
                const minTemp = Math.min(...lutealData.temps);
                return Math.floor((minTemp - 0.2) * 10) / 10;
            },
            max: function(value) {
                const maxTemp = Math.max(...lutealData.temps);
                return Math.ceil((maxTemp + 0.2) * 10) / 10;
            },
            axisLabel: {
                formatter: '{value}°F'
            }
        },
        series: [
            {
                name: 'Temperature',
                type: 'line',
                data: chartData.map(item => item.temp),
                color: '#4caf50',
                symbol: 'circle',
                symbolSize: 8,
                markLine: {
                    silent: true,
                    lineStyle: {
                        color: '#4caf50',
                        type: 'dashed',
                        width: 1
                    },
                    data: [
                        {
                            yAxis: lutealData.avg,
                            name: 'Average',
                            label: {
                                formatter: 'Average: {c}°F',
                                position: 'insideEndTop'
                            }
                        }
                    ]
                }
            }
        ]
    };
    
    lutealChart.setOption(lutealOption);
    
    // Resize when window size changes
    window.addEventListener('resize', function() {
        lutealChart.resize();
    });
} 