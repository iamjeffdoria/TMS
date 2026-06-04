
function formatTriDate(dateStr) {
    if (!dateStr) return '—';
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const parts = dateStr.split('-');
    if (parts.length !== 3) return dateStr;
    const month = months[parseInt(parts[1]) - 1];
    const day = parseInt(parts[2]);
    const year = parts[0];
    return month + '-' + day + '-' + year;
}

 
    
document.addEventListener("DOMContentLoaded", function () {

  // Fix aria-hidden focus warning for ALL modals
$('.modal').on('hide.bs.modal', function () {
    if (document.activeElement) {
        document.activeElement.blur();
    }
});

$('#saveAddPermitBtn').on('click', function () {
    var form = $('#addPermitForm');
    $.ajax({
        url: TRICYCLE_URLS.addTricycle,
        type: "POST",
        data: form.serialize(),
        success: function (data) {
            if (data.success) {
                $('#addPermitModal').modal('hide');
                $('#createReportTable').DataTable().ajax.reload();
                form[0].reset();
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        },
        error: function () {
            alert('An error occurred while saving the tricycle.');
        }
    });
});

// Handle View button click
$(document).on('click', '.btn-view', function() {
    var bodyNumber = $(this).data('body-number');
    var name = $(this).data('name');
    var address = $(this).data('address');
    var makeKind = $(this).data('make-kind');
    var engineMotor = $(this).data('engine-motor');
    var chassis = $(this).data('chassis');
    var plateNo = $(this).data('plate-no');
    var dateRegistered = $(this).data('date-registered');
    var dateExpired = $(this).data('date-expired');
    var status = $(this).data('status');
    var remarks = $(this).data('remarks');
    var toda = $(this).data('toda');

    var statusBadgeStyle = 'background:#e2e8f0;color:#64748b;';
    if (status.toLowerCase() === 'new' || status.toLowerCase().includes('registered') || status.toLowerCase().includes('active')) {
        statusBadgeStyle = 'background:#e1fcef;color:#147d64;';
    } else if (status.toLowerCase().includes('expired')) {
        statusBadgeStyle = 'background:#ffe5e5;color:#c41e3a;';
    } else if (status.toLowerCase().includes('renewed')) {
        statusBadgeStyle = 'background:#e0f2fe;color:#0369a1;';
    } else if (status.toLowerCase().includes('renewal')) {
        statusBadgeStyle = 'background:#fef3c7;color:#d97706;';
    } else if (status.toLowerCase().includes('inactive')) {
        statusBadgeStyle = 'background:#f1f5f9;color:#475569;';
    }

    var remarksText = remarks === 'with_mayors_permit' ? "With Mayor's Permit"
                    : remarks === 'without_mayors_permit' ? "Without Mayor's Permit"
                    : remarks || '—';

    var modalHTML = `
        <div class="px-3 pb-3">
            <div class="row g-2">

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Body Number</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.95rem;">${bodyNumber || '—'}</div>
                    </div>
                </div>

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Plate No</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.95rem;">${plateNo || '—'}</div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Name</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.95rem;">${name || '—'}</div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Address</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.95rem;">${address || '—'}</div>
                    </div>
                </div>

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Make/Kind</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.95rem;">${makeKind || '—'}</div>
                    </div>
                </div>

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Status</div>
                        <div>
                            <span class="badge badge-pill" style="${statusBadgeStyle}font-size:0.8rem;padding:5px 10px;">${status || '—'}</span>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Engine/Motor No</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.95rem;word-break:break-all;">${engineMotor || '—'}</div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Chassis No</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.95rem;word-break:break-all;">${chassis || '—'}</div>
                    </div>
                </div>

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#e1fcef;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Date Registered</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.9rem;">${formatTriDate(dateRegistered)}</div>
                    </div>
                </div>

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#ffe5e5;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Date Expired</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.9rem;">${formatTriDate(dateExpired)}</div>
                    </div>
                </div>

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">Remarks</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.9rem;">${remarksText}</div>
                    </div>
                </div>

                <div class="col-6">
                    <div class="p-2 rounded" style="background:#f8fafc;">
                        <div class="text-muted" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:.5px;">TODA</div>
                        <div class="font-weight-bold text-dark" style="font-size:0.9rem;">${toda || '—'}</div>
                    </div>
                </div>

            </div>
        </div>
    `;

    $('#viewModalContent').html(modalHTML);
    $('#viewPermitModal').modal('show');
});
// Fix aria-hidden focus warning on view modal close
$('#viewPermitModal').on('hide.bs.modal', function () {
    if (document.activeElement) {
        document.activeElement.blur();
    }
});
// Handle Update button click
$(document).on('click', '.btn-update', function() {
    var id = $(this).data('id');
    var bodyNumber = $(this).data('body-number');
    var name = $(this).data('name');
    var address = $(this).data('address');
    var makeKind = $(this).data('make-kind');
    var engineMotor = $(this).data('engine-motor');
    var chassis = $(this).data('chassis');
    var plateNo = $(this).data('plate-no');
    var dateRegistered = $(this).data('date-registered');
    var dateExpired = $(this).data('date-expired');
    var status = $(this).data('status');
    var remarks = $(this).data('remarks');
    
    $('#update_tricycle_id').val(id);
    $('#update_body_number').val(bodyNumber);
    $('#update_name').val(name);
    $('#update_address').val(address);
    $('#update_make_kind').val(makeKind);
    $('#update_engine_motor_no').val(engineMotor);
    $('#update_chassis_no').val(chassis);
    $('#update_plate_no').val(plateNo);
    $('#update_date_registered').val(dateRegistered);
    $('#update_date_expired').val(dateExpired);
    $('#update_status').val(status);
    $('#update_remarks').val(remarks);
    $('#update_toda').val($(this).data('toda') || '');
    var franchiseDate = $(this).data('latest-franchise-date') || '';
    if (franchiseDate) {
        $('#franchiseDateValue').text(franchiseDate);
        $('#franchiseDateHint').removeClass('d-none');
    } else {
        $('#franchiseDateHint').addClass('d-none');
    }
    $('#updatePermitModal').modal('show');
});

// Handle Update Save button click
$('#saveUpdatePermitBtn').on('click', function () {
    var form = $('#updatePermitForm');

    $.ajax({
        url: TRICYCLE_URLS.updateTricycle,
        type: "POST",
        data: form.serialize(),
        success: function (data) {
            if (data.success) {

                $('#updatePermitModal').modal('hide');

                // Reload table (optional if page reloads)
                $('#createReportTable').DataTable().ajax.reload(null, false);

                // Small delay so modal closes smoothly
                setTimeout(function () {
                    location.reload();
                }, 300);

            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        },
        error: function (xhr, status, error) {
            alert('An error occurred while updating the tricycle: ' + error);
        }
    });
});
// Handle Delete button click — open confirmation modal
var deleteTriId = null;
$(document).on('click', '.btn-delete', function () {
    deleteTriId = $(this).data('id');
    var name = $(this).data('name');
    var bodyNumber = $(this).data('body-number');

    $('#deleteTriName').text(name);
    $('#deleteTriBodyNumber').text('Body #: ' + bodyNumber);
    $('#deleteTriModal').modal('show');
});

// Handle confirmed delete
$('#confirmDeleteTriBtn').on('click', function () {
    if (!deleteTriId) return;

    var csrfToken = $('[name=csrfmiddlewaretoken]').first().val();

    $.ajax({
        url: TRICYCLE_URLS.deleteTricycle,
        type: "POST",
        data: {
            tricycle_id: deleteTriId,
            csrfmiddlewaretoken: csrfToken
        },
        success: function (data) {
            if (data.success) {
                $('#deleteTriModal').modal('hide');
                deleteTriId = null;
                // ✅ Store message in sessionStorage before reload
                setTimeout(function () {
                    location.reload();
                }, 300);
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        },
        error: function () {
            alert('An error occurred while deleting the tricycle.');
        }
    });
});
    
    // Initialize DataTable with server-side processing
    var table = $('#createReportTable').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": TRICYCLE_URLS.datatableUrl,
            "type": "GET",
            "data": function(d) {
                // Add date filter parameters to the request
                d.filter_start = $('#filterStart').val();
                d.filter_end = $('#filterEnd').val();
            },
            "dataSrc": function(json) {
                // Update status counts when data is loaded
                if (json.statusCounts) {
                    $('#countRenewed').text(json.statusCounts.renewed);
                    $('#countRegistered').text(json.statusCounts.registered);
                    $('#countExpired').text(json.statusCounts.expired);
                }
                return json.data;
            }
        },
        "pageLength": 10,
        "lengthChange": false,
        "lengthMenu": [5, 10, 25, 50, 100],
        "ordering": false,
        "searching": true,
        "dom": 'frtip',
        "columns": [
            { 
                "data": 0,  // Body Number + Remarks badge
                "render": function(data, type, row) {
                    var remarks = row[10];
                    var remarksBadge = '';
                    if (remarks && remarks !== '-') {
                        var remarksText = remarks === 'with_mayors_permit' ? "W/ Mayor's Permit" : "W/O Mayor's Permit";
                        var remarksColor = remarks === 'with_mayors_permit' ? 'badge-success' : 'badge-danger';
                      remarksBadge = '<br><span class="badge ' + remarksColor + ' badge-sm" style="white-space:normal;word-break:break-word;display:inline-block;max-width:100%;"><i class="fas fa-sticky-note"></i> ' + remarksText + '</span>';
                    }
                    return '<span>' + data + '</span>' + remarksBadge;
                }
            },
            { 
                "data": 1,  // Name + TODA badge
                "render": function(data, type, row) {
                    var toda = row[11];
                    var todaBadge = '';
                    if (toda) {
                       todaBadge = '<br><span class="badge badge-warning badge-sm" style="white-space:normal;word-break:break-word;display:inline-block;max-width:100%;"><i class="fas fa-map-pin"></i> ' + toda + '</span>';
                    }
                    return '<span>' + data + '</span>' + todaBadge;
                }
            },
            { "data": 2 },  // Address
            { 
                "data": 3,  // Make/Kind + Status badge
                "render": function(data, type, row) {
                    var status = row[9];
                    var statusBadge = '';
                    if (status) {
                        var badgeClass = 'badge-secondary';
                        if (status.toLowerCase().includes('active') || status.toLowerCase() === 'new' || status.toLowerCase().includes('registered')) {
                            badgeClass = 'badge-success';
                        } else if (status.toLowerCase().includes('expired')) {
                            badgeClass = 'badge-danger';
                        } else if (status.toLowerCase().includes('renewed')) {
                            badgeClass = 'badge-info';
                        } else if (status.toLowerCase().includes('inactive')) {
                            badgeClass = 'badge-warning';
                        }
                        statusBadge = '<br><span class="badge ' + badgeClass + ' badge-sm">' + status + '</span>';
                    }
                    return '<span>' + data + '</span>' + statusBadge;
                }
            },
            { "data": 4 },  // Engine/Motor No
            { "data": 5 },  // Chassis No
            { 
                "data": 6,  // Plate No + Date badges
                "render": function(data, type, row) {
                    var dateRegistered = row[7];
                    var dateExpired = row[8];
                    var dateBadges = '';
                    if (dateRegistered) {
                        dateBadges += '<br><span class="badge badge-success badge-sm"><i class="fas fa-calendar-plus"></i> ' + dateRegistered + '</span>';
                    }
                    if (dateExpired) {
                        dateBadges += ' <span class="badge badge-danger badge-sm"><i class="fas fa-calendar-times"></i> ' + dateExpired + '</span>';
                    }
                    return '<span>' + data + '</span>' + dateBadges;
                }
            },
            { "data": 7,  "visible": false, "searchable": true },   // Date Registered (hidden)
            { "data": 8,  "visible": false, "searchable": true },   // Date Expired (hidden)
            { "data": 9,  "visible": false, "searchable": true },   // Status (hidden)
            { "data": 10, "visible": false, "searchable": true },   // Remarks (hidden)
            { "data": 11, "visible": false, "searchable": true },   // TODA (hidden, globally searchable)
            { "data": 12, "orderable": false },                     // Action
            { "data": 13, "visible": false, "searchable": false }   // Hidden ID
        ],
        "columnDefs": [
        ]
    });

    // Move DataTable global search into our custom row
// Move DataTable global search into our custom row
$('#globalSearchWrapper').append($('#createReportTable_filter'));
$('#createReportTable_filter').css({
    'margin': '0',
    'float': 'none',
    'display': 'flex',
    'align-items': 'center',
    'gap': '6px'
});
$('#createReportTable_filter label').css({
    'margin': '0',
    'display': 'flex',
    'align-items': 'center',
    'gap': '6px',
    'white-space': 'nowrap'
});
$('#createReportTable_filter input').css({
    'margin': '0',
    'width': '180px'
});

    // Real-time date filtering
    $('#filterStart, #filterEnd').on('change', function() {
        table.ajax.reload();
    });
        // TODA dropdown filter (column 11)
    $('#todaFilter').on('change', function() {
        table.column(11).search($(this).val()).draw();
    });

    $('#createReportTable thead tr').clone(true).appendTo('#createReportTable thead');
    
    $('#createReportTable thead tr:eq(1) th').each(function (i) {
        var column = table.column(i);
        
        if (i === 12) {
            $(this).html('');
            return;
        }

        if (!column.visible()) {
            $(this).html('');
            return;
        }

       $(this).html('<input type="text" class="form-control form-control-sm border-secondary" />');
        
        $('input', this).on('keyup change', function () {
            if (column.search() !== this.value) {
                column.search(this.value).draw();
            }
        });
    });
    
// Handle Print Confirm Button
$('#confirmPrintBtn').on('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Get selected checkboxes
    var selectedValue = $('input[name="reportType"]:checked').val();

    if (!selectedValue) {
        alert('Please select a report to print.');
        return;
    }

    var selectedReports = [selectedValue];
        
    // Close dropdown properly using Bootstrap's method
    $('#printReportBtn').dropdown('toggle');

    // Show the global sidebar loader
    $('#sidebar-loader').addClass('active');
    $('#sidebar-loader .sidebar-loader-text').text('Preparing Report...');
        
    // Small delay to ensure dropdown closes before print dialog
    setTimeout(function() {
        generateAndPrintReports(selectedReports);
    }, 150);
});

});
    function generateAndPrintReports(reportTypes) {
        var currentDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });

        var filterStart = $('#filterStart').val();
        var filterEnd = $('#filterEnd').val();

        // Fetch ALL records (no pagination) from the server
        $.ajax({
            url: TRICYCLE_URLS.datatableUrl,
            type: "GET",
            data: {
            draw: 1,
            start: 0,
            length: 99999,
            filter_start: filterStart,
            filter_end: filterEnd,
            'columns[11][search][value]': $('#todaFilter').val(),  // ✅ pass TODA filter
            },
            success: function(json) {
                var allData = json.data;
                $('#sidebar-loader .sidebar-loader-text').text('Building Report...');
                buildAndPrint(allData, reportTypes, currentDate, filterStart, filterEnd);
            },
            error: function() {
                $('#sidebar-loader').removeClass('active');
                $('#sidebar-loader .sidebar-loader-text').text('Loading...');
                alert('Failed to fetch data for printing.');
            }
        });
    }

