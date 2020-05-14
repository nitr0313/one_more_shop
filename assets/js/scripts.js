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
const favorites_api_url = '/v1/api/favorites/';
const added_to_favorites_class = 'fa-thumbs-up added';
const not_favorites_class = 'fa-thumbs-o-up';

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
                        $(el).addClass(not_favorites_class);
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
                        $(el).removeClass(not_favorites_class);
                        $(el).addClass(added_to_favorites_class);
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
                        } else {
                            $(el).addClass(not_favorites_class);
                            // Если открыта страница избранного, то при удалении из избранного
                            // больше не карточку этого элемента
                            if (window.location.pathname === "/favorites/") {
                                $(el).parent().parent().parent().parent().attr('hidden', 'true');
                            }
                        }
                        $(el).text(json[i].count);
                    }
                })
            }
        }
    })
}

// CART FUNCTIONALITY
// Action cart

const add_to_cart_url = '/add_to_cart/';
const remove_from_cart_url = '/remove_from_cart/';
const cart_api_url = '/v1/api/cart/';
const added_to_cart_class = 'in-cart';


function add_to_cart() {
    $('.add-to-cart').each((index, el) => {
        $(el).click((e) => {

            e.preventDefault();
            const id = $(el).data('id');
            let quantity = $(el).data('quantity');
            let update_quantity = $(el).data('update');
            if (quantity === undefined) {
                quantity = 1;
                update_quantity = 0;
            }
            console.log("ID " + id + " quantity " + quantity + " update " + update_quantity);
            console.log(el);
            $.ajax({
                url: add_to_cart_url,
                type: 'POST',
                dataType: 'json',
                data: {
                    id: id,
                    quantity: quantity,
                    update_quantity: update_quantity,
                },
                success: (data) => {
                    $(el).title = "Добавить в корзину (" + data.quantity + " уже есть)";
                    get_cart_items();
                }
            })
        })
    })
}


function remove_from_cart(id) {
    let result = 1;
    $.ajax({
        url: remove_from_cart_url,
        type: 'POST',
        dataType: 'json',
        data: {
            id: id,
        },
        success: (data) => {
            console.log("EL: " + id + " удален из корзины ");
            get_cart_items();
        },
        error: (data) => {
            console.log("Ошибка удаления " + data);
            result = 0;
        }
    })
    return result;
}

function get_cart_items() {
    $.getJSON(cart_api_url, (json) => {
            if (json !== null) {
                for (let i = 0; i < json.length; i++) {
                    // TODO Сделать условие для локации, если в корзине то подругому обработка пойдет
                    $('.add-to-cart').each((index, el) => {
                            const id = $(el).data('id');

                            if (json[i].id == id) {
                                $(el).addClass(added_to_cart_class);

                            } else {
                                $(el).removeClass(added_to_cart_class);
                            }
                        }
                    )
                }
            }
        }
    )
}

$(document).ready(function () {
    add_to_cart();
    add_to_favorites();
    get_favorites();
    get_cart_items();

});

$('.carousel').carousel({
    interval: 2000
});
