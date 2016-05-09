/*!
 * Report Generator
 * v0.0.2
 */
(function(window, angular, wb, $) {'use strict';
    var app = angular.module('reportGenerator', ['dataset-types', 'advanced-search', 'display-fields', 'services.config']),
        $resultsTable = $('#results'),
        maxFieldItems = 100,
        queryDefaults = {
            wt: 'json'
        },
        datatableDefaults = {
            columnDefs: [
                {
                    className: 'nowrap right',
                    targets: [0]
                }
            ],
            pageLength: 100,
            lengthMenu: [[50, 100, 200, 500, -1], [50, 100, 200, 500, 'All']]
        };

    app.run(['$http', '$rootScope', 'configuration', function($http, $rootScope, configuration) {

        function createQuery(keywords) {
            var regexp = /(.*?)((?: (?:OR|AND) )|$)/g;

            if (keywords.length === 0) {
                return '*';
            }

            keywords = keywords.replace(regexp, function(match, key, sep) {
                if (key.length !== 0 && !key.match(/:[\(\[].*?[\)\]]/)) {
                    key = 'product_id_new:(' + key + '*) OR text:(' + key + ')';
                }
                return key + sep;
            });
            return keywords;
        }

        function sanitizeData(rows, fields) {
            var row, r, field, f, cell;

            for (r = 0; r < rows.length; r += 1) {
                row = rows[r];

                for (f = 0; f < fields.length; f += 1) {
                    field = fields[f];
                    cell = row[field];

                    row[field] = cell || '';

                    if (typeof cell === 'object') {
                        row[field] = cell.splice(0, maxFieldItems).join(',');
                    }
                }
            }

            return rows;
        }

        function createFieldsMapping(fields) {
            var fieldsMapping = [],
                f;

            for (f = 0; f < fields.length; f += 1) {
                fieldsMapping.push({
                    data: fields[f],
                    title: fields[f],
                });
            }

            return fieldsMapping;
        }

        function maxResultsFromUrl() {
            var maxResults = wb.pageUrlParts.params.rows;

            if ($rootScope.maxResultsOptions[maxResults]) {
                return maxResults;
            }
        }

        $rootScope.query = wb.pageUrlParts.params.q ? decodeURI(wb.pageUrlParts.params.q) : '';
        $rootScope.maxResultsOptions = {
            20: 20,
            50: 50,
            100: 100,
            1000: '1000 (default)',
            2000: 2000
        };
        $rootScope.maxResults = maxResultsFromUrl() || '1000';

        $rootScope.clearKeywords = function() {
            $rootScope.query = '';
        };

        $rootScope.saveUrl = function() {
            var urlParts = wb.pageUrlParts,
                url = urlParts.absolute.replace(urlParts.search, '').replace(urlParts.hash, '');

            $rootScope.savedUrl = url +
                '?fq=' + $rootScope.dataTypeCtrl.selectedDatasetTypes.join(',') +
                '&q=' + $rootScope.query +
                '&fl=' + $rootScope.dspFieldCtrl.fields.join(',') +
                '&rows=' + $rootScope.maxResults;
        };

        $rootScope.sendQuery = function() {
            var url = configuration.solrCore + '/select',
                params = $.extend(queryDefaults, {
                    fq: 'site_id:' + configuration.siteID + ' AND state:active AND dataset_type:(' + $rootScope.dataTypeCtrl.selectedDatasetTypes.join(' OR ') + ')',
                    q: createQuery($rootScope.query),
                    fl: $rootScope.dspFieldCtrl.fields.join(','),
                    rows: parseInt($rootScope.maxResults, 10)
                }),
                httpMethod = $http.get;

            if (configuration.solrCore.indexOf(configuration.ckanInstance) === -1) {
                httpMethod = $http.jsonp;
                params['json.wrf'] = 'JSON_CALLBACK';
            }

            httpMethod(url, {params: params})
                .then(function(data) {
                    $rootScope.queryError = false;
                    $rootScope.queryResultsCount = data.data.response.numFound;
                    $rootScope.queryResults = data.data.response;
                    $rootScope.downloadLink = data.config.url + '?' + $.param($.extend({}, data.config.params, {wt: 'csv', 'csv.mv.separator': '·', rows: 999999999}));

                    var fields = data.data.responseHeader.params.fl.split(','),
                        datatable = $.extend({}, datatableDefaults, {
                            data: sanitizeData($rootScope.queryResults.docs, fields),
                            columns: createFieldsMapping(fields),
                            fnRowCallback: function(row, data) {
                                var name = data.name,
                                    $firstCell = $(row.firstChild);

                                if ($firstCell.find('a').length === 0) {
                                    $firstCell.append(
                                        '<a target="_blank" href="' + configuration.ckanInstance + '/dataset/' + name + '" class="btn btn-default">' +
                                            '<span class="glyphicon glyphicon-eye-open"><span class="wb-inv">View ' + name + '</span></a>' +
                                        '<a target="_blank" href="' + configuration.ckanInstance + '/dataset/edit/' + name + '" class="btn btn-default">' +
                                            '<span class="glyphicon glyphicon-pencil"><span class="wb-inv">Edit ' + name + '</span></a>'
                                    );
                                }
                            }
                        });

                    $resultsTable.DataTable().destroy();
                    $resultsTable.empty();

                    $resultsTable.dataTable(datatable);
                }, function(response) {
                    delete $rootScope.queryResults;
                    $rootScope.queryError = true;

                    if (response && response.data && response.data.error && response.data.error.msg) {
                        $rootScope.queryErrorMessage = response.data.error.msg;
                    }
                });
        };
    }]);

})(window, angular, wb, jQuery);

