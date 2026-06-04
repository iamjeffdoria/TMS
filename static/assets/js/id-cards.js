/**
 * idcards.js
 * All JS logic for the ID Cards page.
 * Django template values are injected via window.IDCARD_CONFIG (defined inline in the template).
 */

/* ── Helpers ──────────────────────────────────────────────────────── */

function showImagePreview(imageUrl) {
    document.getElementById('preview-image').src = imageUrl;
    $('#imagePreviewModal').modal('show');
}

function formatDateForInput(dateStr) {
    if (!dateStr || dateStr === 'None' || dateStr === 'null') return '';
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
    const parsed = new Date(dateStr.replace(/-/g, ' '));
    if (!isNaN(parsed.getTime())) {
        return `${parsed.getFullYear()}-${String(parsed.getMonth() + 1).padStart(2, '0')}-${String(parsed.getDate()).padStart(2, '0')}`;
    }
    return '';
}

function applyPreviewStyle(id, styles) {
    const el = document.getElementById(id);
    el.style.display = '';
    Object.assign(el.style, styles);
}

/* ── Print state ─────────────────────────────────────────────────── */

let pendingPrintData = null;
let currentPrintType = 1;

function preparePrint(photoUrl, fullName, idNum, address, dob, gender, orNumber, height, weight, dateIssued, expiryDate, dmOnate) {
    pendingPrintData = { photoUrl, fullName, idNum, address, dob, gender, orNumber, height, weight, dateIssued, expiryDate, dmOnate };
    $('#printConfirmModal').modal('show');
}

