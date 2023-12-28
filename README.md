# SleeperBot

The main.py file is a Python script that utilizes the Discord.py library to create a Discord bot. It imports various modules and classes, including requests, json, os, logging, discord, commands, Draft, Member, and load_dotenv.

The script sets up logging, loads environment variables from a .env file, and retrieves the Discord token and league ID from the environment variables. It creates a Discord bot instance with the specified command prefix and intents.

The script defines several bot commands, including sleeper, drafts, and picks. The sleeper command fetches user data from the Sleeper API based on a given username and sends a message with the user's ID and username. The drafts command retrieves a list of draft seasons for a specific league and sends a message with the seasons. The picks command retrieves the picks for a specific season in the league and sends a formatted message with the picks in JSON format.

Finally, the script runs the Discord bot using the provided token.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Classes](#classes)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository.
2. Install the required dependencies using `pip`:
    ```shell
    pip install -r requirements.txt
    ```

## Usage

1. Run the program:
    ```shell
    python main.py
    ```

## Classes
The Draft class represents a draft in a fantasy football league. It has the following attributes:

league_id: The ID of the league the draft belongs to.
draft_id: The ID of the draft.
picks: A list of picks made in the draft.
The class provides the following methods:

get_picks_for_season(league_id, season): Retrieves all the picks made in the drafts of a specific season for a given league. It returns a list of picks for the specified season.
get_picks_for_draft(league_id, draft_id): Retrieves the picks made in a specific draft for a given league. It returns a list of simplified picks.
get_drafts(league_id): Retrieves all the drafts for a given league. It returns a dictionary where the keys are the seasons and the values are lists of drafts for each season.
The Draft class utilizes the Sleeper API to make HTTP requests and retrieve the necessary data. It also includes some helper methods to simplify the retrieved data and organize it by season.

Note: The code snippet provided is missing the import statements for the requests and json modules, which are required for the class to work properly.

## Contributing

Contributions are welcome! Please follow the guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).