/**
 * Checklist-model
 * AngularJS directive for list of checkboxes
 */

angular.module('checklist-model', [])
.directive('checklistModel', ['$parse', '$compile', function($parse, $compile) {
  // contains
  function contains(arr, item, comparator) {
    if (angular.isArray(arr)) {
      for (var i = arr.length; i--;) {
        if (comparator(arr[i], item)) {
          return true;
        }
      }
    }
    return false;
  }

  // add
  function add(arr, item, comparator) {
    arr = angular.isArray(arr) ? arr : [];
      if(!contains(arr, item, comparator)) {
          arr.push(item);
      }
    return arr;
  }

  // remove
  function remove(arr, item, comparator) {
    if (angular.isArray(arr)) {
      for (var i = arr.length; i--;) {
        if (comparator(arr[i], item)) {
          arr.splice(i, 1);
          break;
        }
      }
    }
    return arr;
  }

  // http://stackoverflow.com/a/19228302/1458162
  function postLinkFn(scope, elem, attrs) {
    // compile with `ng-model` pointing to `checked`
    $compile(elem)(scope);

    // getter / setter for original model
    var getter = $parse(attrs.checklistModel);
    var setter = getter.assign;
    var checklistChange = $parse(attrs.checklistChange);

    // value added to list
    var value = $parse(attrs.checklistValue)(scope.$parent);


  var comparator = angular.equals;

  if (attrs.hasOwnProperty('checklistComparator')){
    comparator = $parse(attrs.checklistComparator)(scope.$parent);
  }

    // watch UI checked change
    scope.$watch('checked', function(newValue, oldValue) {
      if (newValue === oldValue) {
        return;
      }
      var current = getter(scope.$parent);
      if (newValue === true) {
        setter(scope.$parent, add(current, value, comparator));
      } else {
        setter(scope.$parent, remove(current, value, comparator));
      }

      if (checklistChange) {
        checklistChange(scope);
      }
    });

    // declare one function to be used for both $watch functions
    function setChecked(newArr, oldArr) {
        scope.checked = contains(newArr, value, comparator);
    }

    // watch original model change
    // use the faster $watchCollection method if it's available
    if (angular.isFunction(scope.$parent.$watchCollection)) {
        scope.$parent.$watchCollection(attrs.checklistModel, setChecked);
    } else {
        scope.$parent.$watch(attrs.checklistModel, setChecked, true);
    }
  }

  return {
    restrict: 'A',
    priority: 1000,
    terminal: true,
    scope: true,
    compile: function(tElement, tAttrs) {
      if (tElement[0].tagName !== 'INPUT' || tAttrs.type !== 'checkbox') {
        throw 'checklist-model should be applied to `input[type="checkbox"]`.';
      }

      if (!tAttrs.checklistValue) {
        throw 'You should provide `checklist-value`.';
      }

      // exclude recursion
      tElement.removeAttr('checklist-model');

      // local scope var storing individual checkbox model
      tElement.attr('ng-model', 'checked');

      return postLinkFn;
    }
  };
}]);

