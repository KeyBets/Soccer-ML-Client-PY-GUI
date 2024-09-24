from decimal import Decimal
import sys
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QTextEdit
from PyQt5.QtGui import QFont
import requests

class SoccerPredictionClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_teams()

    def initUI(self):
        self.setWindowTitle('KEY BET || Soccer Predictor')
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        # Country selection
        country_layout = QHBoxLayout()
        country_layout.addWidget(QLabel('Country:'))
        self.country_combo = QComboBox()
        country_layout.addWidget(self.country_combo)
        layout.addLayout(country_layout)

        # League selection
        league_layout = QHBoxLayout()
        league_layout.addWidget(QLabel('League:'))
        self.league_combo = QComboBox()
        league_layout.addWidget(self.league_combo)
        layout.addLayout(league_layout)

        # Team selection
        team_layout = QHBoxLayout()
        team_layout.addWidget(QLabel('Home Team:'))
        self.home_team_combo = QComboBox()
        team_layout.addWidget(self.home_team_combo)
        team_layout.addWidget(QLabel('Away Team:'))
        self.away_team_combo = QComboBox()
        team_layout.addWidget(self.away_team_combo)
        layout.addLayout(team_layout)

        # Predict button
        self.predict_button = QPushButton('Predict')
        self.predict_button.clicked.connect(self.predict_match)
        layout.addWidget(self.predict_button)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)

        self.setLayout(layout)

    def load_teams(self):
        self.teams = {}
        try:
            with open('teams.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    country = row['Country']
                    league = row['League']
                    team = row['team']
                    if country not in self.teams:
                        self.teams[country] = {}
                    if league not in self.teams[country]:
                        self.teams[country][league] = []
                    self.teams[country][league].append(team)

            self.country_combo.addItems(sorted(self.teams.keys()))
            self.country_combo.currentTextChanged.connect(self.update_leagues)
            self.league_combo.currentTextChanged.connect(self.update_teams)
            
            self.update_leagues(self.country_combo.currentText())
        except FileNotFoundError:
            self.results_display.setText("Error: teams.csv file not found.")

    def update_leagues(self, country):
        self.league_combo.clear()
        if country in self.teams:
            self.league_combo.addItems(sorted(self.teams[country].keys()))
        self.update_teams(self.league_combo.currentText())

    def update_teams(self, league):
        self.home_team_combo.clear()
        self.away_team_combo.clear()
        country = self.country_combo.currentText()
        if country in self.teams and league in self.teams[country]:
            teams = sorted(self.teams[country][league])
            self.home_team_combo.addItems(teams)
            self.away_team_combo.addItems(teams)

    def predict_match(self):
        home_team = self.home_team_combo.currentText()
        away_team = self.away_team_combo.currentText()

        if home_team == away_team:
            self.results_display.setText("Error: Home team and Away team must be different.")
            return

        try:
            response = requests.post('http://34.83.220.67:5000/predict', 
                                    json={'home_team': home_team, 'away_team': away_team})
            
            if response.status_code == 200:
                result = response.json()
                
                # Format the output
                output = f"Prediction for {home_team} vs {away_team}:\n\n"
                output += f"Full Time Result: {result['Result']} (Home: {result['FTHG']:.2f} - Away: {result['FTAG']:.2f})\n"
                output += f"Half Time Result: {result['HTResult']} (Home: {result['HTHG']:.2f} - Away: {result['HTAG']:.2f})\n\n"
                
                output += "Other Statistics:\n"
                output += f"Corners: Home {result['HC']:.2f} - Away {result['AC']:.2f}\n"
                output += f"Fouls: Home {result['HF']:.2f} - Away {result['AF']:.2f}\n"
                output += f"Yellow Cards: Home {result['HY']:.2f} - Away {result['AY']:.2f}\n"
                output += f"Red Cards: Home {result['HR']:.2f} - Away {result['AR']:.2f}\n"
                
                output += "\nFull Prediction Data:\n"
                for key, value in result.items():
                    if isinstance(value, float):
                        output += f"{key}: {value:.4f}\n"
                    else:
                        output += f"{key}: {value}\n"
                
                self.results_display.setText(output)
            else:
                self.results_display.setText(f"Error: Received status code {response.status_code} from server.")
        
        except requests.exceptions.RequestException as e:
            self.results_display.setText(f"Error connecting to server: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SoccerPredictionClient()
    ex.show()
    sys.exit(app.exec_())