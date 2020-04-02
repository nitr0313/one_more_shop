Vue.filter('truncatewords', function (value, len) {
    if (!value) return 'Здесь пока пусто';
    value = value.toString().split(" ");
    return value.slice(0, len).join(' ') + '...'

});

new Vue({
        el: '#list_book',
        data: {
            books: [],
            hn: '123',
        },
        created: function () {
            const vm = this;
            axios.get('/api/v1/list_book')
                .then(function (response) {
                    vm.books = response.data;
                    vm.hn = window.location.host;
                    // console.log("ЛОГГГГИРОВАНИЕ !!!! " + vm.hostname);
                })

        }
    }
);

new Vue({
    el: '.card-text',
    data: {
        show: true
    },
    methods: {
    }

});

