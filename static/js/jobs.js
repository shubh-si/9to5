$(document).ready(function () {
  const $form = $('#job-filter-form');
  const $container = $('#job-cards-container');
  const $pagination = $('#pagination-container');
  const $totalCount = $('#total-jobs-count');
  const $loadingSpinner = $('#filter-loading-spinner');

  if ($form.length === 0) return;

  let debounceTimer = null;

  function performFilter(targetUrl) {
    let url = targetUrl;
    let data = {};

    if (!url) {
      url = $form.attr('action') || window.location.pathname;
      data = $form.serialize();
    }

    $loadingSpinner.removeClass('d-none');
    $container.css('opacity', '0.5');

    $.ajax({
      url: url,
      type: 'GET',
      data: data,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      success: function (res) {
        $container.html(res.html);
        if ($pagination.length && res.pagination_html) {
          $pagination.html(res.pagination_html);
        }
        if ($totalCount.length && typeof res.total_count !== 'undefined') {
          $totalCount.text(res.total_count);
        }

        const queryParams = typeof data === 'string' ? data : $.param(data);
        const newUrl = url.split('?')[0] + (queryParams ? '?' + queryParams : '');
        window.history.pushState({ path: newUrl }, '', newUrl);
      },
      error: function () {
        window.showToast('error', 'Failed to load job listings. Please try again.');
      },
      complete: function () {
        $loadingSpinner.addClass('d-none');
        $container.css('opacity', '1');
      }
    });
  }

  $form.on('input', 'input[type="text"], input[type="search"]', function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      performFilter();
    }, 350);
  });

  $form.on('change', 'select, input[type="radio"], input[type="checkbox"]', function () {
    performFilter();
  });

  $(document).on('click', '.category-filter-btn', function (e) {
    e.preventDefault();
    const catSlug = $(this).data('slug');
    $('#filter-category').val(catSlug).trigger('change');
  });

  $(document).on('click', '#pagination-container .page-link', function (e) {
    e.preventDefault();
    const href = $(this).attr('href');
    if (href && href !== '#' && !$(this).parent().hasClass('disabled')) {
      $('html, body').animate({ scrollTop: $('#job-results-top').offset().top - 80 }, 200);
      performFilter(href);
    }
  });

  $(document).on('click', '#btn-clear-filters', function (e) {
    e.preventDefault();
    $form[0].reset();
    $form.find('select').val('');
    $form.find('input[type="text"], input[type="number"]').val('');
    $form.find('input[type="checkbox"]').prop('checked', false);
    performFilter();
  });
});

