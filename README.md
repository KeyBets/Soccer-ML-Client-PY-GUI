# KEY BET || Soccer Predictor

A user-friendly soccer prediction desktop application built using Python and PyQt5. The app fetches soccer team data and predictions via an API and provides results for match outcomes, including goals, corners, and more. 
**NOTE:** go to r/keybet subreddit and dm the api key or device ID generated and stored in credentials.csv to the mods/ modmail.

## Features

- **Country and League Selection**: Choose from a list of countries and leagues to select teams for predictions.
- **Home and Away Teams**: Pick home and away teams from available leagues for an upcoming match.
- **Match Prediction**: Predict match outcomes like full-time/half-time goals, corners, red cards, and the winner using machine learning-based forecasts from an API.
- **Results Display**: View predictions and raw data in a readable format.

## Installation

### 1. Python Installation (For Developers and Advanced Users)

Make sure Python 3.x is installed on your system. You will also need to install the required dependencies to run the app.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/soccer-prediction-client.git
cd Soccer-ML-Client-PY-GUI
```

#### Step 2: Install the Required Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Here's what the `requirements.txt` should look like for the dependencies:
```
PyQt5
requests
```

#### Step 3: Prepare the `teams.csv` File

Ensure you have a `teams.csv` file in the root directory, containing the following columns:

| Country | League | team  |
|---------|--------|-------|
| Example | League1| Team1 |
| Example | League2| Team2 |

#### Step 4: Run the App

```bash
python soccer_prediction.py
```

### 2. EXE Installation (For Beginners and Windows Users)

If you're unfamiliar with Python or just want a quick setup, you can download the pre-built executable file from the [releases](https://github.com/KeyBets/Soccer-ML-Client-PY-GUI/releases) page.

#### Step 1: Download the ZIP

- Go to the [releases](https://github.com/KeyBets/Soccer-ML-Client-PY-GUI/releases) page, download the latest `.zip` file and extract.

#### Step 2: Run the EXE

- After extracting, double-click the EXE file to run the app on your Windows machine.

No installation of Python or other dependencies is required.

## Usage

1. Launch the app.
2. Select the **Country** and **League**.
3. Choose the **Home Team** and **Away Team**.
4. Click the `Predict` button to receive a prediction for the match.

## API and Prediction Details

The app sends team data to an external API to get match predictions. The results include:

- Full-time goals
- Half-time goals
- Corners
- Red cards
- Match winner (1 for home, 0 for draw, -1 for away)

## Contributing

If you'd like to contribute to this project, feel free to fork the repository and submit a pull request. We welcome all improvements and new features!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
