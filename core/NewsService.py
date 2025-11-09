import requests
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class NewsService(QObject):
    """
    Handles fetching news from NewsAPI and managing the scrolling ticker.
    
    Emits a signal with the updated ticker string at a regular interval.
    """
    
    # Define signals
    news_ticker_updated = pyqtSignal(str)

    def __init__(self, config, parent=None):
        """
        Initializes the news service.
        
        Args:
            config (dict): The loaded configuration dictionary.
            parent (QObject): The parent object (optional).
        """
        super().__init__(parent)
        self.config = config
        self.debug = self.config.get("debug", False)
        
        # --- Internal State ---
        self.news_string = "Loading news..."
        self.news_padding = " " * 10
        
        # --- Internal Timers ---
        # 1. For fetching new articles from the API
        self.news_fetch_timer = QTimer(self)
        self.news_fetch_timer.timeout.connect(self.update_news)
        # 1800000 ms = 30 minutes
        self.fetch_interval = self.config['display'].get('news_fetch_ms', 1800000)
        
        # 2. For scrolling the text on the screen
        self.news_scroll_timer = QTimer(self)
        self.news_scroll_timer.timeout.connect(self.scroll_news_ticker)
        # 200 ms = 5 times per second
        self.scroll_interval = self.config['display'].get('news_scroll_ms', 200)

    def start(self):
        """Starts the news service timers."""
        print("NewsService started. Fetching initial headlines...")
        self.update_news() # Fetch immediately on start
        self.news_fetch_timer.start(self.fetch_interval)
        self.news_scroll_timer.start(self.scroll_interval)

    def update_news(self):
        """
        Fetches the top headlines from the NewsAPI.
        """
        try:
            # Get settings from config
            api_key = self.config['api_keys']['newsapi']
            country = self.config['display']['news_country']
            
            url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"
            
            if self.debug:
                print(f"NewsService: Fetching news from {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status() # Check for HTTP errors
            
            data = response.json()
            articles = data.get('articles', [])
            
            # 1. Get titles, but only if they are not None
            titles = [article.get('title') for article in articles]
            # 2. Filter out any None or empty strings
            valid_titles = [title for title in titles if title]
            
            if not valid_titles:
                self.news_string = "No news headlines found."
                return

            # Create one long string, separated by bullets
            separator = f"{self.news_padding} • {self.news_padding}"
            single_string = separator.join(valid_titles)
            
            # Create an "endless" loop by joining the string to itself
            self.news_string = f"{single_string}{separator}"

        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            self.news_string = "Error fetching news."
        except Exception as e:
            print(f"Error processing news: {e}")
            self.news_string = "Error processing news."

    def scroll_news_ticker(self):
        """
CHMOD
        Performs one "scroll" step on the news string and emits the result.
        """
        try:
            # 1. Take the first character of the string
            first_char = self.news_string[0]
            # 2. Get the rest of the string
            rest_of_string = self.news_string[1:]
            # 3. Recombine them with the first char at the end
            self.news_string = rest_of_string + first_char
            
            # 4. Emit the updated string for the UI to display
            self.news_ticker_updated.emit(self.news_string)
            
        except IndexError:
            # This happens if self.news_string is empty
            pass 
        except Exception as e:
            print(f"Error scrolling news: {e}")