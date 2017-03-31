$('.add-to-cart').on('submit', 'td', function (event) {
    event.preventDefault();
    var artikel_id = $(this).data('val');
    add_to_cart(artikel_id);
});

function add_to_cart(artikel_id) {
    $.ajax({
        url: '/ajax/addtocart/',
        type: 'POST',
        data: {
            'artikel_id': artikel_id,
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function (data) {
            $('#error-message').html(data);
        }
    });
}

