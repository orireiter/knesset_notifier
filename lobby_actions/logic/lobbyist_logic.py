import logging
from time import sleep

from lxml.html import fromstring
from playwright.sync_api import sync_playwright, Page, Response, Locator, expect


logger = logging.getLogger(__name__)


class LobbyistNamesExtractor:
    URL_WITH_LOBBYISTS_NAME_TO_SCRAPE = (
        "https://main.knesset.gov.il/About/Lobbyist/Pages/Lobbyist.aspx"
    )
    LOBBYIST_TR_XPATH = '//tr[contains(@id, "Result")]'
    GO_TO_NEXT_PAGE_XPATH = '//a[contains(@id, "Next")]'

    def extract(self):
        logger.info(
            f"{self.__class__.__name__} - starting to extract lobbyist names from {self.URL_WITH_LOBBYISTS_NAME_TO_SCRAPE}"
        )
        with sync_playwright() as playwright_object:
            playwright_browser = playwright_object.firefox.launch()
            page = playwright_browser.new_page()

            lobbyist_names = self._scrape_all_lobbyists_names(playwright_page=page)
            return lobbyist_names

    def _scrape_all_lobbyists_names(self, playwright_page: Page):
        playwright_page.goto(
            url=self.URL_WITH_LOBBYISTS_NAME_TO_SCRAPE, wait_until="domcontentloaded"
        )

        names = set()
        for page_index in range(10):
            self._wait_for_page_to_be_fully_loaded(playwright_page=playwright_page)
            logger.info(
                f"{self.__class__.__name__} - page loaded - {page_index=} - names till now {names}"
            )

            names.update(
                self._get_names_from_current_page(playwright_page=playwright_page)
            )

            sleep(0.5)
            next_button = playwright_page.locator(self.GO_TO_NEXT_PAGE_XPATH).first
            if not self._is_more_pages(next_button=next_button):
                break

            next_button.click()

        return names

    def _get_names_from_current_page(self, playwright_page: Page):
        table_rows_of_lobbyists = playwright_page.locator(self.LOBBYIST_TR_XPATH).all()

        lobbyists_names = []

        for table_row in table_rows_of_lobbyists:
            name = table_row.locator("xpath=/td").first.text_content().strip()
            lobbyists_names.append(name)

        return lobbyists_names

    def _wait_for_page_to_be_fully_loaded(self, playwright_page: Page):
        with playwright_page.expect_response(self._is_page_data_loaded):
            expect(
                playwright_page.locator(self.LOBBYIST_TR_XPATH).first
            ).not_to_be_empty()

    def _is_page_data_loaded(self, res: Response):
        if res.url != "https://main.knesset.gov.il/About/Lobbyist/Pages/Lobbyist.aspx":
            return False

        as_lxml = fromstring(res.text())
        lobbyists_rows = as_lxml.xpath(self.LOBBYIST_TR_XPATH)
        if lobbyists_rows:
            return True

        return False

    @staticmethod
    def _is_more_pages(next_button: Locator):
        if (
            next_button.is_disabled()
            or "disabled" in (next_button.get_attribute("class") or "").lower()
        ):
            return False

        return True


def get_lobbyists_from_etl():
    raw_data = LobbyistNamesExtractor().extract()
    return raw_data
