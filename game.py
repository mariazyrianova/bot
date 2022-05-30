import requests
import threading
from telebot import types
from menu import Menu, goto_menu

activeGames = {}

def newGame(chatID, newGame):
    activeGames.update({chatID: newGame})
    return newGame

def getGame(chatID):
    return activeGames.get(chatID, None)

def stopGame(chatID):
    activeGames.pop(chatID, None)

class GameRPS:
    values = ["Камень", "Ножницы", "Бумага"]
    name = "Игра Камень-Ножницы-Бумага (Мультиплеер)"
    text_rules = "<b>Победитель определяется по следующим правилам:</b>\n" \
                 "1. Камень побеждает ножницы\n" \
                 "2. Бумага побеждает камень\n" \
                 "3. Ножницы побеждают бумагу\n" \
                 "подробная информация об игре: <a href='https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C,_%D0%BD%D0%BE%D0%B6%D0%BD%D0%B8%D1%86%D1%8B,_%D0%B1%D1%83%D0%BC%D0%B0%D0%B3%D0%B0'>Wikipedia</a>"
    url_picRules = "https://i.ytimg.com/vi/Gvks8_WLiw0/maxresdefault.jpg"

    def __init__(self):
        self.computerChoice = self.__class__.getRandomChoice()

    def newGame(self):
        self.computerChoice = self.__class__.getRandomChoice()

    @classmethod
    def getRandomChoice(cls):
        lenValues = len(cls.values)
        import random
        rndInd = random.randint(0, lenValues - 1)
        return cls.values[rndInd]

    def playerChoice(self, player1Choice):
        winner = None

        code = player1Choice[0] + self.computerChoice[0]
        if player1Choice == self.computerChoice:
            winner = "Ничья!"
        elif code == "КН" or code == "БК" or code == "НБ":
            winner = "Игрок выиграл!"
        else:
            winner = "Компьютер выиграл!"

        return f"{player1Choice} vs {self.computerChoice} = " + winner

