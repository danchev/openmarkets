"""Service-layer tests for ScreenerService."""

from unittest import mock

from openmarkets.services.screener import ScreenerService


def _service_with_spy() -> tuple[ScreenerService, mock.Mock]:
    repository = mock.Mock()
    return ScreenerService(repository=repository), repository


def test_screen_forwards_query_count_offset_and_session():
    service, repository = _service_with_spy()

    service.search_screener_matches("day_gainers", count=10, offset=5)

    repository.screen.assert_called_once_with("day_gainers", count=10, offset=5, session=service.session)


def test_screen_defaults_count_and_offset():
    service, repository = _service_with_spy()

    service.search_screener_matches("most_actives")

    repository.screen.assert_called_once_with("most_actives", count=25, offset=0, session=service.session)


def test_screen_returns_repository_result():
    service, repository = _service_with_spy()
    repository.screen.return_value = "sentinel-result"

    assert service.search_screener_matches("day_gainers") == "sentinel-result"
