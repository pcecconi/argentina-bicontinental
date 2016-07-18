// Definicion del namespace
var smn = smn || {};

L.CRS['SR-ORG8233'] = new L.Proj.CRS('SR-ORG:8233',
	  '+proj=laea +lat_0=-40 +lon_0=-60 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs',
	  // [-4000000, -5400000, 4000000, 2600000],      
	  {
  		origin: [-4000000, 4000000],
		resolutions: [31250.0, 15625.0, 7812.5, 3906.25, 1953.125, 976.5625, 488.28125, 244.140625, 122.0703125, 61.03515625, 30.517578125, 15.2587890625]
	  }
	);

L.CRS['SR-ORG8639'] = new L.Proj.CRS('SR-ORG:8639',
	  '+proj=stere +lat_0=-90 +lon_0=-63 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
	  // [-10000000, -7000000, 10000000, 13000000],
	  {
        origin: [-10000000, 13000000],
		resolutions: [78125, 39062.5, 19531.25, 9765.625, 4882.8125, 2441.40625, 1220.703125, 610.3515625, 305.17578125, 152.587890625, 76.2939453125, 38.1469726562, 19.0734863281, 9.53674316406]
	  }
	);

smn.Map = (function() {
	var mapa = null, layers = [];

    function redimensionarMapa() {
        $('#mapa').css('width', $(window).width()).css('height', $(window).height()).css('margin', 0);        
        if (mapa) {
            mapa.invalidateSize();            
        }
    }

    function getQueryParameters(str) {
        str = str || document.location.search;
        return (!str && {}) || str.replace(/(^\?)/,'').split("&").map(function(n){return n = n.split("="),this[n[0]] = decodeURIComponent(n[1].replace(/\+/g, ' ')),this}.bind({}))[0];
    }    
    
    function stopPropagation(ev) {
        if (ev.stopPropagation) {
            ev.stopPropagation();
        } else {
            ev.cancelBubble = true;
        }            
    }

	return {
		init: function(divId, config) { 
            var mapDivId = $('.mapa')[0].id;

            // Elimino el "Cargando..."
            $('#'+mapDivId).empty();

            var params = getQueryParameters();

            if (smn.map && smn.map.config) {
                var c = smn.map.config,
                    ext = c.extent.split(' ').map(parseFloat);
                if (c.fullscreen && !(params.maximize=="false")) {
                    // El div del mapa tiene que ocupar toda la ventana
                    redimensionarMapa();

                    $(window).on('resize', function() {
                        redimensionarMapa();
                    });
                }
		        c.crs = c.crs.toUpperCase();
                var crs = L.CRS[c.crs.replace(':', '')];
                try {                    
                    leftBottom = proj4(c.crs).inverse(ext.slice(0,2));
                    rightTop = proj4(c.crs).inverse(ext.slice(2,4));
                    mapa = L.map(mapDivId, {
                        crs: crs,
                        continuousWorld: true,
                        worldCopyJump: false,
                        attributionControl: false,
                        minZoom: 2,
                        /*,
                        maxZoom: 10
                        */ 
                    }).fitBounds(
                        L.latLngBounds(
                            L.latLng(leftBottom[1], leftBottom[0]), 
                            L.latLng(rightTop[1], rightTop[0])
                        )
                    );
                    
                    var attribution = L.control.attribution({
                        prefix: ''
                    }).addTo(mapa);

                    var base_layer = L.tileLayer(c.baselayerurl, {
                        tms: c.tmsbaselayer,
                        attribution: c.attribution,
                        continuousWorld: true
                    }).addTo(mapa);

                    var ref_layer = L.tileLayer(c.baselayerurl, {
                        tms: true,
                        continuousWorld: false
                    });

                    L.control.scale({imperial: false}).addTo(mapa);
                    
                    // Esto es para evitar que los clicks sobre los elementos flotantes sobre el
                    // mapa sean capturados por el mapa y generen movimientos no previstos        
                    $('.leaflet-control')
                        .on('mousedown', stopPropagation)
                        .on('dblclick', stopPropagation);

                } catch(e) {
                    console.log('Se produjo un error al inicializar el mapa. Revise la configuración.', e);
                }

            } else {
                console.log('Missing configuration smn.map.config');
            }
		}
	};
})();
