 document.addEventListener("DOMContentLoaded", function () {

    
      document.querySelectorAll(".btn-view").forEach(button => {
      button.addEventListener("click", function () {

          let $tr = $(this).closest("tr");
          let row = table.row($tr);   // DataTables row
          let data = row.data();                        // get ALL columns including hidden

          let fields = [
              "Control No", "Status", "Name", "Address", "Business Name",
              "Motorized Operation", "OR No", "Amount Paid", "Issue Date",
              "Expiry Date", "Issued At", "Mayor", "Quarter"
          ];

          let html = "";

          for (let i = 0; i < fields.length; i++) {
              let value;

              // Status: prefer data-search or cell text, show capitalized
          if (i === 1) {
              let rawStatus = $tr.find("td:eq(1)").data("search");

                  let badgeClass = "badge-secondary";
                  if (rawStatus === "active") badgeClass = "badge-success";
                  else if (rawStatus === "inactive") badgeClass = "badge-warning";
                  else if (rawStatus === "expired") badgeClass = "badge-danger";

                  value = `<span class="badge ${badgeClass}">${rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1)}</span>`;
              }
          else {
                  value = (data[i] === undefined || data[i] === null) ? '' : data[i];
                  if (typeof value === 'object') {
                      value = $tr.find(`td:eq(${i})`).text().trim();
                  }
              }

              if (!value) value = '&mdash;';

              html += `
                <div class="col-md-4 col-sm-6 mb-4">
                  <div class="small text-muted">${fields[i]}</div>
                  <div class="font-weight-bold">${value}</div>
                </div>
              `;
          }

          document.getElementById("modalContent").innerHTML = html;
          $("#viewModal").modal("show");
      });
  });

        function toInputDate(dateStr) {
            if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
            // Handles "Mar-1-2026" format — replace dashes with spaces for reliable parsing
            const parsed = new Date(dateStr.replace(/-/g, ' '));
            if (!isNaN(parsed.getTime())) {
                return `${parsed.getFullYear()}-${String(parsed.getMonth()+1).padStart(2,'0')}-${String(parsed.getDate()).padStart(2,'0')}`;
            }
            return '';
        }

  document.querySelectorAll(".btn-update").forEach(button => {
    button.addEventListener("click", function () {

        let $tr = $(this).closest("tr");  // the table row
        let row = table.row($tr);
        let data = row.data();   // array including hidden columns

        document.getElementById("u_id").value = this.dataset.id;

        document.getElementById("u_control_no").value = data[0];

        // ✅ Use data-search instead of data[1]
        let status = $tr.find("td:eq(1)").data("search"); 
        document.getElementById("u_status").value = status;

        document.getElementById("u_name").value = data[2];
        document.getElementById("u_address").value = data[3];
        document.getElementById("u_business_name").value = data[4];
        document.getElementById("u_motorized").value = data[5];
        document.getElementById("u_or_no").value = data[6];
        document.getElementById("u_amount_paid").value = data[7];
        document.getElementById("u_issue_date").value = toInputDate(data[8]);
        document.getElementById("u_expiry_date").value = toInputDate(data[9]);
        document.getElementById("u_issued_at").value = data[10];
        document.getElementById("u_mayor").value = data[11];
        document.getElementById("u_quarter").value = data[12].trim();

        $("#updateModal").modal("show");
    });
});

  var table = $('#dataTable').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": window.PERMIT_CONFIG.datatableUrl,  // ✅
            "type": "GET"
        },
        "pageLength": 10,
        "lengthChange": false,
        "ordering": false,
        "searching": true,
        "dom": 'frtip',
  "columns": [
    { 
        "data": 0,  // Control No + Issued At badge
        "render": function(data, type, row) {
            var issuedAt = row[10];
            var issuedBadge = '';
            if (issuedAt) {
                issuedBadge = '<br><span class="badge badge-info badge-sm"><i class="fas fa-map-pin"></i> ' + issuedAt + '</span>';
            }
            return '<span>' + data + '</span>' + issuedBadge;
        }
    },
    { "data": 1, "visible": false, "searchable": true },  // Status (hidden)
    { 
        "data": 2,  // Name + Mayor badge
        "render": function(data, type, row) {
            var mayor = row[11];
            var mayorBadge = '';
            if (mayor) {
                mayorBadge = '<br><span class="badge badge-dark badge-sm"><i class="fas fa-user-tie"></i> ' + mayor + '</span>';
            }
            return '<span>' + data + '</span>' + mayorBadge;
        }
    },
    { 
        "data": 3,  // Address + Quarter badge
        "render": function(data, type, row) {
            var quarter = row[12];
            var quarterBadge = '';
            if (quarter) {
                quarterBadge = '<br><span class="badge badge-secondary badge-sm"><i class="fas fa-chart-line"></i> ' + quarter + '</span>';
            }
            return '<span>' + data + '</span>' + quarterBadge;
        }
    },
    { 
        "data": 4,  // Business Name + Issue Date + Expiry Date badges
        "render": function(data, type, row) {
            var issueDate = row[8];
            var expiryDate = row[9];
            var dateBadges = '';
            if (issueDate) {
                dateBadges += '<br><span class="badge badge-success badge-sm"><i class="fas fa-calendar-plus"></i> ' + issueDate + '</span>';
            }
            if (expiryDate) {
                dateBadges += ' <span class="badge badge-danger badge-sm"><i class="fas fa-calendar-times"></i> ' + expiryDate + '</span>';
            }
            return '<span>' + data + '</span>' + dateBadges;
        }
    },
    { 
        "data": 5,  // Motorized Operation + Status badge
        "render": function(data, type, row) {
            var status = row[1];
            var statusBadge = '';
            if (status) {
                var badgeClass = '';
                var statusText = status.charAt(0).toUpperCase() + status.slice(1);
                if (status.toLowerCase() === 'active') badgeClass = 'badge-success';
                else if (status.toLowerCase() === 'inactive') badgeClass = 'badge-warning';
                else if (status.toLowerCase() === 'expired') badgeClass = 'badge-danger';
                else badgeClass = 'badge-secondary';
                statusBadge = '<br><span class="badge ' + badgeClass + ' badge-sm">' + statusText + '</span>';
            }
            return '<span>' + data + '</span>' + statusBadge;
        }
    },
    { 
        "data": 6,  // OR No + Amount Paid badge
        "render": function(data, type, row) {
            var amountPaid = row[7];
            var amountBadge = '';
            if (amountPaid) {
                amountBadge = '<br><span class="badge badge-warning badge-sm">₱ ' + amountPaid + '</span>';
            }
            return '<span>' + data + '</span>' + amountBadge;
        }
    },
    { "data": 7 },   // Amount Paid (hidden)
    { "data": 8 },   // Issue Date (hidden)
    { "data": 9 },   // Expiry Date (hidden)
    { "data": 10 },  // Issued At (hidden)
    { "data": 11 },  // Mayor (hidden)
    { "data": 12 },  // Quarter (hidden)
    { "data": 13, "orderable": false },  // Action
    { "data": 14 },  // Hidden ID
    { "data": 15 }   // Hidden raw status
],
"columnDefs": [
    {
        "targets": [7, 8, 9, 10, 11, 12],  // All hidden data columns
        "visible": false,
        "searchable": true
    },
    {
        "targets": 14,
        "visible": false,
        "searchable": false
    },
    {
        "targets": 15,
        "visible": false,
        "searchable": false
    }
]
    });

    // Column search for text inputs
    table.columns().every(function(index) {
        var that = this;
        
        if (index === 1 || index === 13 || index === 14 || index === 15) {
            return;
        }
        
        $('input', this.header()).on('keyup change clear', function() {
            if (that.search() !== this.value) {
                that.search(this.value).draw();
            }
        });
    });

    // Status dropdown filter
    // $('#statusFilter').on('change', function() {
    //     var searchValue = this.value;
    //     table.column(1).search(searchValue).draw();
    // });

    // View button - use event delegation
    $('#dataTable tbody').on('click', '.btn-view', function(e) {
        e.preventDefault();
        
        let row = table.row($(this).closest('tr'));
        let data = row.data();
        
        let fields = [
            "Control No", "Status", "Name", "Address", "Business Name",
            "Motorized Operation", "OR No", "Amount Paid", "Issue Date",
            "Expiry Date", "Issued At", "Mayor", "Quarter"
        ];

        let html = "";
        for (let i = 0; i < fields.length; i++) {
            let value = data[i] || '&mdash;';
            html += `
                <div class="col-md-4 col-sm-6 mb-4">
                    <div class="small text-muted">${fields[i]}</div>
                    <div class="font-weight-bold">${value}</div>
                </div>
            `;
        }

        document.getElementById("modalContent").innerHTML = html;
        $("#viewModal").modal("show");
    });

    function toInputDate(dateStr) {
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
        let d = new Date(dateStr);
        if (isNaN(d.getTime())) return "";
        let m = ("0" + (d.getMonth() + 1)).slice(-2);
        let day = ("0" + d.getDate()).slice(-2);
        return `${d.getFullYear()}-${m}-${day}`;
    }

    // Update button - use event delegation
    $('#dataTable tbody').on('click', '.btn-update', function(e) {
        e.preventDefault();
        
        let row = table.row($(this).closest('tr'));
        let data = row.data();

        document.getElementById("u_id").value = data[14];  // ID from hidden column
        document.getElementById("u_control_no").value = data[0];
        document.getElementById("u_status").value = data[15];  // Raw status from hidden column
        document.getElementById("u_name").value = data[2];
        document.getElementById("u_address").value = data[3];
        document.getElementById("u_business_name").value = data[4];
        document.getElementById("u_motorized").value = data[5];
        document.getElementById("u_or_no").value = data[6];
        document.getElementById("u_amount_paid").value = data[7];
        document.getElementById("u_issue_date").value = toInputDate(data[8]);
        document.getElementById("u_expiry_date").value = toInputDate(data[9]);
        document.getElementById("u_issued_at").value = data[10];
        document.getElementById("u_mayor").value = data[11];
        document.getElementById("u_quarter").value = data[12].trim();

        $("#updateModal").modal("show");
    });
