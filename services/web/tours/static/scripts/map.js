async function displayTrack(map, gpxURL, full_track=false) {

    const request = new Request(gpxURL);
    const response = await fetch(request);
    const gpxString = await response.text();

    const gpx = new L.GPX(gpxString, {
        async: true,
        polyline_options: { color: 'blue' },
    })
    .on("loaded", (e) => {
        if (full_track) {
            map.fitBounds(e.target.getBounds());
        }
    })
    .addTo(map);
}
