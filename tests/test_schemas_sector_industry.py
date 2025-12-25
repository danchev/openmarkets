from openmarkets.schemas.sector_industry import IndustryResearchReportEntry


def test_validate_target_price_with_none():
    data = {
        "id": "r1",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": None,
    }

    r = IndustryResearchReportEntry(**data)
    assert r.target_price is None


def test_validate_target_price_with_float_string():
    data = {
        "id": "r2",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": "12.34",
    }

    r = IndustryResearchReportEntry(**data)
    assert isinstance(r.target_price, float)
    assert r.target_price == 12.34


def test_validate_target_price_with_non_numeric_returns_none():
    data = {
        "id": "r3",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": "N/A",
    }

    r = IndustryResearchReportEntry(**data)
    assert r.target_price is None


def test_validate_target_price_with_float_value():
    data = {
        "id": "r4",
        "headHtml": "head",
        "provider": "p",
        "reportTitle": "t",
        "reportType": "type",
        "targetPrice": 7,
    }

    r = IndustryResearchReportEntry(**data)
    assert isinstance(r.target_price, float)
    assert r.target_price == 7.0
