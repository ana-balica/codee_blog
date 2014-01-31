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
                $('#content').hide().html(data['data']).fadeIn('slow');
                // update the page title
                $('title').html(data['title']);
                // update the URL
                window.history.pushState("", "", page_url);
                // scroll to top
                window.scrollTo(0, 0);
                // syntax highlight everything on page
                Rainbow.color();
            }
        });
    });

    $("body").on('submit', 'form', function (event) {
        event.preventDefault();
        var $name = $("#name").val();
        var $email = $("#email").val();
        var $message = $("#message").val();
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/contact',
            data: { name: $name, email: $email, message: $message },
            contentType: "application/x-www-form-urlencoded; charset=utf-8",
            success: function (data) {
                c(data);
            }
        });
    });
});

// shorter version of console.log
function c(val) {
    console.log(val);
}
