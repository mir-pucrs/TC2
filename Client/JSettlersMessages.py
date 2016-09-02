'''
    NEWCHANNEL           = 1001
    MEMBERS              = 1002
    CHANNELS             = 1003
    JOIN                 = 1004
    TEXTMSG              = 1005
    LEAVE                = 1006
    DELETECHANNEL        = 1007
    LEAVEALL             = 1008
    PUTPIECE             = 1009
    GAMETEXTMSG          = 1010
    LEAVEGAME            = 1011
    SITDOWN              = 1012
    JOINGAME             = 1013
    BOARDLAYOUT          = 1014
    DELETEGAME           = 1015
    NEWGAME              = 1016
    GAMEMEMBERS          = 1017
    STARTGAME            = 1018
    GAMES                = 1019
    JOINAUTH             = 1020
    JOINGAMEAUTH         = 1021
    IMAROBOT             = 1022
    JOINGAMEREQUEST      = 1023
    PLAYERELEMENT        = 1024
    GAMESTATE            = 1025
    TURN                 = 1026
    SETUPDONE            = 1027
    DICERESULT           = 1028
    DISCARDREQUEST       = 1029
    ROLLDICEREQUEST      = 1030
    ROLLDICE             = 1031
    ENDTURN              = 1032
    DISCARD              = 1033
    MOVEROBBER           = 1034
    CHOOSEPLAYER         = 1035
    CHOOSEPLAYERREQUEST  = 1036
    REJECTOFFER          = 1037
    CLEAROFFER           = 1038
    ACCEPTOFFER          = 1039
    BANKTRADE            = 1040
    MAKEOFFER            = 1041
    CLEARTRADEMSG        = 1042
    BUILDREQUEST         = 1043
    CANCELBUILDREQUEST   = 1044
    BUYCARDREQUEST       = 1045
    DEVCARD              = 1046
    DEVCARDCOUNT         = 1047
    SETPLAYEDDEVCARD     = 1048
    PLAYDEVCARDREQUEST   = 1049
    DISCOVERYPICK        = 1052
    MONOPOLYPICK         = 1053
    FIRSTPLAYER          = 1054
    SETTURN              = 1055
    ROBOTDISMISS         = 1056
    POTENTIALSETTLEMENTS = 1057
    CHANGEFACE           = 1058
    REJECTCONNECTION     = 1059
    LASTSETTLEMENT       = 1060
    GAMESTATS            = 1061
    BCASTTEXTMSG         = 1062
    RESOURCECOUNT        = 1063
    ADMINPING            = 1064
    ADMINRESET           = 1065
    LONGESTROAD          = 1066
    LARGESTARMY          = 1067
    SETSEATLOCK          = 1068
    STATUSMESSAGE        = 1069
    CREATEACCOUNT        = 1070
    UPDATEROBOTPARAMS    = 1071
    SERVERPING           = 9999
'''

g_harbour_to_resource = {

    "3For1"       : 6,
    "ClayHarbor"  : 1,
    "OreHarbor"   : 2,
    "SheepHarbor" : 3,
    "GrainHarbor" : 4,
    "LumberHarbor": 5
}

g_board_indicators = {

    0: 'Desert',
    1: 'Clay',
    2: 'Ore',
    3: 'Sheep',
    4: 'Grain',
    5: 'Lumber',
    6: 'EmptySea',

    7: '3For1',
    8: '3For1',
    9: '3For1',
    10: '3For1',
    11: '3For1',
    12: '3For1',

    17: 'ClayHarbor',
    18: 'OreHarbor',
    19: 'SheepHarbor',
    20: 'GrainHarbor',
    21: 'LumberHarbor',

    33: 'ClayHarbor',
    34: 'OreHarbor',
    35: 'SheepHarbor',
    36: 'GrainHarbor',
    37: 'LumberHarbor',

    49: 'ClayHarbor',
    50: 'OreHarbor',
    51: 'SheepHarbor',
    52: 'GrainHarbor',
    53: 'LumberHarbor',

    65: 'ClayHarbor',
    66: 'OreHarbor',
    67: 'SheepHarbor',
    68: 'GrainHarbor',
    69: 'LumberHarbor',

    81: 'ClayHarbor',
    82: 'OreHarbor',
    83: 'SheepHarbor',
    84: 'GrainHarbor',
    85: 'LumberHarbor',

    97: 'ClayHarbor',
    98: 'OreHarbor',
    99: 'SheepHarbor',
    100: 'GrainHarbor',
    101: 'LumberHarbor'
}

