function togglePasswordVisibility(inputId, iconElement) {
    var passwordInput = document.getElementById(inputId);
    var icon = iconElement.querySelector('i');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

document.addEventListener("DOMContentLoaded", function () {

    // ── Initialize DataTable (server-side) ────────────────────────────
    var table = $('#dataTable').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: ADMIN_URLS.datatableUrl,
            type: "GET"
        },
        pageLength: 10,
        lengthChange: false,
        ordering: false,
        searching: true,
        columns: [
            {
                // Username + Status badge
                data: 0,
                render: function(data, type, row) {
                    var statusHtml = (row[5] || '').includes('Active')
                        ? '<br><span class="badge badge-success badge-sm"><i class="fas fa-circle"></i> Active</span>'
                        : '<br><span class="badge badge-danger badge-sm"><i class="fas fa-circle"></i> Inactive</span>';
                    return '<span>' + data + '</span>' + statusHtml;
                }
            },
            {
                // Full Name + Email badge
                data: 1,
                render: function(data, type, row) {
                    var email = row[2];
                    var emailBadge = email
                        ? '<br><span class="badge badge-secondary badge-sm"><i class="fas fa-envelope"></i> ' + email + '</span>'
                        : '';
                    return '<span>' + data + '</span>' + emailBadge;
                }
            },
            { data: 2, visible: false, searchable: true },   // Email (hidden, still searchable)
            {
                // Created By + Date badge
                data: 3,
                render: function(data, type, row) {
                    var createdAt = row[8];
                    var dateBadge = createdAt
                        ? '<br><span class="badge badge-info badge-sm"><i class="fas fa-calendar-alt"></i> ' + createdAt + '</span>'
                        : '';
                    return '<span>' + (data || '—') + '</span>' + dateBadge;
                }
            },
            {
                // Permissions + Status badge (status hidden separately)
                data: 4,
                render: function(data, type, row) {
                    return '<span>' + (data || '—') + '</span>';
                }
            },
            { data: 5, visible: false, searchable: false },  // Status (hidden, shown in col 0)
            { data: 6, orderable: false, searchable: false }, // Action
            { data: 7, visible: false, searchable: false },   // Hidden ID
            { data: 8, visible: false, searchable: false },   // Hidden created_at
        ]
    });

    // ── Column search ─────────────────────────────────────────────────
    table.columns().every(function(index) {
        var that = this;
        if ([5, 6, 7, 8].includes(index)) return;
        $('input', this.header()).on('keyup change clear', function() {
            if (that.search() !== this.value) {
                that.search(this.value).draw();
            }
        });
    });

    // ── VIEW ──────────────────────────────────────────────────────────
    $('#dataTable tbody').on('click', '.btn-admin-view', function () {
        var row = table.row($(this).closest('tr'));
        var data = row.data();
        var usernameText = data[0] || '';
        var fullNameText = data[1] || usernameText;
        var emailText    = data[2] || '—';
        var createdByText = data[3] || '—';
        var statusActive = (data[5] || '').includes('Active');

        document.getElementById('view-admin-username').innerText  = usernameText ? '@' + usernameText : '';
        document.getElementById('view-admin-full-name').innerText = fullNameText;
        document.getElementById('view-admin-email').innerText     = emailText;
        document.getElementById('view-admin-created-by').innerText = createdByText;
        document.getElementById('view-admin-created-at').innerText = data[8] || '—';

        document.getElementById('view-admin-status').innerHTML = statusActive
            ? '<span class="badge badge-success">Active</span>'
            : '<span class="badge badge-danger">Inactive</span>';

        var initials = (fullNameText.split(/\s+/).map(n => n ? n[0] : '').join('').slice(0, 2) || usernameText.slice(0, 2)).toUpperCase();
        var avatarEl = document.getElementById('admin-avatar');
        if (avatarEl) avatarEl.innerText = initials;

        var permPotpot = this.dataset.permPotpot;
        var permMoto   = this.dataset.permMoto;

        function permBadge(val, label) {
            var granted = (val === '1');
            var bg    = granted ? '#f0fdf4' : '#f9fafb';
            var color = granted ? '#15803d' : '#6b7280';
            var dot   = granted ? '●' : '○';
            return '<span style="font-size:12px;padding:4px 10px;border-radius:20px;background:' + bg + ';color:' + color + ';">' + dot + ' ' + label + '</span>';
        }
        document.getElementById('view-admin-perm-potpot').innerHTML = permBadge(permPotpot, 'Potpot');
        document.getElementById('view-admin-perm-moto').innerHTML   = permBadge(permMoto, 'Motorcycle');

        $('#viewAdminModal').modal('show');
    });

    // ── EDIT ──────────────────────────────────────────────────────────
    $('#dataTable tbody').on('click', '.btn-admin-edit', function (e) {
        e.preventDefault();
        var modal = document.getElementById('editAdminModal');

        modal.querySelector('input[name="admin_id"]').value          = this.dataset.adminId || '';
        modal.querySelector('input[name="username"]').value          = this.dataset.username || '';
        modal.querySelector('input[name="username_original"]').value = this.dataset.username || '';
        modal.querySelector('input[name="full_name"]').value         = this.dataset.fullName || '';
        modal.querySelector('input[name="email"]').value             = this.dataset.email || '';
        modal.querySelector('#edit-admin-created-by').innerText      = this.dataset.createdBy || '—';
        modal.querySelector('#edit-admin-created-at').innerText      = this.dataset.createdAt || '—';
        modal.querySelector('select[name="role"]').value = this.dataset.role || 'potpot_admin';
        modal.querySelector('select[name="status"]').value           = this.dataset.status === '1' ? '1' : '0';

        $('#editAdminModal').modal('show');
    });

    // ── DELETE ────────────────────────────────────────────────────────
$('#dataTable tbody').on('click', '.btn-admin-delete', function (e) {
    e.preventDefault();
    var adminId = this.dataset.adminId;
    if (!confirm('Are you sure you want to delete this admin?')) return;

    $.ajax({
        url: '/delete-admin/',
        type: 'POST',
        data: {
            admin_id: adminId,
            csrfmiddlewaretoken: ADMIN_URLS.csrfToken
        },
        success: function(response) {
            if (response.success) {
                $('#dataTable').DataTable().ajax.reload();
            } else {
                alert('Error: ' + (response.error || 'Could not delete admin.'));
            }
        },
        error: function() {
            alert('Server error. Please try again.');
        }
    });
});

});

document.addEventListener("DOMContentLoaded", function () {
    var fileInput = document.getElementById('adminFileInput');
    var importBtn = document.getElementById('importAdminBtn');

    fileInput.addEventListener('change', function () {
        importBtn.disabled = !fileInput.files || fileInput.files.length === 0;
    });
});