import requests
import json

class Draft:
    def __init__(self, league_id, draft_id, picks):
        self.league_id = league_id
        self.draft_id = draft_id
        self.picks = picks
        
    @staticmethod
    def get_picks_for_season(league_id, season):
        # Get all drafts grouped by season
        drafts_by_season = Draft.get_drafts(league_id)
        
        # Check if the specified season exists in the drafts
        if season not in drafts_by_season:
            print(f"No drafts found for season {season}")
            return None

        # Get the drafts for the specified season
        drafts_for_season = drafts_by_season[season]

        # Create a list to store the picks for the drafts of the specified season
        picks_for_season = []

        # Iterate over the drafts for the specified season
        for draft in drafts_for_season:
            # Get the draft ID
            draft_id = draft['draft_id']

            # Get the picks for the draft
            picks = Draft.get_picks_for_draft(league_id, draft_id)

            # Add the picks to the list of picks for the drafts of the specified season
            picks_for_season.extend(picks)

        # Print the picks for the season for debugging
        print(f"Picks for season {season}: {picks_for_season}")

        return picks_for_season
    
    @staticmethod
    def get_picks_for_draft(league_id, draft_id):
        # Make the API call to get the picks for the draft
        response = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks")

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to get picks for draft with ID {draft_id}")
            return []

        # Get the picks from the response
        picks = response.json()

        # Create a list to store the simplified picks
        simplified_picks = []

        # Iterate over the first 36 picks
        for pick in picks[:12]:
            # Create a simplified version of the pick with only the specified values
            simplified_pick = {
                'firstname': pick['metadata']['first_name'],
                'lastname': pick['metadata']['last_name'],
                'number': pick['metadata']['number'],
                'team': pick['metadata']['team'],
                'round': pick['round'],
                'pick number': pick['pick_no']
            }

            # Add the simplified pick to the list of simplified picks
            simplified_picks.append(simplified_pick)

        return simplified_picks

    @staticmethod
    def get_drafts(league_id):
        response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/drafts')
        data = json.loads(response.text)
        
        # Create a dictionary to store the drafts grouped by season
        drafts_by_season = {}
        
        # Iterate over the drafts
        for draft in data:
            # Get the season of the draft
            season = draft['season']
            
            # Check if the season exists in the dictionary
            if season not in drafts_by_season:
                # If the season doesn't exist, create it and set its value to an empty list
                drafts_by_season[season] = []
            
            # Add the draft to the list of drafts for this season
            drafts_by_season[season].append(draft)
        
        return drafts_by_season