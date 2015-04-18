# -*- coding: utf-8 -*-
__author__ = 'Spim'

import APIKey as KEY
import sys
import ChampConsts
import requests
import time
import collections
from PySide.QtCore import *
from PySide.QtGui import *

class ResultTable(QTableWidget):
    """
    This class will only be used for one purpose.
    Therefore, it will have a fixed number of
    rows and columns, and a fixed size.
    """
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)
        self.setWindowTitle("Score Breakdown")
        self.setRowCount(12)
        self.setColumnCount(10)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.setFixedSize(847, 385)
        self.setStyleSheet("QTableWidgetItem {color:white}")
        self.setIconSize(QSize(30, 30))

    """
    paintEvent(): Overriding this is required
    in order to have an image background.
    """
    def paintEvent(self, event):
        self.tile = QPixmap('result_background.png')
        painter = QPainter(self.viewport())
        painter.drawTiledPixmap(self.rect(), self.tile)
        super(ResultTable, self).paintEvent(event)
        painter.end()

    """
    setItem(): Overriden because the image
    background is so dark, all text items
    added must be recolored to white.
    """
    def setItem(self, row, column, item):
        text_color = QBrush(QColor("white"))
        item.setForeground(text_color)
        QTableWidget.setItem(self, row, column, item)

"""
Form will serve as the housing for the actual
application.  It would have been better to
have Form inherit from QMainWindow from the
start, but now the formatting would get
destroyed by that change.
"""
class Form(QDialog):
    """
    Initialize the dialog/form:
        layout_overall (vertical):
            layout_storage (horizontal):
                swidget_team_1:
                    layout_team_1 (vertical):
                        *displays contents of _team_1_dict as buttons*
                champ_scroll_widget:
                    swidget_champions:

                swidget_team_2:
            ban_widget:
                layout_ban
    """
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        
        #Set game members:
        self._champ_list = collections.OrderedDict()
        for key, value in sorted(ChampConsts.CHAMP_NAME.items()):
            self._champ_list[key] = value
        self._team_1_dict = dict()
        self._team_2_dict = dict()
        self._team_1_ban_list = []
        self._team_2_ban_list = []
        self._game_list = []
        self._turn = 0
        self._team_1_score = 0
        self._team_2_score = 0
        
        #Set window attributes:
        self.setWindowTitle("ULTRA RAPID FANTASY")
        self.setFixedSize(QSize(650, 366))
        
        #Set up results window
        self.widget_results = ResultTable()
        self.widget_results.closeEvent = self.__ask_play_again
        
        #TONS OF SWIDGETS (for layout storage!)
        self.swidget_left_panel = QWidget()
        self.swidget_right_panel = QWidget()
        self.swidget_team_1 = QWidget()
        self.swidget_team_2 = QWidget()
        self.swidget_team_1_ban = QWidget()
        self.swidget_team_2_ban = QWidget()
        self.swidget_champions = QWidget()
        self.yet_another_widget = QWidget()
        #Set up swidget attributes
        self.swidget_team_1.setFixedSize(70, 200)
        self.swidget_team_2.setFixedSize(70, 200)
        self.swidget_team_1_ban.setFixedSize(70, 100)
        self.swidget_team_2_ban.setFixedSize(70, 100)
        self.swidget_champions.setStyleSheet("QWidget {background:transparent}")
        self.swidget_champions.setWindowFlags(Qt.FramelessWindowHint)
        self.swidget_champions.setAttribute(Qt.WA_TranslucentBackground)
        
        #TONS OF LAYOUTS
        self.layout_overall = QVBoxLayout()
        self.layout_storage = QHBoxLayout()
        self.layout_left_panel = QVBoxLayout(self.swidget_left_panel)
        self.layout_right_panel = QVBoxLayout(self.swidget_right_panel)
        self.layout_team_1 = QVBoxLayout(self.swidget_team_1)
        self.layout_team_2 = QVBoxLayout(self.swidget_team_2)
        self.layout_team_1_bans = QVBoxLayout(self.swidget_team_1_ban)
        self.layout_team_2_bans = QVBoxLayout(self.swidget_team_2_ban)
        self.layout_center_panel = QVBoxLayout(self.yet_another_widget)
        
        #Create non-storage widgets
        self.__menu_bar = QMenuBar()
        self.instruction_label = QLabel()
        self.champ_scroll_widget = QScrollArea()

        #Set up non-storage widgets
        self.__menu_bar.addAction("About", self.__riot_disclaimer)
        self.instruction_label.setFixedWidth(400)
        self.instruction_label.setAlignment(Qt.AlignHCenter)
        self.champ_scroll_widget.setWidgetResizable(True)
        self.champ_scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.champ_scroll_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.champ_scroll_widget.setStyleSheet("QWidget {background:transparent}")
        self.champ_scroll_widget.setWindowFlags(Qt.FramelessWindowHint)
        self.champ_scroll_widget.setAttribute(Qt.WA_TranslucentBackground)

        #Attach things to layouts
        self.layout_overall.addWidget(self.__menu_bar)
        self.layout_overall.addLayout(self.layout_storage)
        self.layout_left_panel.addWidget(self.swidget_team_1)
        self.layout_left_panel.addWidget(self.swidget_team_1_ban)
        self.layout_right_panel.addWidget(self.swidget_team_2)
        self.layout_right_panel.addWidget(self.swidget_team_2_ban)
        self.layout_center_panel.addWidget(self.instruction_label)
        self.layout_center_panel.addWidget(self.champ_scroll_widget)
        self.layout_storage.addWidget(self.swidget_left_panel)
        self.layout_storage.addWidget(self.yet_another_widget)
        self.layout_storage.addWidget(self.swidget_right_panel)

        #Gather a list of URF games in another thread
        self._get_games_thread = QThread()
        self._get_games_thread.run = self.get_game_list
        self._get_games_thread.start()

        #Music initialization/playing
        league_music = QSound("ChampSelect.wav")
        league_music.play()

        self.redraw()

    """
    __riot_disclaimer(): Displays the disclaimer
    requested by "Attribution" in the
    API Terms & Conditions.
    """
    def __riot_disclaimer(self):
        disclaimer = QMessageBox()
        disclaimer_text = "ULTRA RAPID FANTASY isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc."
        disclaimer.setText(disclaimer_text)
        disclaimer.setWindowTitle("About URF")
        disclaimer.exec_()
    """
    get_game_list(): Get a list of URF games.
    Originally, this was meant to collect an
    hours' worth of games, from two hours ago
    to an hour ago. Because URF was disabled,
    this now collects games from a fixed time
    known to work: Mon, 13 Apr 2015 02:15:00 GMT
    Also, to avoid long wait times, this now
    collects only 50 minutes worth of games.
    """
    def get_game_list(self):
        #current_time = (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds()
        #valid_time = int(current_time - (current_time % 300)) - 7200
        valid_time = 1428891300
        x = 0
        print("Loading game list, please wait...")
        #Pull 50 minutes (10 * 5) worth of games IDs.
        while x < 10:
            response = requests.get(
                "https://na.api.pvp.net/api/lol/na/v4.1/game/ids?beginDate=" +
                str(valid_time) +
                "&api_key=" +
                KEY.API_KEY)
            #Sleep for the length of "retry-after" header.
            if response.status_code == 429:
                print(
                    "Sleeping for " +
                    str(int(response.headers['retry-after']) + 1))
                time.sleep(int(response.headers['retry-after']) + 1)
            #Abort and self-destruct if we get a different error.
            elif response.status_code != 200:
                print("Bad response code: " + str(response.status_code))
                print(response.reason)
                sys.exit("Bad response")
            #Append each game ID retrieved to _game_list.
            else:
                print("Good response code (" + str(x + 1) + " / 10)")
                temp_list = response.json()
                for y in xrange(0, temp_list.__len__()):
                    self._game_list.append(temp_list[y])
                valid_time += 300
                x += 1

    """
    select_champion(): When a button is clicked,
    figures out what champion is associated with
    that button, and uses _turn to figure out
    where that champion should go.
    """
    def select_champion(self):
        button_name = self.sender().property('champion')
        if self._turn == 0 or self._turn == 2 or self._turn == 4:
            self._team_1_ban_list.append(button_name)
            self._turn += 1
        elif self._turn == 1 or self._turn == 3 or self._turn == 5:
            self._team_2_ban_list.append(button_name)
            self._turn += 1
        elif self._turn == 6 or self._turn == 9 or self._turn == 10 \
                or self._turn == 13 or self._turn == 14:
            self._team_1_dict[button_name] = 1
            self._turn += 1
        elif self._turn == 7 or self._turn == 8 or self._turn == 11 \
                or self._turn == 12 or self._turn == 15:
            self._team_2_dict[button_name] = 1
            self._turn += 1
        elif self._turn == 16:
            return
        else:
            sys.exit("Illegal Turn Value")
        self._champ_list.pop(button_name)
        self.redraw()

    """
    redraw() handles:
    -Removing all previous buttons
    -Recreating buttons according to game state
    -Changing instruction_label to advise players
    -Prompting scoring phase when teams are complete.
    """
    def redraw(self):
        #Create Widgets
        self.swidget_champions = QWidget()
        self.layout_champs = QVBoxLayout(self.swidget_champions)

        #Set instruction_label based on _turn
        if self._turn == 0 or self._turn == 2 or self._turn == 4:
            self.instruction_label.setText(
                "TEAM 1, BAN A CHAMPION (" +
                str(6 - self._turn) +
                " BANS LEFT)")
        if self._turn == 1 or self._turn == 3 or self._turn == 5:
            self.instruction_label.setText(
                "TEAM 2, BAN A CHAMPION (" +
                str(6 - self._turn) +
                " BANS LEFT)")
        if self._turn == 6 or self._turn == 9 or self._turn == 10 \
                or self._turn == 13 or self._turn == 14:
            self.instruction_label.setText("TEAM 1, PICK A CHAMPION")
        if self._turn == 7 or self._turn == 8 or self._turn == 11 \
                or self._turn == 12 or self._turn == 15:
            self.instruction_label.setText("TEAM 2, PICK A CHAMPION")
        self.instruction_label.setStyleSheet("QLabel {color:white;font-size:400%}")

        #Reset Widgets
        while not self.layout_team_1.count() == 0:
            doomed_button = self.layout_team_1.takeAt(0)
            doomed_button.widget().deleteLater()
        while not self.layout_team_2.count() == 0:
            doomed_button = self.layout_team_2.takeAt(0)
            doomed_button.widget().deleteLater()
        while not self.layout_team_1_bans.count() == 0:
            doomed_button = self.layout_team_1_bans.takeAt(0)
            doomed_button.widget().deleteLater()
        while not self.layout_team_2_bans.count() == 0:
            doomed_button = self.layout_team_2_bans.takeAt(0)
            doomed_button.widget().deleteLater()

        #Reset team labels
        team_1_label = QLabel("Team 1")
        team_1_label.setStyleSheet("QLabel {color:white}")
        self.layout_team_1.addWidget(team_1_label)
        team_2_label = QLabel("Team 2")
        team_2_label.setStyleSheet("QLabel {color:white}")
        self.layout_team_2.addWidget(team_2_label)

        #Populate team 1 buttons
        for champion in self._team_1_dict:
            temp = self.champion_to_button(champion)
            self.layout_team_1.addWidget(temp)

        #Populate team 2 buttons
        for champion in self._team_2_dict:
            temp = self.champion_to_button(champion)
            self.layout_team_2.addWidget(temp)

        #Populate team 1's bans
        for champion in self._team_1_ban_list:
            temp = self.champion_to_button(champion)
            self.layout_team_1_bans.addWidget(temp)

        #Populate team 2's bans
        for champion in self._team_2_ban_list:
            temp = self.champion_to_button(champion)
            self.layout_team_2_bans.addWidget(temp)

        #Populate champion pool buttons, with 10 to a row.
        x = 0
        new_layout = QHBoxLayout()
        for champion in self._champ_list:
            temp = self.champion_to_button(champion)
            temp.clicked.connect(self.select_champion)
            new_layout.addWidget(temp)
            x = x + 1
            if x % 10 == 0:
                new_layout.setSpacing(10)
                new_layout.setContentsMargins(0, 0, 10, 0)
                self.layout_champs.addLayout(new_layout)
                new_layout = QHBoxLayout()
        self.layout_champs.addLayout(new_layout)

        #Set layout
        self.champ_scroll_widget.setWidget(self.swidget_champions)
        self.setLayout(self.layout_overall)

        #Check for end of pick/ban phase
        if self._turn > 15:
            self._thread_pull_games = QThread()
            self._thread_pull_games.run = self.pull_games
            self._thread_pull_games.finished.connect(self.calc_scores)
            self._thread_pull_games.start()
            self.instruction_label.setText("Loading scores, please wait...")

    """
    champion_to_button(): Given a champion name,
    this function will return a button with the
    appropriate icon and size, and with the
    champion name as a property.
    """
    def champion_to_button(self, champion):
        temp = QPushButton()
        temp_icon = QIcon(ChampConsts.CHAMP_NAME[champion]['Icon'])
        temp.setIcon(temp_icon)
        temp.setIconSize(QSize(30, 30))
        temp.setFixedSize(QSize(30, 30))
        temp.setProperty('champion', champion)
        return temp

    """
    pull_games(): Makes an API request for each
    game ID gathered into _game_list. Collects
    information for champions selected by either
    player, and can finish early if each champion
    has been found.
    """
    def pull_games(self):
        game_list_len = self._game_list.__len__()
        count = 0
        while count < game_list_len:
            #Quit early if we have two full teams' worth of valid info.
            quit_flag = True
            for y in self._team_1_dict:
                if self._team_1_dict[y] == 1:
                    quit_flag = False
            for y in self._team_2_dict:
                if self._team_2_dict[y] == 1:
                    quit_flag = False
            if quit_flag:
                break

            response = requests.get(
                "https://na.api.pvp.net/api/lol/na/v2.2/match/" +
                str(self._game_list[count]) +
                "?includeTimeline=false&api_key=" +
                KEY.API_KEY)
            #If the return code is 429 "Rate Limit Exceeded",
            #sleep for as long as the response Retry-After
            #header asks.
            if response.status_code == 429:
                print("Sleeping for " + response.headers['retry-after'])
                self.instruction_label.setText(
                    "Loading scores, please wait... " +
                    str(int(100 * count / game_list_len)) +
                    "% *API Pause*")
                time.sleep(int(response.headers['retry-after']))
            #Run screaming for the hills if we have any other error.
            elif response.status_code != 200:
                print("Bad Code: " + str(response.status_code))
                print response.reason
                sys.exit("Bad response")
            #Report each good pull and any relevant champions found
            #to the console.  For the first of a given relevant
            #champion found, save its info into the proper team dict.
            else:
                print("Good Pull: " + str(count) + " / " + str(game_list_len))
                for y in response.json()['participants']:
                    current_champ = ChampConsts.CHAMP_ID[y['championId']]
                    if current_champ in self._team_1_dict:
                        print("Hit: " + ChampConsts.CHAMP_ID[y['championId']])
                        if self._team_1_dict[current_champ] == 1:
                            self._team_1_dict[current_champ] = y['stats']
                    elif current_champ in self._team_2_dict:
                        print("Hit: " + ChampConsts.CHAMP_ID[y['championId']])
                        if self._team_2_dict[current_champ] == 1:
                            self._team_2_dict[current_champ] = y['stats']
                count += 1
                #Crude progress count for the GUI to display.
                self.instruction_label.setText(
                    "Loading scores, please wait... " +
                    str(int(100 * count / game_list_len)) +
                    "%")
                #Sleep every other pull to reduce rate of API requests
                #and make load time seem smoother.
                if count % 2 == 0:
                    time.sleep(1)

    """
    calc_scores(): Uses the information obtained in
    the pull_games thread to count the scores for
    each champion (and each team).  Also preps the
    widget_results table to display each champion's
    stats.
    """
    def calc_scores(self):
        self.widget_results.setHorizontalHeaderLabels(
            ["Champion", "Overall Score", "Kills (2x)",
             "Deaths (-.5x)", "Assists (1.5x)",
             "CS (.01x)", "Triple Kills (2x)",
             "Quadra Kills (5x)", "Penta Kills (10x)",
             "10+ Kills/Assists (+2)"])
        row_count = 1

        self.widget_results.setItem(0, 0, QTableWidgetItem("Team 1"))
        score_string = "Scores for Team 1: \n"
        for champion in self._team_1_dict:
            champ_icon = QIcon(ChampConsts.CHAMP_NAME[champion]['Icon'])
            self.widget_results.setItem(row_count, 0, QTableWidgetItem(champ_icon, ""))
            if self._team_1_dict[champion] == 1:
                self.widget_results.setItem(row_count, 1, QTableWidgetItem("0"))
                for column_count in xrange(2, 10):
                    self.widget_results.setItem(row_count, column_count, QTableWidgetItem("N/A"))
                row_count += 1
                continue
            temp_score = 0.0
            champ_kills = int(self._team_1_dict[champion]['kills'])
            champ_deaths = int(self._team_1_dict[champion]['deaths'])
            champ_assists = int(self._team_1_dict[champion]['assists'])
            champ_cs = int(self._team_1_dict[champion]['minionsKilled'])
            champ_triples = int(self._team_1_dict[champion]['tripleKills'])
            champ_quadras = int(self._team_1_dict[champion]['quadraKills'])
            champ_pentas = int(self._team_1_dict[champion]['pentaKills'])
            temp_score += champ_kills * 2
            self.widget_results.setItem(row_count, 2, QTableWidgetItem(str(champ_kills)))
            temp_score -= champ_deaths * 0.5
            self.widget_results.setItem(row_count, 3, QTableWidgetItem(str(champ_deaths)))
            temp_score += champ_assists * 1.5
            self.widget_results.setItem(row_count, 4, QTableWidgetItem(str(champ_assists)))
            temp_score += champ_cs / 100.0
            self.widget_results.setItem(row_count, 5, QTableWidgetItem(str(champ_cs)))
            temp_score += champ_triples * 2
            self.widget_results.setItem(row_count, 6, QTableWidgetItem(str(champ_triples)))
            temp_score += champ_quadras * 5
            self.widget_results.setItem(row_count, 7, QTableWidgetItem(str(champ_quadras)))
            temp_score += champ_pentas * 10
            self.widget_results.setItem(row_count, 8, QTableWidgetItem(str(champ_pentas)))
            if (champ_kills >= 10) or (champ_assists >= 10):
                temp_score += 2
                self.widget_results.setItem(row_count, 9, QTableWidgetItem("Yes"))
            else:
                self.widget_results.setItem(row_count, 9, QTableWidgetItem("No"))
            self.widget_results.setItem(row_count, 1, QTableWidgetItem(str(temp_score)))
            self._team_1_score += temp_score
            row_count += 1

        self.widget_results.setItem(row_count, 0, QTableWidgetItem("Team 2"))
        row_count += 1
        score_string += "Scores for Team 2: \n"
        for champion in self._team_2_dict:
            champ_icon = QIcon(ChampConsts.CHAMP_NAME[champion]['Icon'])
            self.widget_results.setItem(row_count, 0, QTableWidgetItem(champ_icon, ""))
            if self._team_2_dict[champion] == 1:
                self.widget_results.setItem(row_count, 1, QTableWidgetItem("0"))
                for column_count in range(2, 10):
                    self.widget_results.setItem(row_count, column_count, QTableWidgetItem("N/A"))
                continue
            temp_score = 0.0
            champ_kills = int(self._team_2_dict[champion]['kills'])
            champ_deaths = int(self._team_2_dict[champion]['deaths'])
            champ_assists = int(self._team_2_dict[champion]['assists'])
            champ_cs = int(self._team_2_dict[champion]['minionsKilled'])
            champ_triples = int(self._team_2_dict[champion]['tripleKills'])
            champ_quadras = int(self._team_2_dict[champion]['quadraKills'])
            champ_pentas = int(self._team_2_dict[champion]['pentaKills'])
            temp_score += champ_kills * 2
            self.widget_results.setItem(row_count, 2, QTableWidgetItem(str(champ_kills)))
            temp_score -= champ_deaths * 0.5
            self.widget_results.setItem(row_count, 3, QTableWidgetItem(str(champ_deaths)))
            temp_score += champ_assists * 1.5
            self.widget_results.setItem(row_count, 4, QTableWidgetItem(str(champ_assists)))
            temp_score += champ_cs / 100.0
            self.widget_results.setItem(row_count, 5, QTableWidgetItem(str(champ_cs)))
            temp_score += champ_triples * 2
            self.widget_results.setItem(row_count, 6, QTableWidgetItem(str(champ_triples)))
            temp_score += champ_quadras * 5
            self.widget_results.setItem(row_count, 7, QTableWidgetItem(str(champ_quadras)))
            temp_score += champ_pentas * 10
            self.widget_results.setItem(row_count, 8, QTableWidgetItem(str(champ_pentas)))
            if (champ_kills >= 10) or (champ_assists >= 10):
                temp_score += 2
                self.widget_results.setItem(row_count, 9, QTableWidgetItem("Yes"))
            else:
                self.widget_results.setItem(row_count, 9, QTableWidgetItem("No"))
            self.widget_results.setItem(row_count, 1, QTableWidgetItem(str(temp_score)))
            self._team_2_score += temp_score
            row_count += 1
        self.widget_results.show()

    """
    __ask_play_again(): Prepare and display a
    message box to show the winner and ask the
    players if they want to play again.
    """
    def __ask_play_again(self, event):
        event.accept()
        ask_replay = QMessageBox.StandardButton.Yes
        ask_replay |= QMessageBox.StandardButton.No
        result_string = "Team 1: " + str(self._team_1_score) + "\nTeam 2: " + str(self._team_2_score)
        if self._team_1_score > self._team_2_score:
            result_string += "\nTeam 1 is... \nULTRA RAPIDLY FANTASTIC!"
        elif self._team_1_score < self._team_2_score:
            result_string += "\nTeam 2 is... \nULTRA RAPIDLY FANTASTIC!"
        else:
            result_string += "\nBoth teams are... \nULTRA RAPIDLY FANTASTIC!"
        response = QMessageBox.question(self, "Results", result_string + "\nPlay again?", ask_replay)
        if response == QMessageBox.Yes:
            self.replay()
        else:
            self.quit()

    """
    replay(): Reset the game members and music,
    and redraw the screen for a new game.
    """
    def replay(self):
        self._team_1_dict = dict()
        self._team_2_dict = dict()
        self._team_1_ban_list = []
        self._team_2_ban_list = []
        self._team_1_score = 0
        self._team_2_score = 0
        self._champ_list = collections.OrderedDict()
        for key, value in sorted(ChampConsts.CHAMP_NAME.items()):
            self._champ_list[key] = value
        self._turn = 0
        QSound.play("ChampSelect.wav")
        self.redraw()

    """
    quit(): Quits.
    """
    def quit(self):
        sys.exit()

    """
    paintEvent(): Overloading this was required
    in order to display an image background.
    """
    def paintEvent(self, event):
        self.tile= QPixmap('background.png')
        painter = QPainter(self)
        painter.drawTiledPixmap(self.rect(), self.tile)
        super(Form, self).paintEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Form()
    game.show()
    sys.exit(app.exec_())