var templateModule = angular.module('templateModule',['ngRoute','ngAnimate'])

/*  Configuration    */

// Application routing
templateModule.config(function($routeProvider, $locationProvider){
    $routeProvider
        .when('/', {templateUrl: 'ng/dashboard'})
        .when('/devices', {templateUrl: 'ng/devices'})
        .when('/devices/add', {templateUrl: 'ng/devices/add'})

        .when('/models', {templateUrl: 'ng/models'})
        .when('/models/add', {templateUrl: 'ng/models/add'})

        .when('/basic-config', {templateUrl: 'ng/basic-config'})



    $locationProvider.html5Mode(true);
});

// To avoid conflicts with other template tools such as Jinja2, all between {a a} will be managed by angular instead of {{ }}
templateModule.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);


/*  Services    */

// Store the current operation for the element: Add, view, edit or delete
templateModule.service('operationService', function() {
    var operation = ''
    function set(data) {
        operation = data;
    }
    function get() {
        return operation;
    }

    return {
        set: set,
        get: get
    }

});


// Store the devices
templateModule.service('DevicesService', function($http, NotifyingService) {
    var selected_device =   {
                            name: '', ip: '', authgroup: '', port: '', device_type: '',
                            current_configuration: {
                                hostname: '',
                                ntp_server: ''
                                },
                            changed_configuration: {
                                hostname: '',
                                ntp_server: ''
                                }
                            };
    var devices = []

    function restart_selection(){
        selected_device = {
                            name: '', ip: '', authgroup: '', port: '', device_type: '',
                            current_configuration: {
                                hostname: '',
                                ntp_server: ''
                                },
                            changed_configuration: {
                                hostname: '',
                                ntp_server: ''
                                }
                            };
        }

    function getDevices(){
        return devices;
    }

    function getSelectedDevice(){
        return selected_device
    }

    function init(){

    }

    init();


    return {
        getDevices: getDevices,
        getSelectedDevice: getSelectedDevice,
        restart_selection: restart_selection
    };
});

// Store the device models
templateModule.service('ModelService', function($http) {
    var selected_model = {id: '', name: ''}
    var models = []

    function restart_selection(){
        selected_model = {id: '', name: ''}
    }

    function getModels(){
        return models;
    }

    function getSelectedModel(){
        return selected_model
    }


    function setSelectedModel(model){

        selected_model = model
    }

    function init(){

    }

    init();


    return {
        getModels: getModels,
        getSelectedModel: getSelectedModel,
        setSelectedModel: setSelectedModel,
        restart_selection: restart_selection
    };
});



//Store the authgroups

templateModule.service('AuthgroupsService', function($http, NotifyingService) {
    var authgroups = []

    function getAuthgroups(){
        return authgroups;
    }

    function init(){
    }

    init();

    return {
        getAuthgroups: getAuthgroups
    };
});

/*  Factories */
// The notify service allows services to notify to an specific controller when they finish operations
templateModule.factory('NotifyingService', function($rootScope) {
    return {
        subscribe: function(scope, callback) {
            var handler = $rootScope.$on('notifying-service-event', callback);
            scope.$on('$destroy', handler);
        },

        notify: function() {
            $rootScope.$emit('notifying-service-event');
        }
    };
});



/*  Controllers    */


//Location controller is in charge of managing the routing location of the application
templateModule.controller('LocationController', function($scope, $location){
     $scope.go = function ( path ) {
        $location.path( path );
    };
});

