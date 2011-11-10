$(document).ready(function(){
  $('.work>a').click(function(e){
    $(this.parentElement).find('.copyright').show();
    return false;
  });
  $('#accept').click(function(){
    window.location = $(this.parentElement.parentElement.parentElement)
      .find('a:first').attr('href');
  });
  $('#cancel').click(function(){
    $('.copyright').hide();
  });
});
