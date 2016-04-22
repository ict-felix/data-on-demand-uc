/*global angular, Highcharts, Set */
/*jslint node: true */
'use strict';

var ucServices = angular.module('ucServices', []);

ucServices.service('ucService', ['$http', function ($http) {
    this.ping = function () {
        return $http.post('/ping');
    };

    this.getLocations = function () {
        return $http.get('/locations');
    };

    this.getRTT = function () {
        return $http.get('/rtt');
    };

    this.getFiles = function () {
        return $http.get('/smosfiles');
    };

    this.submitRequest = function (body) {
        return $http.post('/submit', body);
    };

    this.sliceCreate = function () {
        return $http.post('/createslice');
    };

    this.sliceDelete = function () {
        return $http.post('/deleteslice');
    };

    this.createChart = function (initcb, loadcb) {
        return new Highcharts.StockChart({
            chart: {
                renderTo: 'periodic-results-chart',
                zoomType: 'x',
                events: {
                    load: function () {
                        var i, series = [];
                        for (i = 0; i < this.series.length; i += 1) {
                            if (this.series[i].name !== "Navigator") {
                                series.push(this.series[i]);
                            }
                        }
                        for (i = 0; i < series.length; i += 1) {
                            loadcb(series[i]);
                        }
                    }
                }
            },
            title: {text: ''},
            xAxis: {
                type: 'datetime',
                labels: {
                    overflow: 'justify',
                    format: '{value:%Y/%m/%d %H:%M:%S}',
                    align: 'right',
                    rotation: -30
                }
            },
            yAxis: {title: {text: 'time (s)'}},
            legend: {enabled: true},
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: {x1: 0, y1: 0, x2: 0, y2: 1},
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: {radius: 2},
                    lineWidth: 1,
                    states: {hover: {lineWidth: 1}},
                    threshold: null
                }
            },
            series: initcb()
        });
    };
}]);

ucServices.factory('operationsService', function () {
    var files = {
        names: []
    };

    files.add = function (n) {
        files.names.push(n);
    };

    return files;
});

ucServices.factory('monitoringService', function () {
    var info = {
        data: []
    };
    info.append = function (d) {
        info.data.push(d);
    };
    info.flush = function () {
        info.data.length = 0;
    };
    return info;
});
