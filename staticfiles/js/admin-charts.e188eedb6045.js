$(document).ready(function () {

  const catCanvas = document.getElementById('categoryChart');
  if (catCanvas) {
    const catLabels = JSON.parse(catCanvas.dataset.labels || '[]');
    const catCounts = JSON.parse(catCanvas.dataset.counts || '[]');

    new Chart(catCanvas, {
      type: 'doughnut',
      data: {
        labels: catLabels,
        datasets: [{
          data: catCounts,
          backgroundColor: [
            '#4f46e5', '#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#64748b'
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 14,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 }
            }
          }
        },
        cutout: '68%'
      }
    });
  }

  const statusCanvas = document.getElementById('statusChart');
  if (statusCanvas) {
    const statusLabels = JSON.parse(statusCanvas.dataset.labels || '[]');
    const statusCounts = JSON.parse(statusCanvas.dataset.counts || '[]');

    new Chart(statusCanvas, {
      type: 'bar',
      data: {
        labels: statusLabels,
        datasets: [{
          label: 'Applications',
          data: statusCounts,
          backgroundColor: [
            '#818cf8', '#fbbf24', '#f87171', '#34d399'
          ],
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, font: { family: "'Plus Jakarta Sans', sans-serif" } },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false },
            ticks: { font: { family: "'Plus Jakarta Sans', sans-serif" } }
          }
        }
      }
    });
  }

  $('.btn-moderate-action').on('click', function (e) {
    e.preventDefault();
    const $btn = $(this);
    const actionUrl = $btn.data('url');
    const actionType = $btn.data('action');
    const $row = $btn.closest('.moderation-row');

    $btn.prop('disabled', true);

    $.ajax({
      url: actionUrl,
      type: 'POST',
      data: { ajax: '1' },
      dataType: 'json',
      success: function (res) {
        if (res.status === 'success') {
          window.showToast('success', res.message);
          $row.css('background-color', actionType === 'approve' ? '#ecfdf5' : '#fef2f2');
          $row.fadeOut(400, function () {
            $(this).remove();

            if ($('#moderation-table-body tr').length === 0) {
              $('#moderation-table-body').html('<tr><td colspan="5" class="text-center text-muted py-4"><i class="bi bi-check2-circle text-success fs-3 d-block mb-1"></i>No pending job listings in the queue.</td></tr>');
            }
          });

          const $badge = $('#pending-counter-badge');
          if ($badge.length) {
            let current = parseInt($badge.text()) || 0;
            $badge.text(Math.max(0, current - 1));
          }
        }
      },
      error: function () {
        window.showToast('error', 'Failed to execute moderation action.');
        $btn.prop('disabled', false);
      }
    });
  });
});
