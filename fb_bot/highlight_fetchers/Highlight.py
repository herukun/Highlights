import abc

from fb_bot.highlight_fetchers import football_team_mapping


class Highlight:
    __metaclass__ = abc.ABCMeta

    def __init__(self, link, match_name, img_link, view_count, category, time_since_added):
        self.link = link
        self.img_link = img_link
        self.view_count = view_count
        self.category = category
        self.time_since_added = time_since_added

        # Match information
        team1, score1, team2, score2 = self.get_match_info(match_name)

        # Run mapping for football team names as team can be named differently
        self.team1 = football_team_mapping.get_exact_name(team1.lower())
        self.team2 = football_team_mapping.get_exact_name(team2.lower())

        self.score1 = score1
        self.score2 = score2

        # Source of the highlight (website)
        self.source = self.get_source()

    @abc.abstractmethod
    def get_match_info(self, match):
        """ Override method """

    @abc.abstractmethod
    def get_source(self):
        """ Override method """

    def __str__(self):
        return str((self.link, self.team1, self.score1, self.team2, self.score2,
                    self.img_link, self.view_count, self.category, self.time_since_added, self.source))