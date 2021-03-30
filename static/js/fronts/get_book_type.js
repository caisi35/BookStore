var app = angular.module('demo', []);

app.controller('Hello', function ($scope, $http) {
    $http.get($SCRIPT_ROOT + '/get_book_type').then(function (response) {
        $scope.types = response.data;
        // console.log($scope.types)
    });
});

app.controller('all_types', function ($scope, $http) {
    $http.get($SCRIPT_ROOT + '/get_book_all_type').then(function (response) {
        $scope.all_types = response.data;
        // console.log($scope.all_types)
    });
});

app.controller('Order', function ($scope, $http) {
    $http.get($SCRIPT_ROOT + '/orders/get_order_badge').then(function (response) {
        $scope.total = response.data;
        // console.log($scope.total);
    })
});

app.controller('recommend_product', function ($scope, $http) {
    id = document.getElementById('book_id').value;
    // console.log(id);
    $http.get($SCRIPT_ROOT + '/recommend_product/' + id).then(function (response) {
        $scope.recommend_book = response.data;
        // console.log($scope.id);
    })
});

app.controller('recommend_user', function ($scope, $http) {
    $http.get($SCRIPT_ROOT + '/recommend_user').then(function (response) {
        $scope.recommend_book = response.data;
         // console.log($scope.recommend_book);
    })
});

app.controller('recommend_order', function ($scope, $http) {
    $http.get($SCRIPT_ROOT + '/orders/order_for_recommend').then(function (response) {
        $scope.recommend_order = response.data;
         // console.log($scope.recommend_order);
    })
});

app.controller('recommend_cart', function ($scope, $http) {
    $http.get($SCRIPT_ROOT + '/product/add_to_cart/recommend_for_cart').then(function (response) {
        $scope.recommend_cart = response.data;
         console.log($scope.recommend_cart);
    })
});