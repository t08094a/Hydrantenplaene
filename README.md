# Hydrant maps
Hydrantenpläne für Ipsheim, basierend auf http://printmaps-osm.de/
Hydrant maps for village [Ipsheim en](https://en.wikipedia.org/wiki/Ipsheim) or [Ipsheim de](https://de.wikipedia.org/wiki/Ipsheim).

# Based on OpenStreetMap
All fire hydrants are implemented as features in [OpenStreetMap](https://www.openstreetmap.org/). A rendered map can be seen at [Hydrants Ipsheim](http://www.openfiremap.de/?zoom=16&lat=49.52867&lon=10.48735&layers=B00000).

# Printmaps
The maps are rendered With help of [printmaps-osm](http://printmaps-osm.de/de/index.html).
The CLI client is stored as Linux amd64 binary in `./bin`. For other operating systems you can find binaries at [CLI-Clients](http://printmaps-osm.de/de/client.html).

# Shared files
All shared files are referenced as symbolic links to each partial map.  
If the symlinks are broken, they could be restored by  

```bash
cd <partial map folder>

ls -d1 ../shared/* | while read f; do
  ln -sf "$(cat $f)" "$f"
done
```

# How to position scale bar
Get start position with help of [uMap](https://umap.openstreetmap.fr/de/map/new/). Create a marker at interested position with <kbd>Ctrl</kbd>+<kbd>M</kbd> and copy the values from coordinates.  
With theese coordinates we could create the relevant data:

```bash
Usage:
  printmaps bearingline  lat       lon      angle length  linelabel     filename

$ printmaps bearingline  51.98130  7.51479  90.0  1000.0  "1000 Meter"  scalebar-1000
```

