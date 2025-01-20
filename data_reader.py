import geopandas as gpd
import numpy as np
from numpy.typing import NDArray
from shapely.geometry.polygon import Polygon
import shapely
from functools import partial
from typing import List, Optional


def poly2lines(poly: Polygon, xy: Optional[List[float]] = None):
    coords = shapely.get_coordinates(poly, include_z=True)
    if xy is not None:
        xy[0], xy[1] = max(xy[0], coords[:, 0].max()), min(xy[1], coords[:, 0].min())
        xy[2], xy[3] = max(xy[2], coords[:, 1].max()), min(xy[3], coords[:, 1].min())
    return np.hstack((coords[:-1], coords[1:]))

def read_shp(path: str):
    city: gpd.GeoDataFrame = gpd.read_file(path)
    xy = [-np.inf, np.inf, -np.inf, np.inf]
    func = partial(poly2lines, xy=xy)
    lines: NDArray[np.float64] = np.concatenate(tuple(func(i) for i in city["geometry"]))
    return lines, dict(zip(("x_max", "x_min", "y_max", "y_min"), xy))


if __name__ == "__main__":
    lines, xy = read_shp("./local/Shanghai/Shanghai_Buildings_DWG-Polygon.shp")
    print(lines, xy)