(function( $, wb ) {
"use strict";

var $document = wb.doc,
	authorSelector = "#field-internal_authors",
	authorInput = $( authorSelector ),
	root = $('body').data('siteRoot'),
	sql = "SELECT \"last name\" || ', ' || \"first name\" AS Name FROM \"c870d6fc-132c-46ed-aa82-4db2ebee310c\" WHERE lower(\"full name\") LIKE lower('%{keyword}%') LIMIT 25",
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
                            url: encodeURI( root + "api/3/action/datastore_search_sql?sql=" +  sql.replace('{keyword}', author)),
                            dataType: "json"
                        }
                    });
                }
            }, 10 );
        }
    }
});

$document.on( "ajax-fetched.wb", authorSelector, function( event ) {
	var dataList = $( "#" + authorInput.attr( "data-multilist" ) ),
		names = event.fetch.response.result.records,
		lenNames = names.length,
		options = "",
		indName, name;

	dataList.empty();

	for ( indName = 0; indName !== lenNames; indName += 1 ) {
		name = names[ indName ];

		options += "<option label=\"" + name.name + "\" value=\"" + name.name + "\"></option>";
	}

	if ( wb.ielt10 ) {
		options = "<select>" + options + "</select>";
	}

	dataList.append( options );

	authorInput.trigger( "wb-update.wb-multilist" );
});

})( jQuery, wb );