// Save Update
document.getElementById("saveUpdateBtn").addEventListener("click", function () {
    const btn = this;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm mr-1" role="status" aria-hidden="true"></span> Saving...';
    document.getElementById('sidebar-loader').classList.add('active');

    let id = document.getElementById("u_id").value;
    let csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let formData = new FormData();
    formData.append("control_no", document.getElementById("u_control_no").value);
    formData.append("status", document.getElementById("u_status").value);
    formData.append("name", document.getElementById("u_name").value);
    formData.append("address", document.getElementById("u_address").value);
    formData.append("business_name", document.getElementById("u_business_name").value);
    formData.append("motorized_operation", document.getElementById("u_motorized").value);
    formData.append("or_no", document.getElementById("u_or_no").value);
    formData.append("amount_paid", document.getElementById("u_amount_paid").value);
    formData.append("issue_date", document.getElementById("u_issue_date").value);
    formData.append("expiry_date", document.getElementById("u_expiry_date").value);
    formData.append("issued_at", document.getElementById("u_issued_at").value);
    formData.append("mayor", document.getElementById("u_mayor").value);
    formData.append("quarter", document.getElementById("u_quarter").value);

    fetch(`/mayors-permit/update/${id}/`, {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": csrftoken },
    })
    .then(res => {
        if (!res.ok) {
            return res.text().then(text => {
                throw new Error('Server error ' + res.status + ': ' + text.substring(0, 300));
            });
        }
        return res.json();
    })
    .then(data => {
        if (data.success) {
            $("#updateModal").modal("hide");

            let alertBox = document.createElement("div");
            alertBox.className = "alert alert-success mt-3";
            alertBox.innerText = data.message;
            document.querySelector(".card-body").prepend(alertBox);

            setTimeout(() => alertBox.remove(), 3000);
            location.reload(); // loader stays until page reloads
        } else {
            document.getElementById('sidebar-loader').classList.remove('active');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check"></i> Save Changes';
            alert(data.error || 'Failed to update permit.');
        }
    })
    .catch(err => {
        document.getElementById('sidebar-loader').classList.remove('active');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-check"></i> Save Changes';
        console.error('Update error:', err.message);
        alert('Error: ' + err.message);
    });
});

