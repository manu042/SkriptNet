/*! Parser: dates - updated 8/22/2016 (v2.27.5) */
/* Extract dates using popular natural language date parsers */
/*jshint jquery:true */
/*global Sugar*/
;(function ($) {
	'use strict';

	/*! Sugar (https://sugarjs.com/docs/#/DateParsing) */
	/* demo: http://jsfiddle.net/Mottie/abkNM/4163/ */
	$.tablesorter.addParser({
		id: 'sugar',
		is: function () {
			return false;
		},
		format: function (s) {
			// Add support for sugar v2.0+
			var create = Date.create || Sugar.Date.create,
				date = create ? create(s) : s ? new Date(s) : s;
			return date instanceof Date && isFinite(date) ? date.getTime() : s;
		},
		type: 'numeric'
	});

	/*! Datejs (http://www.datejs.com/) */
	/* demo: http://jsfiddle.net/Mottie/abkNM/4164/ */
	$.tablesorter.addParser({
		id: 'datejs',
		is: function () {
			return false;
		},
		format: function (s) {
			var date = Date.parse ? Date.parse(s) : s ? new Date(s) : s;
			return date instanceof Date && isFinite(date) ? date.getTime() : s;
		},
		type: 'numeric'
	});

})(jQuery);