(function(window, angular) {'use strict';
    var app = angular.module('advanced-search', ['fields']);

    app.controller('AdvancedSearchController', ['$rootScope', function($rootScope) {
        this.emptyKey = false;
        this.operator = 'AND';
        this.keyword = '';

        this.onFieldChange = function() {
            this.fieldType = $rootScope.fieldsCtrl.fieldsDef[this.field].type;
        };

        this.onEmptyChanged = function() {
            if (this.emptyKey) {
                this.operator = 'AND';
            }
        };

        this.addField = function() {
            var getExpression = function() {
                    var escapeKeyword = function(keyword) {
                            return keyword.replace(/:/g, '\\:');
                        },
                        prefix = this.field + ':',
                        keyword = this.keyword,
                        type, startDate, endDate;

                    if (this.emptyKey) {
                        return '-' + prefix + '[* TO *]';
                    }

                    type = $rootScope.fieldsCtrl.fieldsDef[this.field].type;
                    if (type === 'date') {
                        try {
                            startDate = new Date(this.startDate).toISOString();
                            endDate = new Date(this.endDate);
                            endDate.setDate(1);
                            endDate.setSeconds(-1);
                            endDate = endDate.toISOString();
                        } catch (e) {}
                        return prefix + '[' + escapeKeyword(startDate) + ' TO ' + escapeKeyword(endDate) + ']';
                    }

                    return prefix + '(' + escapeKeyword(keyword) + ')';
                },
                operatorStr = '',
                expr;

            if (this.field && (this.emptyKey || this.keyword || (this.startDate && this.endDate))) {
                expr = getExpression.apply(this);

                if ($rootScope.query && $rootScope.query.trim() !== '') {
                    operatorStr = ' ' + (this.operator) + ' ';
                }

                $rootScope.query += operatorStr + expr;

                this.keyword = '';
            }
        };
    }]);

    app.directive('advancedSearch', function() {
        return {
            restrict: 'E',
            templateUrl: 'templates/advanced-search.html',
            controller: 'AdvancedSearchController',
            controllerAs: 'advSrchCtrl'
        };
    });

    /* Trim Poyfill:
     * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/Trim
     */
    if (!String.prototype.trim) {
        (function() {
            // Make sure we trim BOM and NBSP
            var rtrim = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g;
            String.prototype.trim = function() {
                return this.replace(rtrim, '');
            };
        })();
    }

})(window, angular);

(function(window, angular, wb) {'use strict';
    var app = angular.module('dataset-types', ['checklist-model', 'services.config']);

    app.controller('DatasetTypesController', ['$http', '$rootScope', 'configuration', function($http, $rootScope, configuration) {
        var typesRequest = configuration.solrCore + '/select?fq=site_id:' + configuration.siteID + '&q=*:*&rows=0&wt=json&facet=true&facet.field=dataset_type',
            _this = this,
            httpMethod = $http.get;

        function fromDefault(types) {
            var notSelected = [
                'codeset',
                'geodescriptor',
                'subject',
                'survey'
            ];

            return types.filter(function(type) {
                if (notSelected.indexOf(type) === -1) {
                    return true;
                }

                return false;
            });
        }

        function fromURL() {
            var datasetTypes = wb.pageUrlParts.params.fq,
                orgs = [];

            if (datasetTypes) {
                decodeURI(datasetTypes).split(',').forEach(function(o) {
                    if (_this.datasetTypes.indexOf(o) !== -1) {
                        orgs.push(o);
                    }
                });

                if (orgs.length > 0) {
                    return orgs;
                }
            }

            return null;
        }

        function querySuccess(data) {
            var types = data.data.facet_counts.facet_fields.dataset_type.filter(function(value) {
                if (typeof value == 'string') {
                    return true;
                }

                return false;
            });

            _this.datasetTypes = types;
            _this.selectedDatasetTypes = fromURL() || fromDefault(types);
            _this.changed();
        }

        this.changed = function() {
            $rootScope.$emit('datasetType.selected', this.selectedDatasetTypes);
        };

        if (configuration.solrCore.indexOf(configuration.ckanInstance) === -1) {
            typesRequest += '&json.wrf=JSON_CALLBACK';
            httpMethod = $http.jsonp;
        }

        httpMethod(typesRequest)
                .then(querySuccess);
    }]);

    app.directive('datasetTypes', function() {
        return {
            restrict: 'E',
            templateUrl: 'templates/dataset-types.html',
            controller: 'DatasetTypesController',
            controllerAs: 'dataTypeCtrl'
        };
    });
})(window, angular, wb);

