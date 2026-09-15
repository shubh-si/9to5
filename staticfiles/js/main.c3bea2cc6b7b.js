$(document).ready(function () {

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  window.showToast = function (type, message) {
    let toastContainer = $('#toast-container');
    if (toastContainer.length === 0) {
      $('body').append('<div id="toast-container" class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1090;"></div>');
      toastContainer = $('#toast-container');
    }

    const bgClass = type === 'success' ? 'bg-success text-white' : (type === 'error' ? 'bg-danger text-white' : 'bg-dark text-white');
    const iconClass = type === 'success' ? 'bi-check-circle-fill' : (type === 'error' ? 'bi-exclamation-triangle-fill' : 'bi-info-circle-fill');

    const toastHtml = `
      <div class="toast align-items-center ${bgClass} border-0 shadow-lg mb-2" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body d-flex align-items-center gap-2">
            <i class="bi ${iconClass} fs-5"></i>
            <div>${message}</div>
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    `;

    const $toast = $(toastHtml);
    toastContainer.append($toast);
    const bsToast = new bootstrap.Toast($toast[0], { delay: 4000 });
    bsToast.show();
    $toast.on('hidden.bs.toast', function () {
      $(this).remove();
    });
  };

  $(document).on('click', '.btn-bookmark', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const $btn = $(this);
    const jobId = $btn.data('job-id');

    if (!jobId) return;

    $btn.prop('disabled', true);

    $.ajax({
      url: `/jobs/${jobId}/toggle-save/`,
      type: 'POST',
      dataType: 'json',
      success: function (response) {
        if (response.status === 'success') {
          const $icon = $btn.find('i');
          if (response.saved) {
            $btn.addClass('saved');
            $icon.removeClass('bi-bookmark').addClass('bi-bookmark-fill');
          } else {
            $btn.removeClass('saved');
            $icon.removeClass('bi-bookmark-fill').addClass('bi-bookmark');
          }
          window.showToast('success', response.message);
        }
      },
      error: function (xhr) {
        if (xhr.status === 403 || xhr.status === 401) {
          window.showToast('error', 'Please log in as a Job Seeker to bookmark jobs.');
        } else {
          window.showToast('error', 'Could not update bookmark.');
        }
      },
      complete: function () {
        $btn.prop('disabled', false);
      }
    });
  });

  setTimeout(function () {
    $('.alert-dismissible').fadeOut('slow');
  }, 5000);

  const hash = window.location.hash;
  const urlParams = new URLSearchParams(window.location.search);
  const tabParam = urlParams.get('tab');

  if (hash) {
    const $targetTab = $(`button[data-bs-target="${hash}"], button[data-bs-target="#tab-${hash.replace('#', '')}"]`);
    if ($targetTab.length) {
      $targetTab.tab('show');
    }
  } else if (tabParam) {
    const $targetTab = $(`button[data-bs-target="#tab-${tabParam}"], #${tabParam}-tab`);
    if ($targetTab.length) {
      $targetTab.tab('show');
    }
  }
});

