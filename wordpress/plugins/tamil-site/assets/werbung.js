/**
 * Werbebuchung: zählt eine Einblendung, wenn mindestens die halbe Fläche einer gebuchten Anzeige eine Sekunde am Stück
 * sichtbar war (einmal je Seitenaufruf und Anzeige). Ohne Cookies und ohne Kennungen: gesendet wird nur die Buchung.
 */
( function () {
	'use strict';
	var flaechen = document.querySelectorAll( '[data-wb-buchung][data-wb-zaehlen]' );
	if ( ! flaechen.length || ! ( 'IntersectionObserver' in window ) ) {
		return;
	}
	function senden( el ) {
		var daten = new URLSearchParams();
		daten.set( 'buchung', el.getAttribute( 'data-wb-buchung' ) );
		var ziel = el.getAttribute( 'data-wb-zaehlen' );
		if ( navigator.sendBeacon ) {
			navigator.sendBeacon( ziel, daten );
		} else {
			fetch( ziel, { method: 'POST', body: daten, credentials: 'omit', keepalive: true } );
		}
	}
	var uhren = new WeakMap();
	var beobachter = new IntersectionObserver( function ( eintraege ) {
		eintraege.forEach( function ( e ) {
			var el = e.target;
			if ( e.intersectionRatio >= 0.5 ) {
				if ( ! uhren.get( el ) ) {
					uhren.set( el, window.setTimeout( function () {
						beobachter.unobserve( el );
						senden( el );
					}, 1000 ) );
				}
			} else if ( uhren.get( el ) ) {
				window.clearTimeout( uhren.get( el ) );
				uhren.delete( el );
			}
		} );
	}, { threshold: [ 0, 0.5 ] } );
	flaechen.forEach( function ( el ) {
		beobachter.observe( el );
	} );
}() );
