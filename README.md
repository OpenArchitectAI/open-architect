[![](https://dcbadge.vercel.app/api/server/WCNEFsrtjw)](https://discord.gg/WCNEFsrtjw)

<h1 align="center">Open Architect</h1>

<p align="center">
<strong>Orchestrate your fleet of AI software designers, engineers and reviewers!</strong>

<img width="638" alt="image" src="https://github.com/OpenArchitectAI/open-architect/assets/1381992/3eb3c6d7-ff15-4b82-b85d-d32482123fad">
<br>
<br>
<span>Created at the MistralAI hackathon in SF</span>
<br>
</p>

Just create tickets (or have an AI architect assist you), and let the agents do the work. Your approval is required to merge PRs, so no bug or wrong code is ever introduced without your approval!

## Setup

1. Clone this repo
2. Install dependencies with `pip install -r requirements.txt`
3. Enter the infos related to the repository in which you want to work in `settings.json` or run `oa setup`
4. Profit

### How to connect to Github

1. Be part of the org of your repo
2. Go to https://github.com/settings/tokens?type=beta and create a personnal access token for the repo
3. Run the init_connections.py script and provide the URL to your repo and the access token

### Hot to connect to Trello

1. Connect to https://trello.com/ and log in. Navigate to your target Board. Save the Board ID.
2. Create a PowerUp for your Workspace at https://trello.com/power-ups/admin (you don't need the Iframe connector URL). Save your API Key and Secret
3. Run the init_connections.py script and provide the needed secrets

### Other requirement

For the Architect, you'll need an [OpenAI API key](https://platform.openai.com/api-keys) with some credits (we currently use GPT3.5 Turbo with a few tokens, see pricing [here](https://openai.com/pricing#:~:text=1M%20tokens-,GPT%2D3.5%20Turbo,-GPT%2D3.5%20Turbo))

   
## How to run

Design tickets and add them to your backlog with:
- `streamlit run start_architecting.py` to spawn an architect running in a chatbot that will create code tickets with you.

Run your fleet with:
- `./oa start intern` to spawn a developer that will process tickets and open PRs with code.
- `./oa start reviewer` to spawn a reviewer that will review PRs and ask for changes.

You can also start multiple ones with `./oa start agent1 agent2`

## Contributing

This is intended to be a collaborative project, and we'd love to take suggestions for new features, improvements, and fixes!

- If there is something you'd like us to work on, feel free to open an **Issue** with the adequate tag and a good description. If it's a bug, please add steps to reproduce it.
- If you have a contribution you'd like to make: first of all, thanks! You rock! Please open a PR and we'll review it as soon as we can!
