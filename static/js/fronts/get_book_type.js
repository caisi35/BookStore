var app = angular.module('demo', []);

app.controller('Hello', function ($scope, $http) {
        $http.get($SCRIPT_ROOT + '/get_book_type').then(function (response) {
            $scope.types = response.data;
            // console.log($scope.types)
        });
    });


app.controller('Order', function ($scope, $http) {
        $http.get($SCRIPT_ROOT + '/orders/get_order_badge').then(function (response) {
            $scope.total = response.data;
            // console.log($scope.total);
        })
    });