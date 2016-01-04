(function( $, wb ) {
"use strict";

var $document = wb.doc,
	authorSelector = "#field-internal_authors",
	authorInput = $( authorSelector ),
	root = $('body').data('siteRoot'),
	settings = window[ 'wb-multilist' ],
	timer;

$document.on( "keydown", authorSelector, function( event ) {
	var $this = $( this ),
	    which = event.which;

	if ( which === 32 || which === 8 || ( which > 47 && which < 91 ) ||
        ( which > 95 && which < 112 ) || ( which > 159 && which < 177 ) ||
        ( which > 187 && which < 223 ) ) {
        if ( !event.altKey ) {

            if ( timer ) {
                clearTimeout( timer );
            }

            timer = setTimeout( function() {
                var author = settings.parseRegexp.exec( event.target.value )[ 2 ].toLowerCase()

                if ( author !== "" ) {
                    $this.trigger({
                        type: "ajax-fetch.wb",
                        fetch: {
                            url: encodeURI( root + "api/3/action/GetInternalAuthors?q=" +  author ),
                            dataType: "json"
                        }
                    });
                }
            }, 500 );
        }
    }
});

$document.on( "ajax-fetched.wb", authorSelector, function( event ) {
	var dataList = $( "#" + authorInput.attr( "data-multilist" ) ),
		authors = event.fetch.response.result,
		lenAuthors = authors.length,
		options = "",
		indAuthors, author, name;

	dataList.empty();

	for ( indAuthors = 0; indAuthors !== lenAuthors; indAuthors += 1 ) {
		author = authors[ indAuthors ];
		name = author.last_name + ", " + author.first_name;

		options += "<option label=\"" + name + "\" value=\"" + name + "\"></option>";
	}

	if ( wb.ielt10 ) {
		options = "<select>" + options + "</select>";
	}

	dataList.append( options );

	authorInput.trigger( "wb-update.wb-multilist" );
});

})( jQuery, wb );