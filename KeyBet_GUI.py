import sys
import requests
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
        self.base_url = 'http://34.168.124.158:5000'
        self.init_ui()
        self.authenticate_user()

    def init_ui(self):
        self.setWindowTitle('Soccer Predictor')
        self.setGeometry(100, 100, 600, 800)

        layout = QVBoxLayout()

        # Country selection
        country_layout = QHBoxLayout()
        country_layout.addWidget(QLabel('Country:'))
        self.country_combo = QComboBox()
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

    def authenticate_user(self):
        logged_in = False
        while not logged_in:
            login_dialog = LoginDialog()
            if login_dialog.exec_() == QDialog.Accepted:
                username, password = login_dialog.get_credentials()
                if self.login(username, password):
                    logged_in = True
                    self.load_countries()
                else:
                    QMessageBox.warning(self, 'Login Failed', 'Invalid username or password. Please try again.')
            else:
                sys.exit()

    def login(self, username, password):
        url = f'{self.base_url}/login'
        response = self.session.post(url, json={'username': username, 'password': password})
        return response.status_code == 200

    def load_countries(self):
        url = f'{self.base_url}/get_countries'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                countries = response.json()
                self.country_combo.addItems(countries)
            else:
                QMessageBox.warning(self, 'Error', 'Failed to load countries')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load countries: {str(e)}')

    def update_leagues(self, country):
        url = f'{self.base_url}/get_leagues/{country}'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                leagues = response.json()
                self.league_combo.clear()
                self.league_combo.addItems(leagues)
            else:
                QMessageBox.warning(self, 'Error', 'Failed to load leagues')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load leagues: {str(e)}')

    def update_teams(self, league):
        country = self.country_combo.currentText()
        url = f'{self.base_url}/get_teams/{country}/{league}'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                teams = response.json()
                self.home_team_combo.clear()
                self.away_team_combo.clear()
                self.home_team_combo.addItems(teams)
                self.away_team_combo.addItems(teams)
            else:
                QMessageBox.warning(self, 'Error', 'Failed to load teams')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load teams: {str(e)}')

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
                output += f"Full Time Result: {result['FTR']:.2f}\n"
                output += f"Half Time Result: {result['HTR']:.2f}\n"
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
