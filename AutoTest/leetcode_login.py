import logging
import json
import undetected_chromedriver as uc

class AutoLeetCode:
    def __init__(self, headless=False, verbose=False):
        """
        Initializes the AutoLeetCode instance.

        Args:
            headless (bool): Whether to run Chrome in headless mode.
            verbose (bool): Whether to enable verbose logging.
        """
        self.headless = headless

        if verbose:
            logging.getLogger().setLevel(logging.INFO)
            logging.info("Verbose mode active")

        # Set Chrome options
        options = uc.ChromeOptions()
        options.headless = self.headless

        logging.info("Loading undetected Chrome")
        self.browser = uc.Chrome(
            options=options,
            headless=headless,
            log_level=10,
        )
        self.browser.set_page_load_timeout(15)

        logging.info("Loaded undetected Chrome")

    def save_cookies_and_csrf(self, output_path: str):
        """
        Save cookies and CSRF token to the specified JSON file.

        Args:
            output_path (str): Path to save the cookies and CSRF token in JSON format.
        """
        cookies = self.browser.get_cookies()
        cookies_dict = {}
        csrf_token = ""
        cookies_list = []

        # Extract cookies and CSRF token
        for cookie in cookies:
            cookies_list.append(f"{cookie['name']}={cookie['value']}")
            if cookie['name'] == 'csrftoken':
                csrf_token = cookie['value']

        # Create output JSON structure
        cookies_str = "; ".join(cookies_list)
        output_data = {
            "cookies": cookies_str,
            "csrf_token": csrf_token
        }

        # Save to JSON file
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(output_data, output_file, indent=4)
        
        logging.info(f"Cookies and CSRF token saved to {output_path}")

    def login_and_save(self, output_path: str):
        """
        Logs into LeetCode and saves cookies and CSRF token.

        Args:
            output_path (str): Path to save the cookies and CSRF token in JSON format.
        """
        login_url = "https://leetcode.com/accounts/login/"
        self.browser.get(login_url)

        # Wait for user to manually log in
        input("Please log in manually and press Enter here once done...")

        # Save cookies and CSRF token after login
        self.save_cookies_and_csrf(output_path)

    def quit(self):
        """
        Closes the browser.
        """
        logging.info("Closing browser.")
        self.browser.quit()


if __name__ == "__main__":
    # Initialize the script and log in manually
    output_file_path = "leetcode_cookies_csrftoken.json"
    autoleet = AutoLeetCode(headless=False, verbose=True)
    autoleet.login_and_save(output_file_path)
    autoleet.quit()