// Add Permit
document.getElementById("saveAddPermitBtn").addEventListener("click", function() {
    const btn = this;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm mr-1" role="status" aria-hidden="true"></span> Saving...';
    document.getElementById('sidebar-loader').classList.add('active');

    let form = document.getElementById("addPermitForm");
    let formData = new FormData(form);
    let csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    fetch(window.PERMIT_CONFIG.addUrl, {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": csrftoken },
    })
    .then(res => {
        if (!res.ok) {
            return res.text().then(text => {
                throw new Error('Server error ' + res.status + ': ' + text.substring(0, 300));
            });
        }
        return res.json();
    })
    .then(data => {
        if (data.success) {
            $("#addPermitModal").modal("hide");

            let alertBox = document.createElement("div");
            alertBox.className = "alert alert-success mt-3";
            alertBox.innerText = data.message;
            document.querySelector(".card-body").prepend(alertBox);

            setTimeout(() => alertBox.remove(), 3000);
            location.reload(); // loader stays until page reloads
        } else {
            document.getElementById('sidebar-loader').classList.remove('active');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check"></i> Save Permit';
            alert(data.error || "Failed to add permit.");
        }
    })
    .catch(err => {
        document.getElementById('sidebar-loader').classList.remove('active');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-check"></i> Save Permit';
        console.error(err);
        alert('Error: ' + err.message);
    });
});

     // ── DELETE ────────────────────────────────────────────────────────
    let pendingDeletePermitId = null;

    $('#dataTable tbody').on('click', '.btn-delete-permit', function(e) {
        e.preventDefault();
        pendingDeletePermitId = $(this).data('id');
        const name = $(this).data('name') || 'this record';
        document.getElementById('delete-permit-name').textContent = name;
        $('#deletePermitModal').modal('show');
    });

    document.getElementById('confirmDeletePermitBtn').addEventListener('click', function () {
        if (!pendingDeletePermitId) return;
        fetch(`/mayors-permit/delete/${pendingDeletePermitId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                $('#deletePermitModal').modal('hide');
                pendingDeletePermitId = null;
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(err => console.error(err));
    });


    // History button - use event delegation
$('#dataTable tbody').on('click', '.btn-history', function(e) {
    e.preventDefault();
    
    let permitId = $(this).data('id');
    
    // Show modal
    $("#historyModal").modal("show");
    
    // Fetch history data
    fetch(`/mayors-permit/history-data/${permitId}/`)
        .then(res => res.json())
        .then(response => {
            if (response.success) {
                let data = response.data;
                
                // Populate permit info
                document.getElementById('history-control-no').textContent = data.permit_info.control_no;
                document.getElementById('history-name').textContent = data.permit_info.name;
                
                // Format current status with badge
                let statusBadge = '';
                if (data.permit_info.current_status === 'active') {
                    statusBadge = '<span class="badge badge-success">Active</span>';
                } else if (data.permit_info.current_status === 'inactive') {
                    statusBadge = '<span class="badge badge-warning">Inactive</span>';
                } else if (data.permit_info.current_status === 'expired') {
                    statusBadge = '<span class="badge badge-danger">Expired</span>';
                }
                document.getElementById('history-current-status').innerHTML = statusBadge;
                
                // Populate history timeline
                let timelineHtml = '';
                if (data.history && data.history.length > 0) {
                    data.history.forEach(record => {
                        timelineHtml += `
                            <div class="card mb-2">
                                <div class="card-body py-2">
                                    <div class="row align-items-center">
                                        <div class="col-md-3">
                                            <small class="text-muted"><i class="fas fa-calendar"></i> ${record.date}</small>
                                        </div>
                                        <div class="col-md-6">
                                            <span class="badge badge-secondary">${record.old_status}</span>
                                            <i class="fas fa-arrow-right mx-2"></i>
                                            <span class="badge badge-primary">${record.new_status}</span>
                                        </div>
                                        <div class="col-md-3 text-right">
                                            <small class="text-muted">${record.changed_by}</small>
                                        </div>
                                    </div>
                                    ${record.reason ? `<div class="row mt-2"><div class="col-12"><small><strong>Reason:</strong> ${record.reason}</small></div></div>` : ''}
                                </div>
                            </div>
                        `;
                    });
                } else {
                    timelineHtml = `
                        <div class="alert alert-info text-center">
                            <i class="fas fa-info-circle"></i> No status change history available
                        </div>
                    `;
                }
                
                document.getElementById('historyTimeline').innerHTML = timelineHtml;
            } else {
                document.getElementById('historyTimeline').innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i> ${response.error || 'Failed to load history'}
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error fetching history:', err);
            document.getElementById('historyTimeline').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> Error loading history data
                </div>
            `;
        });
});
});