class GameRPS_Multiplayer:
    game_duration = 10
    values = ["Камень", "Ножницы", "Бумага"]
    name = "Игра Камень-Ножницы-Бумага (Мультиплеер)"
    text_rules = "<b>Победитель определяется по следующим правилам:</b>\n" \
                 "1. Камень побеждает ножницы\n" \
                 "2. Бумага побеждает камень\n" \
                 "3. Ножницы побеждают бумагу\n" \
                 "подробная информация об игре: <a href='https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C,_%D0%BD%D0%BE%D0%B6%D0%BD%D0%B8%D1%86%D1%8B,_%D0%B1%D1%83%D0%BC%D0%B0%D0%B3%D0%B0'>Wikipedia</a>"
    url_picRules = "https://i.ytimg.com/vi/Gvks8_WLiw0/maxresdefault.jpg"

    class Player:

        def __init__(self, playerID, playerName):
            self.id = playerID
            self.gameMessage = None
            self.name = playerName
            self.scores = 0
            self.choice = None
            self.lastChoice = ""

        def __str__(self):
            return self.name

    def __init__(self, bot, chat_user):
        self.id = chat_user.id
        self.gameNumber = 1
        self.objBot = bot
        self.players = {}
        self.gameTimeLeft = 0
        self.objTimer = None
        self.winner = None
        self.lastWinner = None
        self.textGame = ""
        self.addPlayer(None, "Компьютер")
        self.addPlayer(chat_user.id, chat_user.userName)

    def addPlayer(self, playerID, playerName):
        newPlayer = self.Player(playerID, playerName)
        self.players[playerID] = newPlayer
        if playerID is not None:
            self.startTimer()
            self.setTextGame()
            url_picRules = self.url_picRules
            keyboard = types.InlineKeyboardMarkup()
            list_btn = []
            for keyName in self.values:
                list_btn.append(types.InlineKeyboardButton(text=keyName, callback_data="GameRPSm|Choice-" + keyName + "|" + Menu.setExtPar(self)))
            keyboard.add(*list_btn)
            list_btn = types.InlineKeyboardButton(text="Выход", callback_data="GameRPSm|Exit|" + Menu.setExtPar(self))
            keyboard.add(list_btn)
            gameMessage = self.objBot.send_photo(playerID, photo=url_picRules, caption=self.textGame, parse_mode='HTML', reply_markup=keyboard)
            self.players[playerID].gameMessage = gameMessage
        else:
            newPlayer.choice = self.__class__.getRandomChoice()
        self.sendMessagesAllPlayers([playerID])
        return newPlayer

    def delPlayer(self, playerID):
        print("DEL")
        remotePlayer = self.players.pop(playerID)
        try:
            self.objBot.delete_message(chat_id=remotePlayer.id, message_id=remotePlayer.gameMessage.id)
        except:
            pass
        self.objBot.send_message(chat_id=remotePlayer.id, text="Мне жаль, вас выкинуло из игры!")
        goto_menu(self.objBot, remotePlayer.id, "Игры")
        self.findWiner()
        if len(self.players.values()) == 1:
            stopGame(self.id)

    def getPlayer(self, chat_userID):
        return self.players.get(chat_userID)

    def newGame(self):
        self.gameNumber += 1
        self.lastWinner = self.winner
        self.winner = None
        for player in self.players.values():
            player.lastChoice = player.choice
            if player.id == None:
                player.choice = self.__class__.getRandomChoice()
            else:
                player.choice = None
        self.startTimer()

    def looper(self):
        print("LOOP", self.objTimer)
        if self.gameTimeLeft > 0:
            self.setTextGame()
            self.sendMessagesAllPlayers()
            self.gameTimeLeft -= 1
            self.objTimer = threading.Timer(1, self.looper)
            self.objTimer.start()
            print(self.objTimer.name, self.gameTimeLeft)
        else:
            delList = []
            for player in self.players.values():
                if player.choice is None:
                    delList.append(player.id)
            for idPlayer in delList:
                self.delPlayer(idPlayer)

    def startTimer(self):
        print("START")
        self.stopTimer()
        self.gameTimeLeft = self.game_duration
        self.looper()

    def stopTimer(self):
        print("STOP")
        self.gameTimeLeft = 0
        if self.objTimer is not None:
            self.objTimer.cancel()
            self.objTimer = None

    @classmethod
    def getRandomChoice(cls):
        import random
        lenValues = len(cls.values)
        rndInd = random.randint(0, lenValues-1)
        return cls.values[rndInd]
        return random.choice(cls.values)

    def checkEndGame(self):
        isEndGame = True
        for player in self.players.values():
            isEndGame = isEndGame and player.choice != None
        return isEndGame

    def playerChoice(self, chat_userID, сhoice):
        player = self.getPlayer(chat_userID)
        player.choice = сhoice
        self.findWiner()
        self.sendMessagesAllPlayers()

    def findWiner(self):
        if self.checkEndGame():
            self.stopTimer()
            playersChoice = []
            for player in self.players.values():
                playersChoice.append(player.choice)
            choices = dict(zip(playersChoice, [playersChoice.count(i) for i in playersChoice]))
            if len(choices) == 1 or len(choices) == len(self.__class__.values):
                self.winner = "Ничья"
            else:
                choice1, quantity1 = choices.popitem()
                choice2, quantity2 = choices.popitem()

                code = choice1[0] + choice2[0]
                if quantity1 == 1 and code == "КН" or code == "БК" or code == "НБ":
                    choiceWiner = choice1
                elif quantity2 == 1 and code == "НК" or code == "КБ" or code == "БН":
                    choiceWiner = choice2
                else:
                    choiceWiner = None

                if choiceWiner != None:
                    winner = ""
                    for player in self.players.values():
                        if player.choice == choiceWiner:
                            winner = player
                            winner.scores += 1
                            break
                    self.winner = winner

                else:
                    self.winner = "Ничья"
        self.setTextGame()

        if self.checkEndGame() and len(self.players) > 1:
            self.objTimer = threading.Timer(3, self.newGame)
            self.objTimer.start()

    def setTextGame(self):
        from prettytable import PrettyTable
        mytable = PrettyTable()
        mytable.field_names = ["Игрок", "Счёт", "Выбор", "Результат"]
        for player in self.players.values():
            mytable.add_row([player.name, player.scores, player.lastChoice, "Победитель!" if self.lastWinner == player else ""])

        textGame = self.text_rules + "\n\n"
        textGame += "<code>" + mytable.get_string() + "</code>" + "\n\n"

        if self.winner is None:
            textGame += f"Идёт игра... <b>Осталось времени для выбора: {self.gameTimeLeft}</b>\n"
        elif self.winner == "Ничья":
            textGame += f"<b>Ничья!</b> Пауза 3 секунды..."
        else:
            textGame += f"Выиграл: <b>{self.winner}! Пауза 3 секунды..."

        self.textGame = textGame

    def sendMessagesAllPlayers(self, excludingPlayers=()):
        try:
            for player in self.players.values():
                if player.id is not None and player.id not in excludingPlayers:
                    textIndividual = f"\n Ваш выбор: {player.choice}, ждём остальных!" if player.choice is not None else "\n"
                    self.objBot.edit_message_caption(chat_id=player.id, message_id=player.gameMessage.id, caption=self.textGame + textIndividual, parse_mode='HTML',
                                                     reply_markup=player.gameMessage.reply_markup)
        except:
            pass

