/**
 * Functions for menstrual cycle analysis and visualization
 */

// Improved function to detect ovulation day based on scientific criteria
function detectOvulationDay(data) {
    if (!data || !data.days || !data.temperatures || data.days.length < 8) {
        return null; // We need at least 8 days of data to detect a pattern
    }
    
    console.log("Detecting ovulation day with", data.days.length, "days of data");
    
    // Check if ovulation day is provided directly from the backend
    if (data.ovulationDay) {
        console.log("Using ovulation day provided by the backend:", data.ovulationDay);
        return data.ovulationDay;
    }
    
    const temps = data.temperatures.map(t => parseFloat(t));
    const days = data.days.map(d => parseInt(d));
    
    // Method 1: Detection by triphasic pattern (3 consecutive days with elevated temperature)
    for (let i = 2; i < temps.length - 2; i++) {
        // 1. Calculate the average of the previous 6 days
        let sixDaysBefore = temps.slice(Math.max(0, i-6), i);
        let beforeAvg = sixDaysBefore.reduce((a, b) => a + b, 0) / sixDaysBefore.length;
        
        // 2. Check if the next 3 days are all at least 0.2°F above the previous average
        let threeConsecutiveDaysHigher = true;
        for (let j = 0; j < 3; j++) {
            if (i + j >= temps.length || temps[i + j] < beforeAvg + 0.2) {
                threeConsecutiveDaysHigher = false;
                break;
            }
        }
        
        // 3. If the condition is met, the day before the first increase is the ovulation day
        if (threeConsecutiveDaysHigher && days[i] >= 8 && days[i] <= 20) {
            console.log("Ovulation day detected (triphasic pattern):", days[i-1]);
            return days[i-1];
        }
    }
    
    // Method 2: Detection by significant temperature change
    for (let i = 2; i < temps.length - 2; i++) {
        // Calculate average of 3 days before
        let beforeAvg = temps.slice(Math.max(0, i-3), i).reduce((a, b) => a + b, 0) / 
                    Math.min(3, Math.max(0, i-0));
        
        // Calculate average of 3 days after
        let afterAvg = temps.slice(i, Math.min(temps.length, i+3)).reduce((a, b) => a + b, 0) / 
                    Math.min(3, temps.length - i);
        
        // If there is a significant increase (>0.3°F) and we are between days 8-20
        if ((afterAvg - beforeAvg) >= 0.3 && days[i] >= 8 && days[i] <= 20) {
            console.log("Ovulation day detected (temperature change):", days[i]);
            console.log("Temp before:", beforeAvg, "Temp after:", afterAvg, "Difference:", afterAvg - beforeAvg);
            return days[i];
        }
    }
    
    // Method 3: Estimation based on typical cycle (day 14 in a 28-day cycle)
    // If the cycle is shorter or longer, adjust proportionally
    if (days.length > 0) {
        let lastDay = Math.max(...days);
        
        // If we are at least on day 10, use estimation based on typical cycle length
        if (lastDay >= 10) {
            // Estimate total cycle length (typical cycle = 28 days)
            let estimatedCycleLength = 28;
            
            // Estimate ovulation day (in a 28-day cycle, it's usually day 14)
            let estimatedOvulationDay = Math.round(estimatedCycleLength / 2);
            
            // If we've already passed more than half of the estimated cycle, adjust
            if (lastDay > estimatedOvulationDay) {
                estimatedOvulationDay = lastDay - 3; // Consider that ovulation has already occurred
            }
            
            console.log("Estimated ovulation day:", estimatedOvulationDay);
            return Math.min(estimatedOvulationDay, lastDay);
        }
    }
    
    // If detection was not possible, return null
    return null;
}

/**
 * Separates cycle data into follicular and luteal phases
 * @param {Object} cycleData - Cycle data
 * @returns {Object} Object with separated phases
 */
function separateCyclePhases(cycleData) {
    // Detect ovulation day
    const ovulationDay = detectOvulationDay(cycleData);
    console.log("Detected ovulation day:", ovulationDay);
    
    // Prepare arrays for each phase
    let follicularDays = [];
    let follicularTemps = [];
    let lutealDays = [];
    let lutealTemps = [];
    let fertileDays = [];
    let fertileTemps = [];
    
    // If we found the ovulation day, separate the phases
    if (ovulationDay !== null) {
        // Iterate through all days and assign them to the corresponding phase
        for (let i = 0; i < cycleData.days.length; i++) {
            const day = cycleData.days[i];
            const temp = parseFloat(cycleData.temperatures[i]);
            
            // Follicular phase - before ovulation
            if (day < ovulationDay) {
                follicularDays.push(day);
                follicularTemps.push(temp);
            } 
            // Ovulation day and luteal phase - after ovulation
            else {
                lutealDays.push(day);
                lutealTemps.push(temp);
            }
            
            // Fertile days - 5 days before and 1 day after ovulation
            if (day >= ovulationDay - 5 && day <= ovulationDay + 1) {
                fertileDays.push(day);
                fertileTemps.push(temp);
            }
        }
    } 
    // If there is no ovulation day, use an estimate based on cycle length
    else {
        // The luteal phase usually lasts ~14 days, the follicular phase varies more
        // Estimate ovulation day as: cycle length - 14 (if the cycle is long)
        // Or simply use half of the cycle as an estimate for shorter cycles
        let estimatedOvulationDay;
        if (cycleData.days.length > 0) {
            const lastDay = Math.max(...cycleData.days);
            if (lastDay > 20) {
                // For long cycles, estimate ovulation: total length - 14
                estimatedOvulationDay = Math.max(10, lastDay - 14);
            } else {
                // For short or in-progress cycles, use half
                estimatedOvulationDay = Math.round(lastDay / 2);
            }
        } else {
            estimatedOvulationDay = 14; // Default for 28-day cycles
        }
        
        console.log("Using estimated ovulation day:", estimatedOvulationDay);
        
        // Iterate through all days and assign them to the corresponding phase
        for (let i = 0; i < cycleData.days.length; i++) {
            const day = cycleData.days[i];
            const temp = parseFloat(cycleData.temperatures[i]);
            
            // Use the estimate to separate phases
            if (day < estimatedOvulationDay) {
                follicularDays.push(day);
                follicularTemps.push(temp);
            } else {
                lutealDays.push(day);
                lutealTemps.push(temp);
            }
            
            // Estimate fertile days
            if (day >= estimatedOvulationDay - 5 && day <= estimatedOvulationDay + 1) {
                fertileDays.push(day);
                fertileTemps.push(temp);
            }
        }
    }
    
    // Calculate averages for each phase
    let follicularAvg = follicularTemps.length > 0 ? 
        follicularTemps.reduce((a, b) => a + b, 0) / follicularTemps.length : 97.5;
    let lutealAvg = lutealTemps.length > 0 ? 
        lutealTemps.reduce((a, b) => a + b, 0) / lutealTemps.length : 98.1;
    
    return {
        follicular: {
            days: follicularDays,
            temps: follicularTemps,
            avg: follicularAvg
        },
        luteal: {
            days: lutealDays,
            temps: lutealTemps,
            avg: lutealAvg
        },
        fertile: {
            days: fertileDays,
            temps: fertileTemps
        },
        ovulationDay: ovulationDay
    };
} 