$(document).ready(function () {

  $("body").on('click', '.sidebar ul a, a#index, a.read_more, a.pagination_', function (e) {
    e.preventDefault();
    var page_url = $(e.currentTarget).attr('href');
    $.ajax({
      type: 'GET',
      url: $SCRIPT_ROOT + page_url,
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function (data) {
        var content_data = $(data['data']).find('#ajax_content');
        $('#content').hide().html(content_data).fadeIn('slow');

        // update the page title
        $('title').html(data['title']);

        // update the URL
        window.history.pushState("", "", page_url);

        // scroll to top
        window.scrollTo(0, 0);
      }
    });
  });
});

// shorter version of console.log
function c(val) {
  console.log(val);
}