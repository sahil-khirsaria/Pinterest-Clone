$( document ).ready(function() {

});

$('#demo1').toggle()

$('#btn1').click(function() {
  $('#demo2').hide();
  $('#demo3').hide();
  $('#demo1').show();
});

$('#btn2').click(function() {
  $('#demo1').hide();
  $('#demo3').hide();
  $('#demo2').show();
});

$('#btn3').click(function() {
  $('#demo1').hide();
  $('#demo2').hide();
  $('#demo3').show();
});