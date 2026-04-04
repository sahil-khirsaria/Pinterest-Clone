// Pin card click — navigate to detail unless clicking an interactive element
$(document).on('click', '.card-pin[data-href]', function(e) {
  if ($(e.target).closest('a, button, form, input, .board-trigger').length) {
    return;
  }
  window.location.href = $(this).data('href');
});

// Board dropdown toggle
function toggleBoard(e, btn) {
  e.preventDefault();
  e.stopPropagation();
  var dropdown = btn.parentElement.querySelector('.board-dropdown');
  // Close all other open dropdowns first
  document.querySelectorAll('.board-dropdown.open').forEach(function(d) {
    if (d !== dropdown) d.classList.remove('open');
  });
  dropdown.classList.toggle('open');
}

// Close board dropdown when clicking outside
$(document).on('click', function(e) {
  if (!$(e.target).closest('.board-trigger').length) {
    $('.board-dropdown.open').removeClass('open');
  }
});

// Toggle reply form visibility
$(document).on('click', '.reply-toggle', function(e) {
  e.preventDefault();
  $(this).closest('.comment-item').find('> .reply-form').toggle();
});

// Show first tab and mark it active on page load
if ($('#demo1').length) {
  $('#demo1').show();
  $('#btn1').addClass('active');
}

$('#btn1').click(function() {
  $('#demo2').hide();
  $('#demo3').hide();
  $('#demo1').show();
  $('.profile-tabs .btn').removeClass('active');
  $(this).addClass('active');
});

$('#btn2').click(function() {
  $('#demo1').hide();
  $('#demo3').hide();
  $('#demo2').show();
  $('.profile-tabs .btn').removeClass('active');
  $(this).addClass('active');
});

$('#btn3').click(function() {
  $('#demo1').hide();
  $('#demo2').hide();
  $('#demo3').show();
  $('.profile-tabs .btn').removeClass('active');
  $(this).addClass('active');
});