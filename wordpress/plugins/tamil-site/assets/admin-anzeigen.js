/**
 * Einstellungen → Tamil.de Website: Bild einer Eigenanzeige aus der Mediathek wählen. Schreibt die Mediathek-ID in das
 * Zahlenfeld daneben; „Standardbild“ leert es. Ohne Skript bleibt das Zahlenfeld.
 */
( function () {
	'use strict';
	if ( ! window.wp || ! window.wp.media ) {
		return;
	}
	var texte = window.tamilSiteBild || {};
	document.querySelectorAll( '.tamil-bild-waehlen, .tamil-bild-standard' ).forEach( function ( knopf ) {
		knopf.hidden = false;
	} );
	document.addEventListener( 'click', function ( ereignis ) {
		var knopf = ereignis.target.closest( '.tamil-bild-waehlen, .tamil-bild-standard' );
		if ( ! knopf ) {
			return;
		}
		ereignis.preventDefault();
		var feld = document.getElementById( knopf.getAttribute( 'data-feld' ) );
		if ( ! feld ) {
			return;
		}
		if ( knopf.classList.contains( 'tamil-bild-standard' ) ) {
			feld.value = '';
			return;
		}
		var rahmen = window.wp.media( {
			title: texte.titel || '',
			button: { text: texte.knopf || '' },
			library: { type: 'image' },
			multiple: false
		} );
		rahmen.on( 'select', function () {
			var bild = rahmen.state().get( 'selection' ).first();
			if ( bild ) {
				feld.value = String( bild.get( 'id' ) );
			}
		} );
		rahmen.open();
	} );
}() );
