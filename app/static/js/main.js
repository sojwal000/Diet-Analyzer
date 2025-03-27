// Main JavaScript for Diet Analyzer

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize macro chart if element exists
    const macroChartElement = document.getElementById('macroChart');
    if (macroChartElement) {
        const protein = parseFloat(macroChartElement.getAttribute('data-protein') || 0);
        const carbs = parseFloat(macroChartElement.getAttribute('data-carbs') || 0);
        const fats = parseFloat(macroChartElement.getAttribute('data-fats') || 0);
        
        new Chart(macroChartElement, {
            type: 'doughnut',
            data: {
                labels: ['Protein', 'Carbs', 'Fats'],
                datasets: [{
                    data: [protein, carbs, fats],
                    backgroundColor: ['#0dcaf0', '#198754', '#ffc107'],
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Macro Distribution'
                    }
                }
            }
        });
    }

    // Date picker for meal logs
    const datePicker = document.getElementById('logDatePicker');
    if (datePicker) {
        datePicker.addEventListener('change', function() {
            window.location.href = `/nutrition/meal-logs?date=${this.value}`;
        });
    }

    // Food search form
    const foodSearchForm = document.getElementById('foodSearchForm');
    if (foodSearchForm) {
        foodSearchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('query');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a food to search for');
            }
        });
    }

    // Meal plan save form validation
    const savePlanForm = document.getElementById('savePlanForm');
    if (savePlanForm) {
        savePlanForm.addEventListener('submit', function(e) {
            const planName = document.getElementById('plan_name');
            if (!planName.value.trim()) {
                e.preventDefault();
                alert('Please enter a name for your diet plan');
            }
        });
    }
});