g_harbors = {

    '3for1'       : [ 7,  8,  9, 10, 11, 12 ],
    'ClayHarbor'  : [17, 33, 49, 65, 81, 97 ],
    'OreHarbor'   : [18, 34, 50, 66, 82, 98 ],
    'SheepHarbor' : [19, 35, 51, 67, 83, 99 ],
    'GrainHarbor' : [20, 36, 52, 68, 84, 100],
    'LumberHarbor': [21, 37, 53, 69, 85 ,101]
}

g_messageNumberToGameNumber = {

   -1 :  0,
    0 :  2,
    1 :  3,
    2 :  4,
    3 :  5,
    4 :  6,
    5 :  8,
    6 :  9,
    7 : 10,
    8 : 11,
    9 : 12
}

g_stateIdToName = {

      '0'   : 'NEW'                   # Brand new game
    , '1'   : 'READY'                 # Ready to start playing
    , '5'   : 'START1A'               # Players place 1st settlement
    , '6'   : 'START1B'               # Players place 1st road
    , '10'  : 'START2A'               # Players place 2nd settlement
    , '11'  : 'START2B'               # Players place 2nd road
    , '15'  : 'PLAY'                  # Play continues normally
    , '20'  : 'PLAY1'                 # Done rolling
    , '30'  : 'PLACING_ROAD'
    , '31'  : 'PLACING_SETTLEMENT'
    , '32'  : 'PLACING_CITY'
    , '33'  : 'PLACING_ROBBER'
    , '40'  : 'PLACING_FREE_ROAD1'    # Player is placing first road
    , '41'  : 'PLACING_FREE_ROAD2'    # Player is placing second road
    , '50'  : 'WAITING_FOR_DISCARDS'  # Waiting for players to discard
    , '51'  : 'WAITING_FOR_CHOICE'    # Waiting for player to choose a player
    , '52'  : 'WAITING_FOR_DISCOVERY' # Waiting for player to choose 2 resources
    , '53'  : 'WAITING_FOR_MONOPOLY'  # Waiting for player to choose a resource
    , '1000': 'OVER'                  # The game is over
}

def g_MessageNumberToGameNumber(messageNumber):

    return g_messageNumberToGameNumber[messageNumber]

class Message:
    def __init__(self):
        pass

    def to_cmd(self):
        pass

    def values(self):
        vars = filter(lambda x: x not in [
                                "__doc__", "__init__", "__module__"
                              , "to_cmd", "parse", "values", "id", "etype"]
                     , dir(self))
        return dict([(name, getattr(self, name)) for name in vars])

    @staticmethod
    def parse(text):
        return None

class ChannelsMessage(Message):
    id = 1003
    def __init__(self, channels):
        self.channels = channels

    def to_cmd(self):
        return "{0}|{1}".format(self.id, ",".join(self.channels))

    @staticmethod
    def parse(text):
        channels = filter(None, text.split(","))
        return ChannelsMessage(channels)

class SitDownMessage(Message):
    id = 1012

    def __init__(self, game, nickname, playernum, isrobot):
        self.game = game
        self.nickname = nickname
        self.playernum = playernum
        self.isrobot = isrobot

    def to_cmd(self):
        return "{0}|{1},{2},{3},{4}".format(self.id, self.game, self.nickname
                                            , self.playernum, str(self.isrobot).lower())

    @staticmethod
    def parse(text):
        data = text.split(",")
        gn = data[0]  # game name
        nn = data[1]  # nick name
        pn = data[2]  # seat number
        rf = False if data[3] == "false" else True  # is robot
        return SitDownMessage(gn, nn, pn, rf)

class JoinGameMessage(Message):
    id = 1013
    def __init__(self, nickname, password, host, game):
        self.nickname = nickname
        self.password = password
        self.host = host
        self.game = game

    def to_cmd(self):
        password = "\t" if self.password == "" else self.password
        return "{0}|{1},{2},{3},{4}".format(self.id, self.nickname, password
                                        ,self.host, self.game)

    @staticmethod
    def parse(text):
        data = text.split(",")
        data[1] = "" if data[1] == "\t" else ""
        return JoinGameMessage(*data)

