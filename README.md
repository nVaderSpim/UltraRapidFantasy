# UltraRapidFantasy
Entry into the League of Legends API Challenge: ULTRA RAPID FANTASY.
This application uses Python 2.7.9 and PySide 1.2.2.

**Ultra Rapid Fantasy uses the Riot API to get information about League of Legends URF games. Because URF is no longer playable, this game has to grab info from the same pool of old games and will therefore be fairly predictable!**

Note: This application requires a script called APIKey.py which contains a Riot Games API key (as a string) named API_KEY.
I've withheld my own API key for security's sake.

To start the application, run LoLUltraRapidFantasy.py in the same directory as "background.png," "result_background.png", and "ChampSelect.wav".  It will create a directory named Icons and download a .png icon for each of the current League of Legends champions.  Currently, Bard's icon does not seem to be valid.  This repository includes a Bard.png which can be manually put into the Icons folder to correct this.

"Ultra Rapid Fantasy is the superhero given its powers when League of Legends Champion Select was bitten by a radioactive Fantasy LCS.  Two players (local on one machine only) will pick and ban champions in exactly the same manner as League of Legends normal or ranked draft mode.  After the pick/ban phase is complete, the application will search through URF games until it has either found stats for each selected champion, or ran out of games.  Champions will be scored with the same point values as Fantasy LCS: 2 per kill, 1.5 per assist, -.5 per death, .01 per cs, 2 points for getting at least 10 kills or assists, and 2, 5, and 10 for triple, quadra, and penta kills, respectively.  The winning team earns the accolade "ULTRA RAPIDLY FANTASTIC" and the loser... doesn't."

For those unfamiliar with League of Legends draft mode, the game is played like this:
Click a champion icon/button in the scroll area in the center of the window to select it. Player 1 and player 2 will alternate for the first six selections (three each).  These champions will be banned, and cannot be picked by either player.  Afterward, player 1 will select the first remaining champion for his/her team (also removing it from the selection list).  Player 2 will then pick two champions consecutively, followed by two more champions for player 1 (three team members, five picks overall), two more for player 2, two more for player 1 (full team, nine picks overall), and one last pick for player 2.

At this point, data will be pulled from the Riot API to score the game.  After data collection is completed, a table will be shown to display each champion's scores.  Upon closing the table window, a message box will display the team's final scores and declare the winner, at which point the players can choose to start a new game or exit.

This was a pretty fun project, I enjoyed the opportunity to get more familiar with Python.  I hope you enjoy it!  Demonstration video available at: https://www.youtube.com/watch?v=tmqzwzZ20K0

Ultra Rapid Fantasy isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.