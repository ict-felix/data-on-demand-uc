/*global angular, console, document, google, alert, Highcharts*/
/*jslint node: true, newcap: true*/
'use strict';

angular.module('DataPreprocOnDemandApp', [
  'ui.router',
  'ngTable',
  'ucControllers',
  'ucServices'
]).
config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/error');

    $stateProvider
        .state('home', {
            url: '',
            views: {
                map: {
                    controller: 'MapController'
                },
                files: {
                    templateUrl: '/static/files/file_table.html',
                    controller: 'FilesController'
                },
                operations: {
                    templateUrl: '/static/files/operation_panel.html',
                    controller: 'OperationsController'
                },
                charts: {
                    templateUrl: '/static/files/results.chart.html',
                    controller: 'ChartsController'
                }
            }
        });
}]).
run(function () {
    console.log('Frontend started!');
});
