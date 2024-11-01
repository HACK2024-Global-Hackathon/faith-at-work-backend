import pytest
from utils.geo_utils import get_walking_estimate_haversine


@pytest.fixture
def marina_bay_sands():
    return (1.2834, 103.8607)

@pytest.fixture
def raffles_place():
    return (1.2837, 103.8501)


def test_get_walking_estimate_haversine_precision(marina_bay_sands, raffles_place):
    result = get_walking_estimate_haversine(0, 0, 0, 0)
    assert result["distance_m"] == 0
    assert result["walking_time_mins"] == 0

    result = get_walking_estimate_haversine(marina_bay_sands[0], marina_bay_sands[1], raffles_place[0], raffles_place[1])

    assert result["distance_m"] == pytest.approx(1178.84, rel=1e-2)
    assert result["walking_time_mins"] == pytest.approx(24.55, rel=1e-2)


@pytest.fixture(params=[
    ((1.2834, 103.8607), (1.2837, 103.8501)), # Marina Bay Sands to Raffles Place
    ((1.2952, 103.8550), (1.2905, 103.8519)), # Suntec City to Millenia Walk
    ((1.3050, 103.8310), (1.3070, 103.8470)), # Changi Airport to Jewel Changi
])
def location_pair(request):
    return request.param

def test_get_walking_estimate_haversine(location_pair):
    latA, longA = location_pair[0]
    latB, longB = location_pair[1]

    result = get_walking_estimate_haversine(latA, longA, latB, longB)

    assert result["distance_m"] > 0
    assert result["walking_time_mins"] > 0


@pytest.fixture(params=[
    ((0, 0), (0, 0)),
    ((1.2952, 103.8550), (1.2952, 103.8550)),
    ((1.3050, 103.8310), (1.3050, 103.8310)),
])
def same_location_pair(request):
    return request.param


def test_get_walking_estimate_haversine_same_location(same_location_pair):
    latA, longA = same_location_pair[0]
    latB, longB = same_location_pair[1]

    result = get_walking_estimate_haversine(latA, longA, latB, longB)

    assert result["distance_m"] == 0
    assert result["walking_time_mins"] == 0
