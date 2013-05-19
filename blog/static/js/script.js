$(document).ready(function() {
  $("a:contains('about')").click(function(e) {
    e.preventDefault();
    c('cliked');
    $.ajax({
      type: 'GET',
      url: $SCRIPT_ROOT + '/about',
      contentType: "application/json; charset=utf-8",
      success: function(data) {
        var content_data = $(data['data']).find('#ajax_content');
        $('#content').hide().html(content_data).fadeIn('slow');
      }
    });
  });
});

// shorter version of console.log
function c(val) {
  console.log(val);
}