/**
 * JavaScript file for temperature record editing functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Temperature edit script loaded');
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Detect edit buttons
    const editButtons = document.querySelectorAll('.edit-btn');
    console.log('Edit buttons found:', editButtons.length);
    
    // Handle edit button clicks
    editButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            console.log('Edit button clicked');
            e.preventDefault();
            
            const date = this.getAttribute('data-date');
            const rowId = this.getAttribute('data-row-id');
            console.log('Record date:', date, 'Row ID:', rowId);
            
            // Find the row using data-row-id instead of ID
            const rows = document.querySelectorAll('[data-row-id="' + rowId + '"]');
            const row = rows[0];
            
            if (!row) {
                console.error('Row not found for rowId:', rowId);
                return;
            }
            
            console.log('Row found, showing edit inputs');
            
            // Show edit inputs
            row.querySelectorAll('.temp-value, .mucus-value, .mood-value, .comment-value').forEach(function(el) {
                el.classList.add('d-none');
            });
            
            row.querySelectorAll('.edit-temp, .edit-mucus, .edit-mood, .edit-comment, .edit-cycle-day').forEach(function(el) {
                el.classList.remove('d-none');
            });
            
            // Show/hide buttons
            this.classList.add('d-none');
            row.querySelector('.save-btn').classList.remove('d-none');
            row.querySelector('.cancel-btn').classList.remove('d-none');
            row.querySelector('.delete-btn').classList.add('d-none');
        });
    });
    
    // Handle cancel button clicks
    document.querySelectorAll('.cancel-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            console.log('Cancel button clicked');
            e.preventDefault();
            
            const rowId = this.getAttribute('data-row-id');
            
            // Find the row using data-row-id
            const rows = document.querySelectorAll('[data-row-id="' + rowId + '"]');
            const row = rows[0];
            
            // Hide edit inputs
            row.querySelectorAll('.temp-value, .mucus-value, .mood-value, .comment-value').forEach(function(el) {
                el.classList.remove('d-none');
            });
            
            row.querySelectorAll('.edit-temp, .edit-mucus, .edit-mood, .edit-comment, .edit-cycle-day').forEach(function(el) {
                el.classList.add('d-none');
            });
            
            // Show/hide buttons
            row.querySelector('.edit-btn').classList.remove('d-none');
            row.querySelector('.save-btn').classList.add('d-none');
            row.querySelector('.cancel-btn').classList.add('d-none');
            row.querySelector('.delete-btn').classList.remove('d-none');
        });
    });
    
    // Handle save button clicks
    document.querySelectorAll('.save-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            console.log('Save button clicked');
            e.preventDefault();
            
            const date = this.getAttribute('data-date');
            const rowId = this.getAttribute('data-row-id');
            
            // Find the row using data-row-id
            const rows = document.querySelectorAll('[data-row-id="' + rowId + '"]');
            const row = rows[0];
            
            const saveBtn = this;
            
            // Disable button and show loading indicator
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            
            // Collect edited values
            const temperature = row.querySelector('.temp-input').value;
            const cycle_day = row.querySelector('.cycle-day-input').value;
            const mucus_type = row.querySelector('.mucus-input').value;
            const mood = row.querySelector('.mood-input').value;
            const comment = row.querySelector('.comment-input').value;
            
            console.log('Data to send:', {
                date, temperature, cycle_day, mucus_type, mood, comment
            });
            
            // Send data using fetch API
            fetch('/update_record', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: date,
                    temperature: temperature,
                    cycle_day: cycle_day,
                    mucus_type: mucus_type,
                    mood: mood,
                    comment: comment
                })
            })
            .then(response => {
                console.log('Response received:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                
                if (data.success) {
                    // Update displayed values
                    row.querySelector('.temp-value').textContent = parseFloat(temperature).toFixed(2) + '°F';
                    row.querySelector('.mucus-value').textContent = mucus_type || 'Not recorded';
                    row.querySelector('.mood-value').textContent = mood || 'Not recorded';
                    row.querySelector('.comment-value').textContent = comment || '';
                    
                    // Update cycle day badge
                    const badgeText = 'Day ' + cycle_day;
                    const cycleBadge = row.querySelector('.badge');
                    cycleBadge.textContent = badgeText;
                    
                    if (cycle_day == 1) {
                        cycleBadge.classList.remove('bg-secondary');
                        cycleBadge.classList.add('bg-danger');
                    } else {
                        cycleBadge.classList.remove('bg-danger');
                        cycleBadge.classList.add('bg-secondary');
                    }
                    
                    // Update fertile/non-fertile status
                    const statusBadge = row.querySelectorAll('.badge')[1];
                    if (parseFloat(temperature) >= 98.6) {
                        statusBadge.classList.remove('bg-secondary');
                        statusBadge.classList.add('bg-success');
                        statusBadge.textContent = 'Fertile';
                    } else {
                        statusBadge.classList.remove('bg-success');
                        statusBadge.classList.add('bg-secondary');
                        statusBadge.textContent = 'Non-Fertile';
                    }
                    
                    // Hide edit inputs
                    row.querySelectorAll('.temp-value, .mucus-value, .mood-value, .comment-value').forEach(function(el) {
                        el.classList.remove('d-none');
                    });
                    
                    row.querySelectorAll('.edit-temp, .edit-mucus, .edit-mood, .edit-comment, .edit-cycle-day').forEach(function(el) {
                        el.classList.add('d-none');
                    });
                    
                    // Show/hide buttons
                    row.querySelector('.edit-btn').classList.remove('d-none');
                    row.querySelector('.save-btn').classList.add('d-none');
                    row.querySelector('.cancel-btn').classList.add('d-none');
                    row.querySelector('.delete-btn').classList.remove('d-none');
                    
                    // Show success message
                    showAlert('Record updated successfully', 'success');
                } else {
                    console.error('Error in response:', data.message);
                    showAlert('Error: ' + data.message, 'danger');
                    // Restore save button
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Save';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error updating record', 'danger');
                // Restore save button
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="fas fa-save"></i> Save';
            });
        });
    });
    
    // Handle delete button clicks
    document.querySelectorAll('.delete-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            console.log('Delete button clicked');
            e.preventDefault();
            
            if (!confirm('Are you sure you want to delete this record? This action cannot be undone.')) {
                return;
            }
            
            const date = this.getAttribute('data-date');
            const rowId = this.getAttribute('data-row-id');
            
            // Find the row using data-row-id
            const rows = document.querySelectorAll('[data-row-id="' + rowId + '"]');
            const row = rows[0];
            
            const deleteBtn = this;
            
            // Disable button and show loading indicator
            deleteBtn.disabled = true;
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            fetch('/delete_record', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: date
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Delete response:', data);
                
                if (data.success) {
                    // Remove the row from the table
                    row.style.transition = 'opacity 0.3s';
                    row.style.opacity = '0';
                    setTimeout(function() {
                        row.remove();
                        
                        // If no records left, show message
                        if (document.querySelectorAll('tbody tr').length === 0) {
                            const emptyRow = document.createElement('tr');
                            emptyRow.innerHTML = '<td colspan="9" class="text-center">No records available</td>';
                            document.querySelector('tbody').appendChild(emptyRow);
                        }
                    }, 300);
                    
                    showAlert('Record deleted successfully', 'success');
                } else {
                    console.error('Error deleting:', data.message);
                    showAlert('Error: ' + data.message, 'danger');
                    // Restore delete button
                    deleteBtn.disabled = false;
                    deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Delete';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error deleting record', 'danger');
                // Restore delete button
                deleteBtn.disabled = false;
                deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Delete';
            });
        });
    });
    
    // Function to show alerts
    function showAlert(message, type) {
        console.log('Showing alert:', message, type);
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        const alertContainer = document.createElement('div');
        alertContainer.innerHTML = alertHtml;
        
        const container = document.querySelector('.container');
        const row = container.querySelector('.row');
        container.insertBefore(alertContainer.firstChild, row);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(function(alert) {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) closeBtn.click();
            });
        }, 5000);
    }
}); 