import logging

from playwright.sync_api import sync_playwright, Page


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
        playwright_page.wait_for_load_state("networkidle")

        names = set()
        for page_index in range(10):
            logger.info(
                f"{self.__class__.__name__} - scraping page {page_index + 1} - names found till now {names}"
            )
            names.update(
                self._get_names_from_current_page(playwright_page=playwright_page)
            )

            next_button = playwright_page.locator(self.GO_TO_NEXT_PAGE_XPATH).first
            if next_button.is_disabled():
                break

            next_button.click()
            playwright_page.wait_for_load_state("domcontentloaded")
            playwright_page.wait_for_load_state("networkidle")

        return names

    def _get_names_from_current_page(self, playwright_page: Page):
        table_rows_of_lobbyists = playwright_page.locator(self.LOBBYIST_TR_XPATH).all()

        lobbyists_names = []

        for table_row in table_rows_of_lobbyists:
            name = table_row.locator("xpath=/td").first.text_content().strip()
            lobbyists_names.append(name)

        return lobbyists_names


def get_lobbyists_from_etl():
    raw_data = LobbyistNamesExtractor().extract()
    return raw_data
