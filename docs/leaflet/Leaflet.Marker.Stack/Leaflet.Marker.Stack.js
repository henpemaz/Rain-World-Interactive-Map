
L.Marker.Stack = L.Marker.extend({

	options: {
		// 🍂option icons: [Icon]
		// The array of icons that make up this stack
		icons: [],

		// 🍂option stackOffset: Point
		// The offset (in pixels) to be applied as icons are being stacked
		stackOffset: L.point(0, -5),

		// 🍂option stackZOffset: Point
		// The offset (in z-index units) to be applied as icons are being stacked
		// A positive value will put the last icon on top, and a negative value
		// will display the first icon on top.
		stackZOffset: 1
	},

	// This replaces the _initIcon from L.Marker, which previously
	// was adding just one icon to the marker.
	// this._icon becomes a container for all the stacked icons.
	_initIcon: function () {
		var options = this.options,
		    classToAdd = 'leaflet-zoom-' + (this._zoomAnimated ? 'animated' : 'hide');

		options.stackOffset = L.point(options.stackOffset);

		this._icon = L.DomUtil.create('div', classToAdd);

		var c = 0;
		for (var i in options.icons) {

			var chip = options.icons[i];

			var chipElement = chip.createIcon();

			L.DomUtil.setPosition(chipElement, options.stackOffset.multiplyBy(c));
			chipElement.style.zIndex = options.stackZOffset * c;

			c++;
			this._icon.appendChild(chipElement);
		}

		this.getPane().appendChild(this._icon);
	}

});



L.marker.stack = function(latlng, opts) {
	return new L.Marker.Stack(latlng, opts);
}