//Device controller is in charge of managing the devices data
templateModule.controller('DeviceController', function($scope, $location, $http, DevicesService, AuthgroupsService, ModelService){


    $scope.loader = {loading : false};

    $scope.selected_device = DevicesService.getSelectedDevice();
    $scope.devices = []
    $scope.authgroups = AuthgroupsService.getAuthgroups();

    $scope.setSelectedDevice = function(device){

        $scope.selected_device = device
    };

    $scope.saveDevice = function(){
        $scope.loader.loading = true;
        $scope.selected_device.model = ModelService.getSelectedModel();
        $scope.promise = $http
            .post("ng" + $location.path(), $scope.selected_device)
            .then(function (response, status, headers, config){
                if ($location.path() === '/devices/add'){
                    $location.path('/devices');
                    create_notification('Success!','' , 'success', 5000)
                }
                if ($location.path() === '/basic-config'){
                    create_notification('Success!','Updating device information' , 'success', 5000)
                    DevicesService.restart_selection();
                    $scope.selected_device = DevicesService.getSelectedDevice();
                    $scope.refreshDevicesFromServer();
                }
            })
            .catch(function(response, status, headers, config){
               create_notification('Error', response.data.message , 'danger', 0)
               $scope.loader.loading = false;
            })
            .finally(function(){
            })
    };


    $scope.deleteDevice = function(){
        $scope.loader.loading = true;
        $scope.promise = $http
            .post("ng/devices/delete", $scope.selected_device)
            .then(function (response, status, headers, config){
                $location.path('/devices');
                create_notification('Success!','' , 'success', 5000);
            })
            .catch(function(response, status, headers, config){
               create_notification('Error', response.data.message , 'danger', 0)

            })
            .finally(function(){
                DevicesService.restart_selection();
                $scope.loader.loading = false;
                $scope.refreshDevicesFromServer();
            });
    };

    $scope.refreshDevicesFromServer = function (){
        $scope.devices = []
        $scope.loader.loading = true;
        $http
            .post("ng/api/devices/")
            .then(function (response, status, headers, config){
                $scope.devices = response.data;
            })
            .catch(function(response, status, headers, config){
                create_notification('Error getting devices', response.data.message , 'danger', 0)
            })
            .finally(function(){
                $scope.loader.loading = false;
            })
    };

    $scope.refreshAuthgruopsFromServer = function (){
        $http
            .post("ng/api/authgroups/")
            .then(function (response, status, headers, config){
                $scope.authgroups = response.data;
            })
            .catch(function(response, status, headers, config){
                create_notification('Error getting authgroups', response.data.message , 'danger', 0)
            })
    }

    if ($location.path() === '/devices'){
        $scope.refreshDevicesFromServer();
    }

    if ($location.path() === '/devices/add'){
        $scope.refreshAuthgruopsFromServer();
        DevicesService.restart_selection();
    }


    if ($location.path() === '/basic-config'){
        $scope.refreshDevicesFromServer();
        DevicesService.restart_selection();
    }
});


//Model controller is in charge of managing the device models data
templateModule.controller('ModelController', function($scope, $location, $http, ModelService){

    $scope.loader = {loading : false};

    $scope.selected_model = ModelService.getSelectedModel();
    $scope.models = ModelService.getModels();


    $scope.setSelectedModel = function(model){
        $scope.selected_model = model;
        ModelService.setSelectedModel(model);
    };

    $scope.saveModel = function(){
        $scope.loader.loading = true;
        $scope.promise = $http
            .post("ng/models/add", $scope.selected_model)
            .then(function (response, status, headers, config){
                $location.path('/models');
                create_notification('Success!','' , 'success', 5000)
            })
            .catch(function(response, status, headers, config){

               create_notification('Error', response.data.message , 'danger', 0)

            })
            .finally(function(){
                ModelService.restart_selection();
                $scope.loader.loading = false;
            })
    };


    $scope.deleteModel = function(){
        $scope.loader.loading = true;
        $scope.promise = $http
            .post("ng/models/delete", $scope.selected_model)
            .then(function (response, status, headers, config){
                $location.path('/models');
                create_notification('Success!','' , 'success', 5000);
            })
            .catch(function(response, status, headers, config){
               create_notification('Error', response.data.message , 'danger', 0)

            })
            .finally(function(){
                ModelService.restart_selection();
                $scope.loader.loading = false;
                $scope.refreshModelsFromServer();
            });
    };

    $scope.refreshModelsFromServer = function (){
        $scope.loader.loading = true;
        $http
            .post("ng/api/models/")
            .then(function (response, status, headers, config){
                $scope.models = response.data;
            })
            .catch(function(response, status, headers, config){
                create_notification('Error getting devices', response.data.message , 'danger', 0)
            })
            .finally(function(){
                $scope.loader.loading = false;
            })
    };

    if ($location.path() === '/models'){
        $scope.refreshModelsFromServer();
    }

    if ($location.path() === '/devices/add'){
        $scope.refreshModelsFromServer();
    }
});