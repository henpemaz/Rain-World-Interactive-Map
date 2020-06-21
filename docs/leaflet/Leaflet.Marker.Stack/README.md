# `L.Marker.Stack` & `L.Icon.Chip`

A client-side implementation of @CartoDB's idea of a [stacked chips symbolizer](http://blog.cartodb.com/stacking-chips-a-map-hack/).

![Image of a few chip stacks with random data](http://ivansanchez.github.io/Leaflet.Marker.Stack/chips.png)

This is composed of two parts:
* `L.Marker.Stack` allows displaying several `L.Icon`s on a stack top of each other, at the same `L.LatLng`.
* `L.Icon.Chip` is a ellipse-shaped `L.Icon`.


## `L.Marker.Stack` reference

Behaves like a `L.Marker`, but has the following options:

* `icons`: Must be an `Array` of `L.Icon`s. The order of the icons in the array defines the stacking order. This deprecates the `icon` property.
* `stackOffset`: An instance of `L.Point`. Defines how many pixels each icon is offset from the previous one. The default is `[0, -5]`, which means each icon is offset 5 pixels vertically towards the top (it is possible to make downward-facing stacks).
* `stackZOffset`: An integer, affecting the [z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Positioning/Understanding_z_index) of the icons. Positive values display the last icon on top, negative values display the first icon on top. The default is a positive 1.



## `L.Icon.Chip` reference

Behaves like a `L.DivIcon`, but has the following extra options:

* `border`: A [CSS definition the `border` property](https://developer.mozilla.org/docs/Web/CSS/border). Defaults to `"#888 solid 1px"`.
* `color`: A [CSS color definition](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value). Defaults to `"blue"`.
* `iconSize`: Defaults to `[12, 8]`. Change it to make the ellipse bigger or smaller.
* `iconAnchor`: Defaults to `[6, 4]` (the center of the ellipse).


## Example

```js
var stack = L.marker.stack(myCenter, {
	icons: [
		L.icon.chip({ color: 'red' }),
		L.icon.chip({ color: 'red' }),
		L.icon.chip({ color: 'blue' }),
		L.icon.chip({ color: 'lime' }),
	],
	stackOffset: [0, -5]
});

map.addLayer(stack);
```

Check out the live demos:
- [simple](http://ivansanchez.github.io/Leaflet.Marker.Stack/demos/simple.html).
- [color ramps](http://ivansanchez.github.io/Leaflet.Marker.Stack/demos/color_ramps.html).



### Legalese

"THE BEER-WARE LICENSE":
<ivan@sanchezortega.es> wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.