(function(window, angular, wb) {'use strict';
    var app = angular.module('display-fields', ['fields']);

    app.controller('DisplayFieldsController', ['$rootScope', '$scope', function($rootScope, $scope) {
        var _this = this;

        function fromUrl() {
            var displayFields = wb.pageUrlParts.params.fl,
                fields;

            if (displayFields) {

                fields = [].concat(_this.mandatoryFields);
                decodeURI(displayFields).split(',').forEach(function(field) {
                    if (fields.indexOf(field) === -1) {
                        fields.push(field);
                    }
                });

                // Remove fields that are not recognized;
                /*$rootScope.$on('datasetType.selected', function(event) {
                    var fields = $('#displayfield').scope().fieldsCtrl.fields,
                        fieldsIndex;

                    _this.fields = _this.fields.filter(function(f) {
                        if (fields.indexOf(f) === -1) {
                            return false;
                        }

                        return true;
                    });

                    $rootScope.$apply();
                });*/

                return fields;
            }

            return null;
        }

        this.field = '';
        this.mandatoryFields = [
            'name'
        ];

        this.fields = fromUrl() || [
            'name',
            'content_type_codes',
            'subject_codes',
            'title_en',
            'admin_notes_en'
        ];

        this.getVisible = function() {
            return this.fields.length !== 0;
        };

        this.getMandatory = function(field) {
            return this.mandatoryFields.indexOf(field) !== -1;
        };

        this.addField = function() {
            if (this.field && this.fields.indexOf(this.field) === -1) {
                this.fields.push(this.field);
                this.field = '';
            }
        };

        this.removeField = function(field) {
            this.fields.splice(this.fields.indexOf(field), 1);
        };
    }]);

    app.directive('displayFields', function() {
        return {
            restrict: 'E',
            templateUrl: 'templates/display-fields.html',
            controller: 'DisplayFieldsController',
            controllerAs: 'dspFieldCtrl'
        };
    });

})(window, angular, wb);

(function(window, angular) {'use strict';
    var app = angular.module('fields', ['services.config']);

    app.controller('FieldsController', ['$http', '$q', '$rootScope', 'configuration', function($http, $q, $rootScope, configuration) {
        var _this = this;

        $rootScope.fieldsCtrl = this;

        this.datasetTypesFields = {};
        this.fields = [];

        $rootScope.$on('datasetType.selected', function(event, selectedDatasetType) {
            var fieldsRequest = configuration.ckanInstance + '/api/3/action/scheming_dataset_schema_show?callback=JSON_CALLBACK&type=',
                fieldsCallback = function(response) {
                    var result = response.data.result,
                        type = result.dataset_type,
                        fields = result.dataset_fields,
                        fieldsLength = fields.length,
                        fieldsResults = {},
                        languages = result.form_languages || [],
                        languagesLength = languages.length,
                        f, field, l, fieldObj;

                    for (f = 0; f < fieldsLength; f += 1) {
                        field = fields[f];
                        fieldObj = {type: field.schema_field_type};

                        if (field.schema_field_type === 'fluent' || (field.preset && field.preset.indexOf('fluent') !== -1)) {
                            for (l = 0; l < languagesLength; l += 1) {
                                fieldsResults[field.field_name + '_' + languages[l]] = fieldObj;
                            }
                        } else {
                            fieldsResults[field.field_name] = fieldObj;

                            if (field.lookup) {
                                for (l = 0; l < languagesLength; l += 1) {
                                    fieldsResults[field.field_name + '_desc_' + languages[l]] = fieldObj;
                                }
                            }
                        }
                    }

                    _this.datasetTypesFields[type] = fieldsResults;
                    addFields(type);
                },
                fieldErrorCallback = function(response) {
                    var type = response.config.url.match(/type=([^&]*)/)[1],
                        types = $rootScope.dataTypeCtrl.datasetTypes,
                        typeIndex = types.indexOf(type),
                        selectedTypeIndex = selectedDatasetType.indexOf(type);

                    if (selectedTypeIndex !== -1) {
                        selectedDatasetType.splice(selectedTypeIndex, 1);
                    }

                    if (typeIndex !== -1) {
                        types.splice(typeIndex, 1);
                    }
                },
                addFields = function(type) {
                    $.extend(newFields, _this.datasetTypesFields[type]);
                },
                promises = [],
                newFields = {},
                o, type, p;

            for (o = 0; o < selectedDatasetType.length; o += 1) {
                type = selectedDatasetType[o];

                if (!_this.datasetTypesFields[type]) {
                    p = $http.jsonp(fieldsRequest + type, {cache: true})
                        .then(fieldsCallback, fieldErrorCallback);
                    promises.push(p);
                } else {
                    addFields(type);
                }
            }

            $q.all(promises)
                .then(function() {
                    _this.fields = Object.keys(newFields).sort();
                    _this.fieldsDef = newFields;
                });
        });
    }]);
})(window, angular);
