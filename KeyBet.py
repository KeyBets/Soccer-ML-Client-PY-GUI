import sys
import requests
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QTextEdit, QProgressBar, QDialog, QLineEdit, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 150)
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        layout.addRow('Username:', self.username_input)
        layout.addRow('Password:', self.password_input)

        button_box = QHBoxLayout()
        login_button = QPushButton('Login')
        login_button.clicked.connect(self.accept)
        button_box.addWidget(login_button)

        layout.addRow(button_box)
        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()

class SoccerPredictionClient(QWidget):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.base_url = self.load_server_ip()
        self.teams_data = self.load_teams_from_csv('teams.csv')
        self.init_ui()
        self.authenticate_user()

    def load_server_ip(self):
        try:
            with open('server_ip.txt', 'r') as f:
                ip = f.read().strip()
            return f'http://{ip}'
        except FileNotFoundError:
            print("Error: server_ip.txt not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading server IP: {str(e)}")
            sys.exit(1)

    def load_teams_from_csv(self, filename):
        teams_data = {}
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    country = row['Country']
                    league = row['League']
                    team = row['team']
                    if country not in teams_data:
                        teams_data[country] = {}
                    if league not in teams_data[country]:
                        teams_data[country][league] = []
                    teams_data[country][league].append(team)
            
            # Sort everything alphabetically
            for country in teams_data:
                for league in teams_data[country]:
                    teams_data[country][league].sort()
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
        return teams_data

    def init_ui(self):
        self.setWindowTitle('KeyBet || Soccer Predictor')
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        # Country selection
        country_layout = QHBoxLayout()
        country_layout.addWidget(QLabel('Country:'))
        self.country_combo = QComboBox()
        self.country_combo.addItems(sorted(self.teams_data.keys()))
        self.country_combo.currentTextChanged.connect(self.update_leagues)
        country_layout.addWidget(self.country_combo)
        layout.addLayout(country_layout)

        # League selection
        league_layout = QHBoxLayout()
        league_layout.addWidget(QLabel('League:'))
        self.league_combo = QComboBox()
        self.league_combo.currentTextChanged.connect(self.update_teams)
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

        # Winner bars
        bars_layout = QHBoxLayout()
        self.home_bar = QProgressBar(self)
        self.home_bar.setRange(0, 100)
        bars_layout.addWidget(QLabel('Home Team:'))
        bars_layout.addWidget(self.home_bar)

        self.away_bar = QProgressBar(self)
        self.away_bar.setRange(0, 100)
        bars_layout.addWidget(QLabel('Away Team:'))
        bars_layout.addWidget(self.away_bar)
        layout.addLayout(bars_layout)

        # Output text area
        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

        self.setLayout(layout)

        # Initialize leagues for the first country
        self.update_leagues(self.country_combo.currentText())

    def authenticate_user(self):
        logged_in = False
        while not logged_in:
            login_dialog = LoginDialog()
            if login_dialog.exec_() == QDialog.Accepted:
                username, password = login_dialog.get_credentials()
                if self.login(username, password):
                    logged_in = True
                else:
                    QMessageBox.warning(self, 'Login Failed', 'Invalid username or password. Please try again.')
            else:
                sys.exit()

    def login(self, username, password):
        url = f'{self.base_url}/login'
        response = self.session.post(url, json={'username': username, 'password': password})
        return response.status_code == 200

    def update_leagues(self, country):
        self.league_combo.clear()
        if country in self.teams_data:
            self.league_combo.addItems(sorted(self.teams_data[country].keys()))

    def update_teams(self, league):
        country = self.country_combo.currentText()
        self.home_team_combo.clear()
        self.away_team_combo.clear()
        if country in self.teams_data and league in self.teams_data[country]:
            teams = self.teams_data[country][league]
            self.home_team_combo.addItems(teams)
            self.away_team_combo.addItems(teams)

    def predict_match(self):
        home_team = self.home_team_combo.currentText()
        away_team = self.away_team_combo.currentText()

        if home_team == away_team:
            self.text_area.setText("Error: Home and Away teams cannot be the same.")
            return

        url = f'{self.base_url}/predict'
        data = {'home_team': home_team, 'away_team': away_team}

        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                output = f"Prediction:\n\n"
                output += f"Full Time Home Goals: {result['FTHG']:.2f}\n"
                output += f"Full Time Away Goals: {result['FTAG']:.2f}\n"
                output += f"Half Time Home Goals: {result['HTHG']:.2f}\n"
                output += f"Half Time Away Goals: {result['HTAG']:.2f}\n"
                output += f"Full Time Result: {result['Winner_numeric']:.2f}\n"
                output += f"Half Time Result: {result['HTWinner_numeric']:.2f}\n"
                output += f"Home Corners: {result['HC']:.2f}\n"
                output += f"Away Corners: {result['AC']:.2f}\n"
                output += f"Home Shots: {result['HS']:.2f}\n"
                output += f"Away Shots: {result['AS']:.2f}\n"
                output += f"Home Shots on Target: {result['HST']:.2f}\n"
                output += f"Away Shots on Target: {result['AST']:.2f}\n"

                self.text_area.setText(output)

                # Update progress bars
                total_goals = result['FTHG'] + result['FTAG']
                home_percentage = (result['FTHG'] / total_goals) * 100 if total_goals > 0 else 50
                self.home_bar.setValue(int(home_percentage))
                self.away_bar.setValue(100 - int(home_percentage))
            else:
                self.text_area.setText(f"Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            self.text_area.setText(f"Error: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = SoccerPredictionClient()
    client.show()
    sys.exit(app.exec_())