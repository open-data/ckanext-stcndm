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
            var $list = $(event.delegateTarget).find('.list select :selected'),
                $result = $(event.delegateTarget).find('.result select'),
                $options,
                optionsLength,
                $return = $(event.delegateTarget).find('.return input'),
                all_options = [],
                o;
            if ($result.find('option[value="'+$list.val()+'"]').length == 0) {
                $result.append('<option value="'+$list.val()+'">'+$list.text()+'</option>');
                $options = $result.find("option");
                optionsLength = $options.length;

                for (o = 0; o < optionsLength; o += 1) {
                    all_options.push($options.get(o).value)
                }

                $return.val(all_options.join('; '));
            }
        },
        removeItem = function(event) {
            var $result = $(event.delegateTarget).find('.result select :selected'),
                $options = $result.find("option"),
                optionsLength,
                $return = $(event.delegateTarget).find('.return input'),
                all_options = [],
                o;
            $result.remove();
            $options = $('.result select option');
            optionsLength = $options.length;
            for (o = 0; o < optionsLength; o += 1) {
                all_options.push($options.get(o).value)
            }

            $return.val(all_options.join('; '));
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
        var $select = $(event.delegateTarget).find('.list select'),
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

                $append.append('<option value="' + term.code + '">' + term.code + ' | ' + term.title[wb.lang] + '</option>');
            }
        } else {
            $select.append('<option value="">' + wb.i18n('no-match') + '</option>');
        }
    });

    $('[data-autocomplete]').on('click', 'button', function(event) {
        if ($(event.target).hasClass('add')) {
            addItem.apply(this, arguments);
        }
        else if ($(event.target).hasClass('remove')) {
            removeItem.apply(this, arguments);
        }
    });

    $('[data-autocomplete]').on('keydown', 'select', function(event) {
        if (event.which === 13) {
            addItem.apply(this, arguments);
        }
    });

})(window, jQuery, wb);