function executePrint(idType) {
    if (!pendingPrintData) return;
    currentPrintType = idType;
    const data = pendingPrintData;
    const cfg  = window.IDCARD_CONFIG;

    const previewIds = [
        'preview-dyn-photo', 'preview-dyn-name', 'preview-dyn-id', 'preview-dyn-addr',
        'preview-dyn-dob', 'preview-dyn-gender', 'preview-dyn-or', 'preview-dyn-height',
        'preview-dyn-weight', 'preview-dyn-issued', 'preview-dyn-expiry', 'preview-dyn-mayor'
    ];

    previewIds.forEach(id => {
        const el = document.getElementById(id);
        el.style.cssText = '';
        el.style.position = 'absolute';
    });

    $('#printConfirmModal').modal('hide');

    if (idType === 1) {
        document.getElementById('preview-template-bg').src = cfg.template1Img;

        applyPreviewStyle('preview-dyn-photo', {
            top: '19.2%', left: '50.3%', width: '275px', height: '250px',
            transform: 'translateX(-50%)', objectFit: 'cover'
        });
        applyPreviewStyle('preview-dyn-name', {
            top: '48%', left: '50%', transform: 'translateX(-50%)',
            fontSize: '50px', fontWeight: '700', textTransform: 'uppercase',
            display: 'inline-block', fontFamily: "'Rajdhani', sans-serif",
            color: '#000033', whiteSpace: 'nowrap'
        });
        applyPreviewStyle('preview-dyn-id', {
            top: '43.7%', left: '42.7%', fontSize: '30px', fontWeight: 'bold',
            color: 'white', fontFamily: "'Rajdhani', sans-serif"
        });
        applyPreviewStyle('preview-dyn-addr', {
            top: '56%', left: '15.5%', width: '50%',
            fontSize: '25px', fontWeight: 'bold', lineHeight: '1.1',
            color: '#000000', whiteSpace: 'nowrap', overflow: 'visible', textOverflow: 'clip'
        });
        applyPreviewStyle('preview-dyn-dob',    { top: '60.8%', left: '26%',   fontSize: '25px', fontWeight: 'bold', color: '#000000' });
        applyPreviewStyle('preview-dyn-gender', { top: '60.7%', left: '77.5%', fontSize: '25px', fontWeight: 'bold', color: '#000000' });
        applyPreviewStyle('preview-dyn-or',     { top: '69%',   left: '77.5%', fontSize: '25px', fontWeight: 'bold', color: '#000000' });
        applyPreviewStyle('preview-dyn-height', { top: '64.3%', left: '26%',   fontSize: '25px', fontWeight: 'bold', color: '#000000' });
        applyPreviewStyle('preview-dyn-weight', { top: '64.3%', left: '77.5%', fontSize: '25px', fontWeight: 'bold', color: '#000000' });
        applyPreviewStyle('preview-dyn-issued', { top: '69.2%', left: '26%',   fontSize: '25px', fontWeight: 'bold', color: '#000000' });
        applyPreviewStyle('preview-dyn-expiry', { top: '73%',   left: '26%',   fontSize: '25px', fontWeight: 'bold', color: '#000000' });
        applyPreviewStyle('preview-dyn-mayor', {
            top: '79.3%', left: '50%', transform: 'translateX(-50%)',
            fontSize: '25px', fontWeight: 'bold', paddingLeft: '50px',
            paddingRight: '50px', display: 'inline-block', color: '#000000',
            whiteSpace: 'nowrap', overflow: 'hidden', maxWidth: '100%'
        });

        document.getElementById('preview-dyn-photo').src       = data.photoUrl;
        document.getElementById('preview-dyn-name').innerText  = data.fullName;
        document.getElementById('preview-dyn-id').innerText    = data.idNum;
        document.getElementById('preview-dyn-addr').innerText  = data.address;

        // Auto-scale address if it overflows its column
        const addrEl    = document.getElementById('preview-dyn-addr');
        const container = addrEl.parentElement;
        const maxWidth  = container.offsetWidth * 0.50;
        const actualWidth = addrEl.scrollWidth;
        if (actualWidth > maxWidth) {
            addrEl.style.transformOrigin = 'left center';
            addrEl.style.transform = `scaleX(${maxWidth / actualWidth})`;
        } else {
            addrEl.style.transform = 'scaleX(1)';
        }

        document.getElementById('preview-dyn-dob').innerText    = data.dob;
        document.getElementById('preview-dyn-gender').innerText = data.gender || '';
        document.getElementById('preview-dyn-or').innerText     = data.orNumber || '';
        document.getElementById('preview-dyn-height').innerText = data.height ? data.height + ' cm' : '';
        document.getElementById('preview-dyn-weight').innerText = data.weight ? data.weight + ' kg' : '';
        document.getElementById('preview-dyn-issued').innerText = data.dateIssued || '';
        document.getElementById('preview-dyn-expiry').innerText = data.expiryDate || '';
        document.getElementById('preview-dyn-mayor').innerText  = 'MARY DOMINIQUE OÑATE';

    } else {
        document.getElementById('preview-template-bg').src = cfg.template2Img;

        applyPreviewStyle('preview-dyn-photo', {
            top: '16%', left: '50%', transform: 'translateX(-50%)',
            width: '257px', height: '257px', borderRadius: '8px'
        });
        applyPreviewStyle('preview-dyn-name', {
            top: '59.1%', left: '50%', transform: 'translateX(-50%)',
            fontSize: '35px', fontWeight: 'bold', textTransform: 'uppercase',
            backgroundColor: '#F5F5F0', border: '2px solid #141414',
            borderRadius: '8px', padding: '8px 20px', whiteSpace: 'nowrap'
        });
        applyPreviewStyle('preview-dyn-id', {
            top: '43%', left: '50%', transform: 'translateX(-50%)',
            fontSize: '30px', backgroundColor: '#F5F5F0',
            border: '2px solid #fff', borderRadius: '5px',
            padding: '6px', width: '270px', textAlign: 'center'
        });
        applyPreviewStyle('preview-dyn-addr', {
            top: '75%', left: '50%', transform: 'translateX(-50%)',
            width: '85%', textAlign: 'center', fontSize: '20px',
            fontWeight: 'bold', backgroundColor: '#F5F5F0',
            border: '2px solid #505050', borderRadius: '8px', padding: '12px 16px'
        });

        ['preview-dyn-dob', 'preview-dyn-gender', 'preview-dyn-or',
         'preview-dyn-height', 'preview-dyn-weight', 'preview-dyn-issued',
         'preview-dyn-expiry', 'preview-dyn-mayor'
        ].forEach(id => { document.getElementById(id).style.display = 'none'; });

        document.getElementById('preview-dyn-photo').src      = data.photoUrl;
        document.getElementById('preview-dyn-name').innerText = data.fullName;
        document.getElementById('preview-dyn-id').innerText   = 'ID No: ' + data.idNum;
        document.getElementById('preview-dyn-addr').innerText = 'Address: ' + data.address;
    }

    setTimeout(() => $('#printPreviewModal').modal('show'), 400);
}

