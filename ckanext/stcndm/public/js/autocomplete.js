(function(window, $, wb) {
    'use strict';

    var timeout,
        root = $('body').data('siteRoot'),
        getAutocomplete = function(event) {
            var val = event.target.value,
                data;

            if (val) {
                data = $.extend({q: '*' + val + '*'}, wb.getData(event.delegateTarget, 'autocomplete'));

                wb.doc.trigger({
                    type: 'ajax-fetch.wb',
                    element: event.delegateTarget,
                    fetch: {
                        url: root + 'api/3/action/GetAutocomplete',
                        data: data,
                        dataType: 'jsonp',
                        jsonp: 'callback'
                    }
                });
            }
        },
        addItem = function(event) {
            var $codes = $(event.delegateTarget).find('input[name!=""][name], textarea'),
                codes = $codes.val(),
                code = $(event.delegateTarget).find('select option:selected').val();

            if (!codes) {
                $codes.val(code);
            } else if (codes.split(';').indexOf(code) === -1) {
                $codes.val(codes + ';' + code);
            }
        };

    $('[data-autocomplete]').on('keydown', 'input[type="text"]:first', function() {
        var _this = this,
            args = arguments;

        clearTimeout(timeout);
        timeout = setTimeout(function() {
            getAutocomplete.apply(_this, args);
        }, 500);
    });

    $('[data-autocomplete]').on('ajax-fetched.wb', function(event) {
        var $select = $(event.delegateTarget).find('select'),
            terms = event.fetch.response.result.results,
            termsLength = terms.length,
            t, term, group, $append;

        $select.empty();

        if (terms.length !== 0) {
            for (t = 0; t < termsLength; t += 1) {
                term = terms[t];
                group = term.group;

                if (group) {
                    group = group[wb.lang];
                    $append = $select.find('optgroup[label="' + group + '"]');

                    if ($append.length === 0) {
                        $append = $('<optgroup label="' + group + '"></optgroup>').appendTo($select);
                    }
                } else {
                    $append = $select;
                }

                $append.append('<option value="' + term.code + '">' + term.title.en + ' | ' + term.title.fr + ' | ' + term.code);
            }
        } else {
            $select.append('<option value="">' + wb.i18n('no-match') + '</option>');
        }
    });

    $('[data-autocomplete]').on('click', 'button', function(event) {
        addItem.apply(this, arguments);
    });

    $('[data-autocomplete]').on('keydown', 'select', function(event) {
        if (event.which === 13) {
            addItem.apply(this, arguments);
        }
    });



})(window, jQuery, wb);