class BoardLayoutMessage(Message):
    id = 1014

    def __init__(self, gameName, hexes, numbers, robberPos):
        self.gameName = gameName
        self.hexes = hexes
        self.numbers = numbers
        self.robberpos = robberPos

    def to_cmd(self):
        return "{0}|{1},{2},{3},{4}".format(self.id, self.game
                                            , ",".join(map(str, self.hexes))
                                            , ",".join(map(str, self.numbers))
                                            , self.robberpos)

    @staticmethod
    def parse(text):
        data = text.split(",")
        gameName = data[0]
        hexes = map(int, data[1:38])
        numbers = map(int, data[38:38 + 37])
        robberpos = int(data[-1])
        return BoardLayoutMessage(gameName, hexes, numbers, robberpos)

class NewGameMessage(Message):
    id = 1016

    def __init__(self, gameName):
        self.gameName = gameName

    def to_cmd(self):
        return "{0}|{1}".format(self.id, self.gameName)

    @staticmethod
    def parse(text):
        return NewGameMessage(text)

class StartGameMessage(Message):
    id = 1018

    def __init__(self, game):
        self.game = game

    def to_cmd(self):
        return "{0}|{1}".format(self.id, self.game)

    @staticmethod
    def parse(text):
        return StartGameMessage(text)

class GamesMessage(Message):
    id = 1019

    def __init__(self, games):
        self.games = games

    def to_cmd(self):
        return "{0}|{1}".format(self.id, ",".join(self.games))

    @staticmethod
    def parse(text):
        games = filter(None, text.split(","))
        return GamesMessage(games)

class JoinGameAuthMessage(Message):
    id = 1021

    def __init__(self, gameName):
        self.gameName = gameName

    def to_cmd(self):
        return "{0}|{1}".format(self.id, self.gameName)

    @staticmethod
    def parse(text):
        return JoinGameAuthMessage(text)

class GameStateMessage(Message):
    id = 1025

    def __init__(self, gameName, state):
        self.gameName   = gameName
        self.state      = state
        self.stateName  = g_stateIdToName[state]

    def to_cmd(self):
        return "{0}|{1},{2}".format(self.id, self.gameName, self.state)

    @staticmethod
    def parse(text):
        g, s = text.split(",")
        return GameStateMessage(g, s)

class SetTurnMessage(Message):
    id = 1055

    def __init__(self, gameName, seatnum):
        self.gameName = gameName
        self.seatnum  = seatnum

    def to_cmd(self):
        return "{0}|{1},{2}".format(self.id, self.gameName, self.seatnum)

    @staticmethod
    def parse(text):
        gameName, seat = text.split(",")
        return SetTurnMessage(gameName, int(seat))

class ChangeFaceMessage(Message):
    id = 1058

    def __init__(self, gameName, playerNum, faceId):
        self.gameName = gameName
        self.playerNum = playerNum
        self.faceId = faceId

    def to_cmd(self):
        return "{0}|{1},{2},{3}".format(self.id, self.gameName, self.playerNum, self.faceId)

    @staticmethod
    def parse(text):
        g, pn, fi = text.split(",")
        return ChangeFaceMessage(g, pn, fi)

class LongestRoadMessage(Message):
    id = 1066

    def __init__(self, gameName, playernum):
        self.gameName = gameName
        self.playernum = playernum

    def to_cmd(self):
        return "{0}|{1},{2}".format(self.id, self.gameName, self.playernum)

    @staticmethod
    def parse(text):
        gameName, pn = text.split(",")
        return LongestRoadMessage(gameName, int(pn))

class LargestArmyMessage(Message):
    id = 1067

    def __init__(self, gameName, playernum):
        self.gameName = gameName
        self.playernum = playernum

    def to_cmd(self):
        return "{0}|{1},{2}".format(self.id, self.gameName, self.playernum)

    @staticmethod
    def parse(text):
        gameName, pn = text.split(",")
        return LargestArmyMessage(gameName, int(pn))

class SetSeatLockMessage(Message):
    id = 1068

    def __init__(self, gameName, seatNumber, isLocked):
        self.gameName   = gameName
        self.seatNumber = seatNumber
        self.isLocked   = isLocked

    def to_cmd(self):
        return "{0}|{1},{2},{3}".format(self.id,
                    self.game, self.seatNumber, self.isLocked)

    @staticmethod
    def parse(text):
        gameName, seatNumber, isLocked = text.split(",")
        return SetSeatLockMessage(gameName, int(seatNumber), bool(isLocked))

class StatusMessageMessage(Message):
    id = 1069

    def __init__(self, status):
        self.status = status

    def to_cmd(self):
        return "{0}|{1}".format(self.id, self.status)

    @staticmethod
    def parse(text):
        return StatusMessageMessage(text)