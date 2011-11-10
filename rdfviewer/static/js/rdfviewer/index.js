$(document).ready(function(){
  $('.work>a').click(function(e){
    $(this.parentNode).find('.copyright').show();
    return false;
  });
  $('#accept').click(function(){
    window.location = $(this.parentNode.parentNode.parentNode)
      .find('a:first').attr('href');
  });
  $('#cancel').click(function(){
    $('.copyright').hide();
  });
});
