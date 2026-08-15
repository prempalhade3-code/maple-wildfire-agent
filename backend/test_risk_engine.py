from risk_engine import calculate_risk_metrics


def test_severe_conditions_cross_the_protective_threshold():
    metrics = calculate_risk_metrics(
        {"wind_speed": 38.0, "humidity": 18.0},
        {"soil_moisture": 9.5, "canopy_density": 32.0, "slope": 4.07, "distance": 80.0, "building_count": 2},
    )

    assert metrics["risk_score"] >= 70.0


def test_normal_conditions_remain_below_the_protective_threshold():
    metrics = calculate_risk_metrics(
        {"wind_speed": 10.0, "humidity": 60.0},
        {"soil_moisture": 22.0, "canopy_density": 1.0, "slope": 0.5, "distance": 15.0, "building_count": 45},
    )

    assert metrics["risk_score"] < 70.0
