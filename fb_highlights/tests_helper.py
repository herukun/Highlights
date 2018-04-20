from datetime import datetime

import dateparser

from fb_bot import messenger_manager
from fb_bot.highlight_fetchers.fetcher_hoofoot import HoofootHighlight
from fb_bot.logger import logger
from fb_bot.model_managers import football_team_manager, football_competition_manager, latest_highlight_manager, \
    context_manager
from fb_highlights.models import User


def class_setup():
    logger.disable()
    messenger_manager.CLIENT.disable()


def set_up(test_user_id):
    context_manager.set_default_context(test_user_id)
    messenger_manager.CLIENT.messages = []


# Set up test database
def fill_db(test_user_id):

    # Create a test user
    User.objects.update_or_create(facebook_id=test_user_id,
                                  first_name="first",
                                  last_name="last",
                                  image_url="http://images/url.png",
                                  locale="en_GB",
                                  timezone=0,
                                  gender="male")

    # Add teams
    football_team_manager.add_football_team("chelsea")
    football_team_manager.add_football_team("barcelona")
    football_team_manager.add_football_team("real madrid")
    football_team_manager.add_football_team("arsenal")
    football_team_manager.add_football_team("liverpool")

    # Add competitions
    football_competition_manager.add_football_competition('champions league')
    football_competition_manager.add_football_competition('premier league')

    # Add highlights
    latest_highlight_manager.add_highlight(HoofootHighlight('http://hoofoot/chelsea-barcelona',
                                                            'Chelsea 0 - 2 Barcelona',
                                                            'http://hoofoot/images?chelsea-barcelona',
                                                            0,
                                                            'Champions League',
                                                            dateparser.parse('2018-01-01')))

    latest_highlight_manager.add_highlight(HoofootHighlight('http://hoofoot/chelsea-real_madrid',
                                                            'Arsenal 1 - 0 Real Madrid',
                                                            'http://hoofoot/images?chelsea-real_madrid',
                                                            0,
                                                            'Champions League',
                                                            dateparser.parse('2018-01-02')))

    latest_highlight_manager.add_highlight(HoofootHighlight('http://hoofoot/arsenal-liverpool',
                                                            'Arsenal 0 - 4 Liverpool',
                                                            'http://hoofoot/images?arsenal-liverpool',
                                                            0,
                                                            'Premier League',
                                                            dateparser.parse('2018-01-03')))

    latest_highlight_manager.add_highlight(HoofootHighlight('http://hoofoot/barcelona-liverpool',
                                                            'Barcelona 1 - 1 Liverpool',
                                                            'http://hoofoot/images?barcelona-liverpool',
                                                            0,
                                                            'Champions League',
                                                            datetime.now()))