window.onload = function() {
	$$('sup.footnote a').each(function(i) {
		i.onclick = function() {
			field = this.href.split("#")[1];
			new Effect.Highlight(field, {duration: 2});
		};
	});
}