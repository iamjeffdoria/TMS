function setQuickFilter(period) {
    const today = new Date();
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    endDateInput.value = today.toISOString().split('T')[0];
    let startDate = new Date();
    
    switch(period) {
        case 'today':
            startDate = new Date(today);
            break;
        case 'week':
            startDate.setDate(today.getDate() - 7);
            break;
        case 'month':
            startDate.setMonth(today.getMonth() - 1);
            break;
        case 'year':
            startDate.setFullYear(today.getFullYear() - 1);
            break;
    }
    
    if (startDateInput) {
        startDateInput.value = startDate.toISOString().split('T')[0];
    }
}

function resetFilters() {
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.reset();
    }
    window.location.href = window.location.pathname;
}

// Preserve filter values on page load
window.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const filterType = document.getElementById('filterType');
    const statusFilter = document.getElementById('statusFilter');

    if (urlParams.has('filter_type') && filterType) {
        filterType.value = urlParams.get('filter_type');
    }
    if (urlParams.has('status_filter') && statusFilter) {
        statusFilter.value = urlParams.get('status_filter');
    }
});