def callback_worker(bot, cur_user, cmd, par, call):
    chat_id = call.message.chat.id
    message_id = call.message.id

    if cmd == "newGame":
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        bot.delete_message(chat_id, message_id)
        newGame(chat_id, GameRPS_Multiplayer(bot, cur_user))
        bot.answer_callback_query(call.id)

    elif cmd == "Join":
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        bot.delete_message(chat_id, message_id)
        gameRSPMult = Menu.getExtPar(par)
        if gameRSPMult is None:
            return
        else:
            gameRSPMult.addPlayer(cur_user.id, cur_user.userName)
        bot.answer_callback_query(call.id)

    elif cmd == "Exit":
        bot.delete_message(chat_id, message_id)
        gameRSPMult = Menu.getExtPar(par)
        if gameRSPMult is not None:
            gameRSPMult.delPlayer(cur_user.id)
        goto_menu(bot, chat_id, "Игры")
        bot.answer_callback_query(call.id)

    elif "Choice-" in cmd:
        gameRSPMult = Menu.getExtPar(par)
        if gameRSPMult is None:
            bot.delete_message(chat_id, message_id)
        else:
            choice = cmd[7:]
            gameRSPMult.playerChoice(cur_user.id, choice)
        bot.answer_callback_query(call.id)

def get_text_messages(bot, cur_user, message):
    chat_id = message.chat.id
    ms_text = message.text

    if ms_text in GameRPS.values:
        gameRSP = getGame(chat_id)
        if gameRSP is None:
            goto_menu(bot, chat_id, "Выход")
            return
        text_game = gameRSP.playerChoice(ms_text)
        bot.send_message(chat_id, text=text_game)
        gameRSP.newGame()

    elif ms_text == "Игра КНБ-MP":
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Создать новую игру", callback_data="GameRPSm|newGame")
        keyboard.add(btn)
        numGame = 0
        for game in activeGames.values():
            if type(game) == GameRPS_Multiplayer:
                numGame += 1
                btn = types.InlineKeyboardButton(
                    text="Игра КНБ-" + str(numGame) + " игроков: " + str(len(game.players)),
                    callback_data="GameRPSm|Join|" + Menu.setExtPar(game))
                keyboard.add(btn)
        btn = types.InlineKeyboardButton(text="Вернуться", callback_data="GameRPSm|Exit")
        keyboard.add(btn)

        bot.send_message(chat_id, text=GameRPS_Multiplayer.name, reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(chat_id, "Вы хотите начать новую игру, или присоединиться к существующей?",
                         reply_markup=keyboard)
if __name__ == "__main__":
    print("Этот код должен использоваться ТОЛЬКО в качестве модуля!")