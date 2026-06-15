function formatMtopDate(dateStr) {
    if (!dateStr) return '';
    return dateStr;
}

document.addEventListener("DOMContentLoaded", function () {

    var table = $('#dataTable').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": MTOP_CONFIG.datatableUrl,
            "type": "GET"
        },
        "pageLength": 10,
        "lengthMenu": [5, 10, 25, 50, 100],
        "lengthChange": false,
        "ordering": false,
        "searching": true,
        "dom": 'frtip',
        "columns": [
            {
                "data": 0,  // Name + Date badge
                "render": function (data, type, row) {
                    var date = row[9];
                    var dateBadge = '';
                    if (date) {
                        dateBadge = '<br><span class="badge badge-info badge-sm"><i class="fas fa-calendar"></i> ' + date + '</span>';
                    }
                    return '<span>' + data + '</span>' + dateBadge;
                }
            },
            {
                "data": 1,  // Case No + Mayor badge
                "render": function (data, type, row) {
                    var mayor = row[12];
                    var mayorBadge = '';
                    if (mayor) {
                        mayorBadge = '<br><span class="badge badge-dark badge-sm"><i class="fas fa-landmark"></i> ' + mayor + '</span>';
                    }
                    return '<span>' + data + '</span>' + mayorBadge;
                }
            },
            {
                "data": 2,  // Address + Municipal Treasurer badge
                "render": function (data, type, row) {
                    var treasurer = row[10];
                    var treasurerBadge = '';
                    if (treasurer) {
                        treasurerBadge = '<br><span class="badge badge-warning badge-sm"><i class="fas fa-user-tie"></i> ' + treasurer + '</span>';
                    }
                    return '<span>' + data + '</span>' + treasurerBadge;
                }
            },
            { "data": 3 },  // No. of Units
            {
                "data": 4,  // Route Operation + Officer in Charge badge
                "render": function (data, type, row) {
                    var officer = row[11];
                    var officerBadge = '';
                    if (officer) {
                        officerBadge = '<br><span class="badge badge-secondary badge-sm"><i class="fas fa-user-shield"></i> ' + officer + '</span>';
                    }
                    return '<span>' + data + '</span>' + officerBadge;
                }
            },
            {
                "data": 5,  // Make + Motor No + Chassis No + Plate No badges
                "render": function (data, type, row) {
                    var motorNo = row[6];
                    var chassisNo = row[7];
                    var plateNo = row[8];
                    var badges = '';
                    if (motorNo) {
                        badges += '<br><span class="badge badge-info badge-sm"><i class="fas fa-cog"></i> ' + motorNo + '</span>';
                    }
                    if (chassisNo) {
                        badges += ' <span class="badge badge-success badge-sm"><i class="fas fa-car"></i> ' + chassisNo + '</span>';
                    }
                    if (plateNo) {
                        badges += ' <span class="badge badge-dark badge-sm"><i class="fas fa-id-card"></i> ' + plateNo + '</span>';
                    }
                    return '<span>' + data + '</span>' + badges;
                }
            },
            { "data": 6, "visible": false, "searchable": true },   // Motor No (hidden)
            { "data": 7, "visible": false, "searchable": true },   // Chassis No (hidden)
            { "data": 8, "visible": false, "searchable": true },   // Plate No (hidden)
            { "data": 9, "visible": false, "searchable": true },   // Date (hidden)
            { "data": 10, "visible": false, "searchable": true },  // Municipal Treasurer (hidden)
            { "data": 11, "visible": false, "searchable": true },  // Officer in Charge (hidden)
            { "data": 12, "visible": false, "searchable": true },  // Mayor (hidden)
            { "data": 13, "orderable": false }                     // Action
        ],
        "columnDefs": []
    });

    /* ── Column search row ─────────────────────────────────── */
    $('#dataTable thead tr').clone(true).appendTo('#dataTable thead');

    $('#dataTable thead tr:eq(1) th').each(function (i) {
        var column = table.column(i);

        if (i === 13 || !column.visible()) {
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

/* ── SAVE NEW RECORD ────────────────────────────────────── */
    document.getElementById("saveRecordBtn").addEventListener("click", function () {
        let form = document.getElementById("addRecordForm");
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        let btn = this;
        let originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm mr-1" role="status" aria-hidden="true"></span> Saving...';
        document.getElementById('sidebar-loader').classList.add('active');

        let formData = new FormData(form);

        fetch(MTOP_CONFIG.addUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": MTOP_CONFIG.csrfToken
            }
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    $("#addRecordModal").modal("hide");
                    setTimeout(function () {
                        location.reload();
                    }, 300);
                } else {
                    document.getElementById('sidebar-loader').classList.remove('active');
                    btn.disabled = false;
                    btn.innerHTML = originalHtml;
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                document.getElementById('sidebar-loader').classList.remove('active');
                btn.disabled = false;
                btn.innerHTML = originalHtml;
                console.error('Error:', error);
                alert('An error occurred while saving the record.');
            });
    });

    /* ── EDIT BUTTON CLICK ──────────────────────────────────── */
   $(document).on("click", ".edit-btn", function () {
        const id = $(this).data("id");

        $.ajax({
            url: MTOP_CONFIG.getUrlBase + id + '/',
            type: "GET",
            success: function (data) {
                $("#edit_id").val(data.id);
                $("#edit_name").val(data.name);
                $("#edit_case_no").val(data.case_no);
                $("#edit_address").val(data.address);
                $("#edit_no_of_units").val(data.no_of_units);
                $("#edit_route_operation").val(data.route_operation);
                $("#edit_make").val(data.make);
                $("#edit_motor_no").val(data.motor_no);
                $("#edit_chasses_no").val(data.chasses_no);
                $("#edit_plate_no").val(data.plate_no);
                $("#edit_date").val(data.date);
                $("#edit_municipal_treasurer").val(data.municipal_treasurer);
                $("#edit_officer_in_charge").val(data.officer_in_charge);
                $("#edit_mayor").val(data.mayor);
            },
            error: function (xhr, status, error) {
                console.error("Error fetching MTOP data:", error);
                alert("Failed to load record data. Please try again.");
            }
        });
    });

/* ── UPDATE BUTTON CLICK ────────────────────────────────── */
    $("#updateRecordBtn").click(function () {
        let btn = this;
        let originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm mr-1" role="status" aria-hidden="true"></span> Updating...';
        document.getElementById('sidebar-loader').classList.add('active');

        $.ajax({
            url: MTOP_CONFIG.updateUrl,
            type: "POST",
            data: $("#editRecordForm").serialize(),
            success: function (res) {
                if (res.success) {
                    $("#editRecordModal").modal("hide");
                    setTimeout(function () {
                        location.reload();
                    }, 300);
                } else {
                    document.getElementById('sidebar-loader').classList.remove('active');
                    btn.disabled = false;
                    btn.innerHTML = originalHtml;
                    alert('Error: ' + (res.error || 'Unknown error'));
                }
            },
            error: function (xhr, status, error) {
                document.getElementById('sidebar-loader').classList.remove('active');
                btn.disabled = false;
                btn.innerHTML = originalHtml;
                console.error("Error updating MTOP:", error);
                alert("Failed to update record. Please try again.");
            }
        });
    });

    /* ── DELETE ─────────────────────────────────────────────── */
    var deleteMtopId = null;

    $(document).on('click', '.btn-delete-mtop', function () {
        deleteMtopId = $(this).data('id');
        var name = $(this).data('name');
        var caseNo = $(this).data('case-no');

        $('#deleteMtopName').text(name);
        $('#deleteMtopCaseNo').text('Case No: ' + caseNo);
        $('#deleteMtopModal').modal('show');
    });

    $('#confirmDeleteMtopBtn').on('click', function () {
        if (!deleteMtopId) return;

        $.ajax({
            url: MTOP_CONFIG.deleteUrl,
            type: "POST",
            data: {
                mtop_id: deleteMtopId,
                csrfmiddlewaretoken: MTOP_CONFIG.csrfToken
            },
            success: function (data) {
                if (data.success) {
                    $('#deleteMtopModal').modal('hide');
                    deleteMtopId = null;
                    setTimeout(function () {
                        location.reload();
                    }, 300);
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            },
            error: function () {
                alert('An error occurred while deleting the MTOP record.');
            }
        });
    });

});