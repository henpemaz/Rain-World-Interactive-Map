
L.Icon.Chip = L.DivIcon.extend({
	options: {
		iconSize: [12, 8],
		iconAnchor: [6, 4],

		// 🍂option border: String
		// A CSS definition of a border, see https://developer.mozilla.org/docs/Web/CSS/border
		border: '#888 solid 1px',

		// 🍂option border: String
		// A CSS definition of a color, see https://developer.mozilla.org/en-US/docs/Web/CSS/color_value
		color: 'blue'
	},

	createIcon: function (oldIcon) {
		var div = (oldIcon && oldIcon.tagName === 'DIV') ? oldIcon : document.createElement('div'),
		    options = this.options;

		div.innerHTML = '';

		div.style.border = this.options.border;
		div.style.borderRadius = '50%';
		div.style.background = this.options.color;

		this._setIconStyles(div, 'icon');

		return div;
	},

	createShadow: function () {
		return null;
	}

});



L.icon.chip = function(options) {
	return new L.Icon.Chip(options);
};