function buildAndPrint(allData, reportTypes, currentDate, filterStart, filterEnd) {
    function formatDate(dateString) {
        if (!dateString) return '';
        var date = new Date(dateString);
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    }

    var printContent = '<div style="padding: 20px; font-family: Arial, sans-serif;">';

    reportTypes.forEach(function(type, index) {
        if (index > 0) {
            printContent += '<div style="page-break-before: always;"></div>';
        }

        var reportTitle = '';
        var filteredData = allData.filter(function(row) {
            var status = row[9].toLowerCase();
            if (type === 'renewed') return status.includes('renewed');
            if (type === 'registered') return status.includes('new') || status.includes('registered');
            if (type === 'expired') return status.includes('expired');
            return false;
        });

        if (type === 'renewed') reportTitle = 'Renewed Franchise Report';
        else if (type === 'registered') reportTitle = 'Registered Tricycle Report';
        else if (type === 'expired') reportTitle = 'Expired Franchise Report';
        var todaFilterVal = $('#todaFilter').val();
        var todaText = todaFilterVal ? `<p style="margin: 5px 0; color: #666;">TODA: ${todaFilterVal}</p>` : '';
        var dateRangeText = '';
        if (filterStart && filterEnd) {
            dateRangeText = `<p style="margin: 5px 0; color: #666;">Date Range: ${formatDate(filterStart)} to ${formatDate(filterEnd)}</p>`;
        } else if (filterStart) {
            dateRangeText = `<p style="margin: 5px 0; color: #666;">From: ${formatDate(filterStart)}</p>`;
        } else if (filterEnd) {
            dateRangeText = `<p style="margin: 5px 0; color: #666;">Until: ${formatDate(filterEnd)}</p>`;
        }

        printContent += `
            <div style="position: relative; margin-bottom: 30px;">
                <img src="${logoUrl}" alt="Logo"
                     style="position: absolute; top: 0; left: 0; width: 80px; height: 80px; object-fit: contain;">
                <div style="text-align: center; padding-top: 10px;">
                    <h1 style="margin: 0; color: #333;">${reportTitle}</h1>
                    <p style="margin: 5px 0; color: #666;">Generated on ${currentDate}</p>
                    ${dateRangeText}
                    ${todaText}
                    <p style="margin: 5px 0; color: #666;">Total Records: ${filteredData.length}</p>
                </div>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                <thead>
                    <tr style="background-color: #4e73df; color: white;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Body Number</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Name</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Address</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Make/Kind</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Plate No</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Date Registered</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Date Expired</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Status</th>
                    </tr>
                </thead>
                <tbody>`;

        filteredData.forEach(function(row, idx) {
            var rowColor = idx % 2 === 0 ? '#f8f9fc' : 'white';
            printContent += `
                <tr style="background-color: ${rowColor};">
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[0]}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[1]}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[2]}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[3]}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[6]}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[7]}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[8]}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">${row[9]}</td>
                </tr>`;
        });

        printContent += `</tbody></table>`;
    });

    printContent += '</div>';

    var iframe = document.createElement('iframe');
    iframe.style.position = 'absolute';
    iframe.style.width = '0';
    iframe.style.height = '0';
    iframe.style.border = '0';
    document.body.appendChild(iframe);

    iframe.contentDocument.open();
    iframe.contentDocument.write('<html><head><title>Tricycle Report</title></head><body>');
    iframe.contentDocument.write(printContent);
    iframe.contentDocument.write('</body></html>');
    iframe.contentDocument.close();

    var images = iframe.contentDocument.images;
    var totalImages = images.length;
    var loadedImages = 0;

    function triggerPrint() {
        // Hide loader just before the print dialog appears
        $('#sidebar-loader').removeClass('active');
        $('#sidebar-loader .sidebar-loader-text').text('Loading...');
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
    }

    if (totalImages === 0) {
        triggerPrint();
    } else {
        for (var i = 0; i < totalImages; i++) {
            images[i].onload = function() {
                loadedImages++;
                if (loadedImages === totalImages) {
                    triggerPrint();
                }
            };
        }
    }

    setTimeout(function() {
        document.body.removeChild(iframe);
    }, 2000);
}