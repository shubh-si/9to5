$(document).ready(function () {
  const $applyForm = $('#job-apply-form');

  if ($applyForm.length === 0) return;

  $('#useProfileResume').on('change', function () {
    if ($(this).is(':checked')) {
      $('#customResumeUploadWrapper').slideUp(200);
    } else {
      $('#customResumeUploadWrapper').slideDown(200);
    }
  });

  $applyForm.on('submit', function (e) {
    e.preventDefault();

    const $btn = $('#btn-submit-application');
    const originalText = $btn.html();
    const $alertContainer = $('#apply-alert-container');

    $alertContainer.empty();
    $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2" role="status"></span>Submitting...');

    const formData = new FormData(this);
    formData.append('ajax', '1');

    $.ajax({
      url: $applyForm.attr('action'),
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      dataType: 'json',
      success: function (response) {
        if (response.status === 'success') {
          $alertContainer.html(`
            <div class="alert alert-success d-flex align-items-center gap-2 mt-3" role="alert">
              <i class="bi bi-check-circle-fill fs-5"></i>
              <div>${response.message}</div>
            </div>
          `);

          $applyForm.find('.form-inputs-group').slideUp(300);
          $btn.removeClass('btn-primary').addClass('btn-success').html('<i class="bi bi-check-lg me-1"></i> Application Submitted');

          window.showToast('success', response.message);

          setTimeout(function () {
            const modalEl = document.getElementById('applyJobModal');
            if (modalEl) {
              const modal = bootstrap.Modal.getInstance(modalEl);
              if (modal) modal.hide();
            }

            $('#btn-open-apply-modal')
              .removeClass('btn-primary')
              .addClass('btn-outline-success disabled')
              .html('<i class="bi bi-check-circle-fill me-1"></i> Applied');
          }, 2500);

        } else {
          $alertContainer.html(`
            <div class="alert alert-danger d-flex align-items-center gap-2 mt-3" role="alert">
              <i class="bi bi-exclamation-triangle-fill fs-5"></i>
              <div>${response.message}</div>
            </div>
          `);
          $btn.prop('disabled', false).html(originalText);
        }
      },
      error: function (xhr) {
        let errorMsg = 'An error occurred while submitting your application.';
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        }
        $alertContainer.html(`
          <div class="alert alert-danger d-flex align-items-center gap-2 mt-3" role="alert">
            <i class="bi bi-exclamation-octagon-fill fs-5"></i>
            <div>${errorMsg}</div>
          </div>
        `);
        $btn.prop('disabled', false).html(originalText);
      }
    });
  });

  $(document).on('change', '.applicant-status-select', function () {
    const $select = $(this);
    const appId = $select.data('app-id');
    const newStatus = $select.val();
    const $badge = $(`#status-badge-${appId}`);

    $.ajax({
      url: `/applications/${appId}/status/`,
      type: 'POST',
      data: {
        status: newStatus,
        ajax: '1'
      },
      dataType: 'json',
      success: function (res) {
        if (res.status === 'success') {
          window.showToast('success', res.message);
          if ($badge.length) {
            $badge.attr('class', `badge ${res.badge_class}`).text(res.status_label);
          }
        }
      },
      error: function () {
        window.showToast('error', 'Failed to update candidate status.');
      }
    });
  });
});
