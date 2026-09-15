$(document).ready(function () {

  $('#btn-add-experience').on('click', function (e) {
    e.preventDefault();
    const index = $('#experience-repeater-container .repeater-item').length + 1;
    const template = `
      <div class="repeater-item experience-entry">
        <button type="button" class="btn-remove-item" title="Remove Experience">
          <i class="bi bi-x-circle-fill fs-5"></i>
        </button>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label small text-muted">Job Title</label>
            <input type="text" name="exp_title[]" class="form-control" placeholder="e.g. Senior Software Engineer" required>
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted">Company Name</label>
            <input type="text" name="exp_company[]" class="form-control" placeholder="e.g. Acme Corp" required>
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted">Time Period</label>
            <input type="text" name="exp_period[]" class="form-control" placeholder="e.g. 2021 - Present">
          </div>
          <div class="col-12">
            <label class="form-label small text-muted">Key Achievements & Responsibilities</label>
            <textarea name="exp_description[]" class="form-control" rows="2" placeholder="Describe main projects, tech stack utilized, and quantifiable achievements..."></textarea>
          </div>
        </div>
      </div>
    `;

    const $newItem = $(template).hide();
    $('#experience-repeater-container').append($newItem);
    $newItem.slideDown(250);
  });

  $('#btn-add-education').on('click', function (e) {
    e.preventDefault();
    const template = `
      <div class="repeater-item education-entry">
        <button type="button" class="btn-remove-item" title="Remove Education">
          <i class="bi bi-x-circle-fill fs-5"></i>
        </button>
        <div class="row g-3">
          <div class="col-md-5">
            <label class="form-label small text-muted">Degree / Certificate</label>
            <input type="text" name="edu_degree[]" class="form-control" placeholder="e.g. B.S. in Computer Science" required>
          </div>
          <div class="col-md-5">
            <label class="form-label small text-muted">School / University</label>
            <input type="text" name="edu_institution[]" class="form-control" placeholder="e.g. Stanford University" required>
          </div>
          <div class="col-md-2">
            <label class="form-label small text-muted">Graduation Year</label>
            <input type="text" name="edu_year[]" class="form-control" placeholder="e.g. 2020">
          </div>
        </div>
      </div>
    `;

    const $newItem = $(template).hide();
    $('#education-repeater-container').append($newItem);
    $newItem.slideDown(250);
  });

  $(document).on('click', '.btn-remove-item', function (e) {
    e.preventDefault();
    const $item = $(this).closest('.repeater-item');
    $item.slideUp(200, function () {
      $(this).remove();
    });
  });
});