function triggerPrintAfterImageLoad(photoElement) {
    let printed = false;
    const triggerPrint = () => {
        if (!printed) {
            printed = true;
            $('#printConfirmModal').modal('hide');
            setTimeout(() => {
                window.print();
                document.getElementById('print-area').classList.remove('active');
                document.getElementById('print-area-2').classList.remove('active');
                pendingPrintData = null;
            }, 300);
        }
    };
    if (photoElement.complete && photoElement.naturalHeight !== 0) {
        triggerPrint();
    } else {
        photoElement.onload  = triggerPrint;
        photoElement.onerror = triggerPrint;
    }
}

/* ── DOM Ready ───────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {
    const cfg = window.IDCARD_CONFIG;

    /* Import ZIP */
    document.getElementById('importIdCardZipBtn').addEventListener('click', function () {
        document.getElementById('importIdCardZipForm').submit();
    });

    /* ── DataTable ─────────────────────────────────────────────────── */
    var table = $('#dataTable').DataTable({
        processing:  true,
        serverSide:  true,
        ajax:        { url: cfg.datatableUrl, type: 'GET' },
        pageLength:  10,
        lengthChange: false,
        ordering:    false,
        searching:   true,
        dom:         'frtip',
        columns: [
            { data: 0, orderable: false, searchable: false },   // Image
            { data: 1 },                                         // ID Number
            {
                data: 2,
                render: function (data, type, row) {
                    var gender = row[3];
                    var badge  = '';
                    if (gender) {
                        var cls  = gender === 'Male'   ? 'badge-info'    : (gender === 'Female' ? 'badge-success' : 'badge-secondary');
                        var icon = gender === 'Male'   ? 'fa-mars'       : (gender === 'Female' ? 'fa-venus'      : 'fa-genderless');
                        badge = '<br><span class="badge ' + cls + ' badge-sm"><i class="fas ' + icon + '"></i> ' + gender + '</span>';
                    }
                    return '<span>' + data + '</span>' + badge;
                }
            },
            { data: 3, visible: false, searchable: true },      // Gender (hidden)
            {
                data: 4,
                render: function (data, type, row) {
                    var height = row[7], weight = row[8], badges = '';
                    if (height) badges += '<br><span class="badge badge-info badge-sm"><i class="fas fa-ruler-vertical"></i> ' + height + ' cm</span>';
                    if (weight) badges += ' <span class="badge badge-secondary badge-sm"><i class="fas fa-weight"></i> ' + weight + ' kg</span>';
                    return '<span>' + (data || '') + '</span>' + badges;
                }
            },
            {
                data: 5,
                render: function (data, type, row) {
                    var orNo  = row[6];
                    var badge = orNo ? '<br><span class="badge badge-warning badge-sm"><i class="fas fa-receipt"></i> ' + orNo + '</span>' : '';
                    return '<span>' + (data || '') + '</span>' + badge;
                }
            },
            { data: 6,  visible: false, searchable: true },     // OR No (hidden)
            { data: 7,  visible: false, searchable: true },     // Height (hidden)
            { data: 8,  visible: false, searchable: true },     // Weight (hidden)
            {
                data: 9,
                render: function (data, type, row) {
                    var expiry = row[10];
                    var badge  = expiry ? '<br><span class="badge badge-danger badge-sm"><i class="fas fa-calendar-times"></i> ' + expiry + '</span>' : '';
                    return '<span>' + (data || '') + '</span>' + badge;
                }
            },
            { data: 10, visible: false, searchable: true },     // Expiry (hidden)
            { data: 11, orderable: false, searchable: false }   // Action
        ]
    });

    /* Column search — skip non-searchable columns */
    table.columns().every(function (index) {
        var that = this;
        if ([0, 3, 6, 7, 8, 10, 11].includes(index)) return;
        $('input', this.header()).on('keyup change clear', function () {
            if (that.search() !== this.value) {
                that.search(this.value).draw();
            }
        });
    });

    /* ── VIEW ──────────────────────────────────────────────────────── */
    $('#dataTable tbody').on('click', '.btn-view-card', function () {
        var d = $(this).data();
        document.getElementById('view-image').src              = d.image || '';
        document.getElementById('view-name').textContent       = d.name || 'N/A';
        document.getElementById('view-id-number').textContent  = d.idnumber || 'N/A';
        document.getElementById('view-gender').textContent     = d.gender || 'N/A';
        document.getElementById('view-dob').textContent        = d.dob || 'N/A';
        document.getElementById('view-address').textContent    = d.address || 'N/A';
        document.getElementById('view-height').textContent     = d.height ? d.height + ' cm' : 'N/A';
        document.getElementById('view-weight').textContent     = d.weight ? d.weight + ' kg' : 'N/A';
        document.getElementById('view-or-number').textContent  = d.ornumber || 'N/A';
        document.getElementById('view-date-issued').textContent = d.dateissued || 'N/A';
        document.getElementById('view-expiry-date').textContent = d.expiry || 'N/A';
        $('#viewIdCardModal').modal('show');
    });

    /* ── UPDATE ────────────────────────────────────────────────────── */
    $('#dataTable tbody').on('click', '.btn-update-card', function () {
        var d = $(this).data();
        document.getElementById('update-card-id').value        = d.id;
        document.getElementById('update-name').value           = d.name || '';
        document.getElementById('update-id-number').value      = d.idnumber || '';
        document.getElementById('update-gender').value         = d.gender || 'M';
        document.getElementById('update-dob').value            = formatDateForInput(d.dob);
        document.getElementById('update-address').value        = d.address || '';
        document.getElementById('update-or-number').value      = d.ornumber || '';
        document.getElementById('update-height').value         = d.height || '';
        document.getElementById('update-weight').value         = d.weight || '';
        document.getElementById('update-date-issued').value    = formatDateForInput(d.dateissued);
        document.getElementById('update-expiry-date').value    = formatDateForInput(d.expiry);
        document.getElementById('update-current-photo').src    = d.image || '';
        $('#updateIdCardModal').modal('show');
    });

    /* ── DELETE ────────────────────────────────────────────────────── */
    let pendingDeleteId = null;

    $('#dataTable tbody').on('click', '.btn-delete-card', function () {
        pendingDeleteId = $(this).data('id');
        document.getElementById('delete-card-name').textContent = $(this).data('name') || 'this record';
        $('#deleteIdCardModal').modal('show');
    });

    document.getElementById('confirmDeleteBtn').addEventListener('click', function () {
        if (!pendingDeleteId) return;
        fetch(`/idcards/delete/${pendingDeleteId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': cfg.csrfToken }
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                $('#deleteIdCardModal').modal('hide');
                location.reload();
                pendingDeleteId = null;
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(err => console.error(err));
    });

    /* ── PRINT (open confirm modal) ────────────────────────────────── */
    $('#dataTable tbody').on('click', '.btn-print-card', function () {
        var d = $(this).data();
        preparePrint(d.image, d.name, d.idnumber, d.address, d.dob, d.gender,
                     d.ornumber, d.height, d.weight, d.dateissued, d.expiry, d.dmonate);
    });

    /* ── SAVE ADD ──────────────────────────────────────────────────── */
    document.getElementById('saveIdCardBtn').addEventListener('click', function () {
        const btn = this;
        btn.disabled   = true;
        btn.innerHTML  = '<span class="spinner-border spinner-border-sm mr-1" role="status" aria-hidden="true"></span> Saving...';
        document.getElementById('sidebar-loader').classList.add('active');

        fetch(cfg.addUrl, {
            method:  'POST',
            body:    new FormData(document.getElementById('idCardForm')),
            headers: { 'X-CSRFToken': cfg.csrfToken }
        })
        .then(r => {
            if (r.ok) {
                $('#addIdCardModal').modal('hide');
                location.reload();
            } else {
                document.getElementById('sidebar-loader').classList.remove('active');
                btn.disabled  = false;
                btn.innerHTML = '<i class="fas fa-save"></i> Save';
                alert('Something went wrong. Please try again.');
            }
        })
        .catch(err => {
            document.getElementById('sidebar-loader').classList.remove('active');
            btn.disabled  = false;
            btn.innerHTML = '<i class="fas fa-save"></i> Save';
            console.error(err);
            alert('Something went wrong. Please check your connection.');
        });
    });

    /* ── SAVE UPDATE ───────────────────────────────────────────────── */
    document.getElementById('updateIdCardBtn').addEventListener('click', function () {
        const btn = this;
        btn.disabled  = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm mr-1" role="status" aria-hidden="true"></span> Updating...';
        document.getElementById('sidebar-loader').classList.add('active');

        fetch(cfg.updateUrl, {
            method:  'POST',
            body:    new FormData(document.getElementById('updateIdCardForm')),
            headers: { 'X-CSRFToken': cfg.csrfToken }
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                $('#updateIdCardModal').modal('hide');
                location.reload();
            } else {
                document.getElementById('sidebar-loader').classList.remove('active');
                btn.disabled  = false;
                btn.innerHTML = '<i class="fas fa-check"></i> Update';
                alert('Error: ' + data.message);
            }
        })
        .catch(err => {
            document.getElementById('sidebar-loader').classList.remove('active');
            btn.disabled  = false;
            btn.innerHTML = '<i class="fas fa-check"></i> Update';
            console.error(err);
            alert('Something went wrong. Please check your connection.');
        });
    });

    /* ── PRINT TEMPLATE SELECTION ──────────────────────────────────── */
    document.getElementById('printId1Btn').addEventListener('click', function () { executePrint(1); });
    document.getElementById('printId2Btn').addEventListener('click', function () { executePrint(2); });

    /* ── CONFIRM PRINT ─────────────────────────────────────────────── */
    document.getElementById('confirmPrintBtn').addEventListener('click', function () {
        $('#printPreviewModal').modal('hide');
        const data   = pendingPrintData;
        const idType = currentPrintType;

        document.getElementById('print-area').classList.remove('active');
        document.getElementById('print-area-2').classList.remove('active');

        if (idType === 1) {
            document.getElementById('print-photo').src              = data.photoUrl;
            document.getElementById('print-name').innerText         = data.fullName;
            document.getElementById('print-id-number').innerText    = data.idNum;
            document.getElementById('print-address').innerText      = data.address;
            document.getElementById('print-dob').innerText          = data.dob;
            document.getElementById('print-gender').innerText       = data.gender || '';
            document.getElementById('print-or-number').innerText    = data.orNumber || '';
            document.getElementById('print-height').innerText       = data.height ? data.height + ' cm' : '';
            document.getElementById('print-weight').innerText       = data.weight ? data.weight + ' kg' : '';
            document.getElementById('print-date-issued').innerText  = data.dateIssued || '';
            document.getElementById('print-expiry-date').innerText  = data.expiryDate || '';
            document.getElementById('print-dm-onate').innerText     = 'MARY DOMINIQUE OÑATE';
            document.getElementById('print-area').classList.add('active');
            triggerPrintAfterImageLoad(document.getElementById('print-photo'));
        } else {
            document.getElementById('print-photo-2').src             = data.photoUrl;
            document.getElementById('print-name-2').innerText        = data.fullName;
            document.getElementById('print-id-number-2').innerText   = 'ID No: ' + data.idNum;
            document.getElementById('print-address-2').innerText     = 'Address: ' + data.address;
            document.getElementById('print-area-2').classList.add('active');
            triggerPrintAfterImageLoad(document.getElementById('print-photo-2'));
        }
    });
});