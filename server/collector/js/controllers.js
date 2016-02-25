/*global angular, console, document, google, alert, Highcharts*/
/*jslint node: true, newcap: true*/
'use strict';

var ucControllers = angular.module('ucControllers', ['ui.router', 'ucServices']);

ucControllers.controller('MapController', ['$scope', 'ucService', function ($scope, ucService) {
    var gmap, ginfo;

    function getRTT(event) {
        var info = '<b>RTTs:</b><br><br>';
        ucService.getRTT()
            .success(function (data) {
                info += data;
                // Replace the info window's content and position.
                ginfo.setContent(info);
                ginfo.setPosition(event.latLng);
                ginfo.open(gmap);
            })
            .error(function (e) {
                console.log("Error in getRTT {}", e);
            });
    }

    ucService.getLocations()
        .success(function (data) {
            console.log("Data", data);

            gmap = new google.maps.Map(document.getElementById('map'), {
                zoom: data.zoom,
                center: new google.maps.LatLng(data.centre.latitude, data.centre.longitude)
            });
            ginfo = new google.maps.InfoWindow();

            angular.forEach(data.locations, function (m) {
                var marker = new google.maps.Marker({
                    position: new google.maps.LatLng(m.latitude, m.longitude),
                    map: gmap,
                    title: m.name,
                });
            });

            var polygon = new google.maps.Polygon({
                paths: data.coordinates,
                strokeColor: '#FF0000',
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: '#FF0000',
                fillOpacity: 0.35
            });
            polygon.setMap(gmap);
            polygon.addListener('click', getRTT);
        })
        .error(function (e) {
            console.log("Error in getLocations {}", e);
        });
}]);

ucControllers.controller('FilesController', ['$scope', '$filter', 'ucService', 'ngTableParams', 'operationsService',
                         function ($scope, $filter, ucService, ngTableParams, operationsService) {
    ucService.getFiles()
        .success(function (data) {
            console.log("Data", data);

            $scope.smosFiles = [];
            angular.forEach(data.smosfiles, function(info) {
                angular.forEach(info.data, function(file) {
                    this.push({
                        id: info.id,
                        testbed: info.testbed,
                        address: info.address,
                        port: info.port,
                        file: file
                    });
                    operationsService.add(file);
                }, $scope.smosFiles);
            });
            console.log("SmosFiles", $scope.smosFiles);

            $scope.smosFileTable = new ngTableParams({
                count: 5
            }, {
                counts: [],
                total: $scope.smosFiles.length,
                getData: function ($defer, params) {
                    $scope.smosData = params.sorting() ? $filter('orderBy')($scope.smosFiles, params.orderBy()) : $scope.smosFiles;
                    $scope.smosData = params.filter() ? $filter('filter')($scope.smosData, params.filter()) : $scope.smosData;
                    $scope.smosData = $scope.smosData.slice((params.page() - 1) * params.count(), params.page() * params.count());
                    $defer.resolve($scope.smosData);
                }
            });
        })
        .error(function (e) {
            console.log("Error in getFiles {}", e);
        });
}]);

ucControllers.controller('OperationsController', ['$scope', 'ucService', 'operationsService', 'monitoringService',
                         function ($scope, ucService, operationsService, monitoringService) {
    $scope.fileOptions = operationsService.names;

    $scope.submit = function () {
        console.log("Inputs", $scope.fileActive, $scope.host, $scope.destination, $scope.username, $scope.password);
        if (angular.isUndefined($scope.fileActive)) {
            alert("Please specify the FILE!");

        } else if (angular.isUndefined($scope.host)) {
            alert("Please insert the HOST!");

        } else if (angular.isUndefined($scope.destination)) {
            alert("Please insert the DESTINATION!");

        } else if (angular.isUndefined($scope.username)) {
            alert("Please insert the USERNAME!");

        } else if (angular.isUndefined($scope.password)) {
            alert("Please insert the PASSWORD!");

        } else {
            var info = {
                file: $scope.fileActive,
                host: $scope.host,
                destination: $scope.destination,
                username: $scope.username,
                password: $scope.password
            };
            ucService.submitRequest(info)
                .success(function (data) {
                    console.log("Data", data);
                    var i, len, value;
                    for (i = 0, len = data.length; i < len; i += 1) {
                        value = data[i].value.endtime - data[i].value.starttime;
                        monitoringService.append([parseInt(data[i].value.starttime * 1000, 10), value]);
                        monitoringService.append([parseInt(data[i].value.endtime * 1000, 10), value]);
                    }
                })
                .error(function (e) {
                    alert("submitRequest failed! Please analyse the log file.\n" + e);
                });
        }
    };
}]);

ucControllers.controller('ChartsController', ['$scope', '$interval', 'ucService', 'monitoringService',
                         function ($scope, $interval, ucService, monitoringService) {
    Highcharts.setOptions({
        global: {useUTC: false}
    });

    $scope.timer = null;

    var chart = ucService.createChart(function () {
        return [{
            step: true,
            name: "real-time",
            data: []
        }];
    }, function (series) {
        $scope.timer = $interval(function () {
            console.log("monitoring-data length", monitoringService.data.length);
            series.setData(monitoringService.data, true, true);
        }, 5000);
    });

    $scope.$on("$destroy", function () {
        if (angular.isDefined($scope.timer)) {
            $interval.cancel($scope.timer);
        }
    });
}]);

ucControllers.controller('SliceController', ['$scope', 'ucService', function ($scope, ucService) {
    $scope.createSlice = function () {
        console.log("create-slice");

        ucService.sliceCreate()
            .success(function (data) {
                console.log("Data", data);
            })
            .error(function (e) {
                alert("Slice creation failed! Please analyse the log file.\n" + e);
            });
    };

    $scope.deleteSlice = function () {
        console.log("delete-slice");

        ucService.sliceDelete()
            .success(function (data) {
                console.log("Data", data);
            })
            .error(function (e) {
                alert("Slice deletion failed! Please analyse the log file.\n" + e);
            });
    };
}]);
