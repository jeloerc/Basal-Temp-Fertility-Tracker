// Main script for the Basal Temperature Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Highlight the current day in the table
    highlightCurrentDay();
    
    // Temperature validation
    setupTemperatureValidation();
    
    // Confirmation for the reset button
    setupResetConfirmation();
    
    // Responsive chart management
    setupResponsiveChart();
    
    // Setup page navigation
    setupPageNavigation();
});

// Highlights the current day in the history table
function highlightCurrentDay() {
    const temperatureTable = document.querySelector('table.table');
    if (!temperatureTable) return;
    
    const rows = temperatureTable.querySelectorAll('tbody tr');
    const dayCounter = document.querySelector('label[for="temperature"]')?.textContent;
    
    if (!dayCounter) return;
    
    const currentDay = parseInt(dayCounter.match(/\d+/)[0]) - 1;
    
    rows.forEach(row => {
        const dayCell = row.querySelector('td:first-child');
        if (dayCell && parseInt(dayCell.textContent) === currentDay) {
            row.classList.add('current-day');
        }
    });
}

// Temperature input validation
function setupTemperatureValidation() {
    const temperatureInput = document.getElementById('temperature');
    if (!temperatureInput) return;
    
    temperatureInput.addEventListener('input', function() {
        const value = parseFloat(this.value);
        if (isNaN(value)) return;
        
        // Validation for unlikely temperatures
        if (value < 95 || value > 104) {
            this.classList.add('is-invalid');
            
            // Create or update error message
            let errorMessage = this.nextElementSibling;
            if (!errorMessage || !errorMessage.classList.contains('invalid-feedback')) {
                errorMessage = document.createElement('div');
                errorMessage.classList.add('invalid-feedback');
                this.parentNode.appendChild(errorMessage);
            }
            
            errorMessage.textContent = 'The temperature appears to be outside the normal human range.';
        } else {
            this.classList.remove('is-invalid');
            const errorMessage = this.nextElementSibling;
            if (errorMessage && errorMessage.classList.contains('invalid-feedback')) {
                errorMessage.remove();
            }
        }
    });
}

// Confirmation before resetting cycle
function setupResetConfirmation() {
    const resetForm = document.querySelector('form[action*="reset_cycle"]');
    if (!resetForm) return;
    
    resetForm.addEventListener('submit', function(e) {
        if (!confirm('Are you sure you want to start a new cycle? This will reset the day counter.')) {
            e.preventDefault();
        }
    });
}

// Setting up the responsive chart
function setupResponsiveChart() {
    const chartContainer = document.getElementById('temperature-chart');
    if (!chartContainer) return;
    
    // If ECharts is available, ensure the chart resizes
    if (window.echarts) {
        const chart = echarts.getInstanceByDom(chartContainer);
        if (chart) {
            const resizeObserver = new ResizeObserver(() => {
                chart.resize();
            });
            
            resizeObserver.observe(chartContainer);
        }
    }
}

// Setup navigation between pages
function setupPageNavigation() {
    // Add active class to current page link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = new URL(link.href, window.location.origin).pathname;
        if (linkPath === currentPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        } else {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
        }
    });
}

// Main JavaScript file for Basal Temperature Tracker
// Enhanced for mobile devices 