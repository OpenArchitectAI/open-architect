# MoarSWEPls by OpenArchitect

Orchestrate your fleet of AI software designers, engineers and reviewers!

Just create tickets (or have an AI architect assist you), and let the agents do the work. Your approval is required to merge PRs, so no bug or wrong code is ever introduced without your approval!

## Setup

1. Clone this repo
2. Install dependencies with `pip install -r requirements.txt`
3. Enter the infos related to the repository in which you want to work in `settings.json` or run `oa setup`
4. Profit

### How to connect to Github

1. Be part of the org of your repo, or the owner of the repo.
2. Go to https://github.com/settings/tokens?type=beta and create a personnal access token for the repo
3. Run `oa setup github` to provide the path to your repo (in the format *owner/repo_name*) and the access token, or put them in `.env`

## How to run

Run your fleet with:
- `oa start intern` to spawn a developer that will process tickets and open PRs with code.
- `oa start reviewer` to spawn a reviewer that will review PRs and ask for changes.
- `oa start architect` to spawn an architect running in a chatbot that will create code tickets with you.

## Connecting to the GH Client

1. Be part of the org of your repo
2. Go to https://github.com/settings/tokens?type=beta and create a personnal access token for the repo
3. Run the init_connections.py script and provide the URL to your repo and the access token

## Connecting to the Trello Client

1. Connect to https://trello.com/ and log in. Navigate to your target Board. Save the Board ID.
2. Create a PowerUp for your Workspace at https://trello.com/power-ups/admin (you don't need the Iframe connector URL). Save your API Key and Secret
3. Run the init_connections.py script and provide the needed secrets
