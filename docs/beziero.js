'use strict';
/* couldn't bother with other libs under contagious mit license so I wrote my own
 * Henrique Maziero 2021
 */
L.Bezier = L.Polyline.extend({
    options: { smoothFactor: 0, noClip: true },
    _updatePath: function () {
        if (this._parts && this._parts[0] && this._parts[0].length >= 3) {
            let p = this._parts[0];
            let str = (p.length == 3) ? "M" + p[0].x + " " + p[0].y + " Q" + p[1].x + "," + p[1].y + " " + p[2].x + "," + p[2].y + "" : "M" + p[0].x + " " + p[0].y + " C" + p[1].x + "," + p[1].y + " " + p[2].x + "," + p[2].y + " " + p[3].x + "," + p[3].y + ""
            this._renderer._setPath(this, str);
        } else { this._renderer._setPath(this, "M0 0"); }
    }

}); // and that's it, a bezier lib in 10 lines, suckers
// now another 30 lines because no points-to-layer for poly/lines
L.BezierGeoJSON = L.GeoJSON.extend({
    addData: function (geojson) {
        // considerable copypaste from the method im trying to extend/modify
        var features = L.Util.isArray(geojson) ? geojson : geojson.features,
            i, len, feature;

        // recursibe
        if (features) {
            for (i = 0, len = features.length; i < len; i++) {
                // only add this if geometry or geometries are set and not null
                feature = features[i];
                if (feature.geometries || feature.geometry || feature.features || feature.coordinates) {
                    this.addData(feature);
                }
            }
            return this;
        }
        var options = this.options,
            geometry = geojson.type === 'Feature' ? geojson.geometry : geojson,
            coords = geometry ? geometry.coordinates : null,
            _coordsToLatLng = options && options.coordsToLatLng || L.GeoJSON.coordsToLatLng,
            latlngs = L.GeoJSON.coordsToLatLngs(coords, geometry.type === 'LineString' ? 0 : 1, _coordsToLatLng),
            layer = new L.Bezier(latlngs, options); // Here
        layer.feature = L.GeoJSON.asFeature(geojson);
        layer.defaultOptions = layer.options;
        this.resetStyle(layer);
        if (options.onEachFeature) {
            options.onEachFeature(geojson, layer);
        }
        return this.addLayer(layer);
    }
});