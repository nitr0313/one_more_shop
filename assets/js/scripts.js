// DJANGO AJAX SETUP

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);

            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }

        }
    }
    return cookieValue
}

const csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
}

$.ajaxSetup({
    beforeSend: (xhr, settings) => {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
});

// END DJANGO AJAX SETUP


const add_to_favorites_url = '/add_to_fav/';
const remove_from_favorites_url = '/remove_fav/';
const favorites_api_url = '/v1/api/';
const added_to_favorites_class = 'added';

function add_to_favorites() {
    $('.add-to-favorites').each((index, el) => {
        $(el).click((e) => {
            e.preventDefault();

            const type = $(el).data('type');
            const id = $(el).data('id');
            console.log(el);
            if ($(e.target).hasClass(added_to_favorites_class)) {
                console.log('has class ' + added_to_favorites_class);
                $.ajax({
                    url: remove_from_favorites_url,
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        type: type,
                        id: id,
                    },
                    success: (data) => {
                        $(el).removeClass(added_to_favorites_class);
                        // $('form[name="remove-from-favorites-' + type + '-' + id + '"]').css('display', 'none');

                        get_favorites()
                    }
                });
            } else {
                console.log('has NO class ' + added_to_favorites_class);
                $.ajax({
                    url: add_to_favorites_url,
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        type: type,
                        id: id,
                    },
                    success: (data) => {
                        $(el).addClass(added_to_favorites_class);
                        // $('form[name="remove-from-favorites-' + type + '-' + id + '"]').css('display', 'none');

                        get_favorites()
                    }
                })

            }

        })
    })

}

function get_favorites() {
    // get_session_favorites_statistics();

    $.getJSON(favorites_api_url, (json) => {
        if (json !== null) {
            for (let i = 0; i < json.length; i++) {
                // console.log(json[i]);
                $('.add-to-favorites').each((index, el) => {
                    const type = $(el).data('type');
                    const id = $(el).data('id');

                    if (json[i].type == type && json[i].id == id) {
                        if (json[i].user_has === true) {
                            $(el).addClass(added_to_favorites_class);
                        }
                        $(el).children(":first").text(json[i].count);
                    }
                })
            }
        }
    })
}


// function get_session_favorites_statistics() {
//     $.getJSON(favorites_api_url, (json) => {
//         let O = $('#favorites-statistics');
//         if (json !== null) {
//             O.empty();
//             let sites_plural = json.length > 1 ? ' objects' : ' objects';
//             O.html(json.length + sites_plural + ' ' + json.toString())
//         } else {
//             O.empty();
//         }
//     })
//
// }

$(document).ready(function () {
    add_to_favorites();
    get_favorites();
});
