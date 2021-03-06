from AgentRandom import *
from datetime import datetime
from datetime import timedelta
import multiprocessing as mp
import threading
import cPickle

# * OPTION (for performance)*#    implement nodes as a tuple (worse to read/understand)
# MCTS TREE NODE STRUCTURE:
# (gameState, action     , Q-value , N-value     , PARENT     , CHILDREN)
#  currState, from parent, reward  , n. of visits, parent node, children
class MCTSNode:

    def __init__(self, player, state, action, qValue, nValue, parent, children, actionsFunction, virtualWins=False):

        self.actingPlayer    = player
        self.gameState       = cPickle.dumps(state, -1) # current gameState
        self.action          = action  # action that led to this state
        self.QValue          = qValue  # node estimated reward value
        self.NValue          = nValue  # number of visits
        self.parent          = parent  # parent
        self.children        = children  # children
        # All-Moves-As-First variables
        self.AMAFQValue      = [0, 0, 0, 0]
        self.AMAFNValue      = 0
        self.QValueHist      = []
        self.saveNodeValue   = 20

        # VIRTUAL WINS
        if virtualWins:
            self.saveNodeValue = 25
            if self.action is not None:
                if self.action.type == 'BuildSettlement':
                    self.QValue[self.actingPlayer] = 20
                    self.NValue = 20
                elif self.action.type == 'BuildCity':
                    self.QValue[self.actingPlayer] = 10
                    self.NValue = 10

        isRootNode = False
        if parent is None:
            isRootNode = True

        # keep possible actions list
        self.possibleActions = actionsFunction(state,
                                               state.players[state.currPlayer],
                                               False,
                                               isRootNode)

        # keep some gameState stuff before pickling
        self.currentPlayer   = state.currPlayer
        self.isTerminal      = state.IsTerminal()

    def GetState(self):
        if self.NValue < self.saveNodeValue:
            return cPickle.loads(self.gameState)
        else:
            return self.gameState

    def GetStateCopy(self):
        if self.NValue < self.saveNodeValue:
            return cPickle.loads(self.gameState)
        else:
            return cPickle.loads(cPickle.dumps(self.gameState, -1))

    def UpdateNValue(self):
        self.NValue += 1
        if self.NValue == self.saveNodeValue:
            self.gameState = cPickle.loads(self.gameState)

    def UpdateQValue(self, addValue):
        self.QValueHist.append(addValue)
        self.QValue += addValue

    def __eq__(self, other):
        if other is None:
            if self is None:
                return True
            return False
        return self.__dict__ == other.__dict__

class AgentMCTS(AgentRandom):

    DiceProbability = \
    {
        2: listm([0.03, 0.03, 0.03, 0.03, 0.03, 0.03]),
        3: listm([0.06, 0.06, 0.06, 0.06, 0.06, 0.06]),
        4: listm([0.08, 0.08, 0.08, 0.08, 0.08, 0.08]),
        5: listm([0.11, 0.11, 0.11, 0.11, 0.11, 0.11]),
        6: listm([0.14, 0.14, 0.14, 0.14, 0.14, 0.14]),
        7: listm([0.17, 0.17, 0.17, 0.17, 0.17, 0.17]),
        8: listm([0.14, 0.14, 0.14, 0.14, 0.14, 0.14]),
        9: listm([0.11, 0.11, 0.11, 0.11, 0.11, 0.11]),
        10: listm([0.08, 0.08, 0.08, 0.08, 0.08, 0.08]),
        11: listm([0.06, 0.06, 0.06, 0.06, 0.06, 0.06]),
        12: listm([0.03, 0.03, 0.03, 0.03, 0.03, 0.03])
    }

    TradingTypes = ['Simple', 'Optimistic', None]

    def __init__(self, name, seatNumber, choiceTime = 10.0, simulationCount = None, explorationValue = 0.25,
                 multiThreading = False, numberOfThreads = 0, preSelectMode = 'citiesOverSettlements',
                 simPreSelectMode = None, trading = None, virtualWins = False):

        super(AgentMCTS, self).__init__(name, seatNumber)

        self.choiceTime          = choiceTime
        self.agentName           = "MONTE CARLO TREE SEARCH : {0} sec, {1} sims".format(choiceTime, simulationCount)
        self.simulationCounter   = 0
        self.maxSimulations      = simulationCount
        self.movesToDo           = [] #move buffer
        self.multiTreading       = multiThreading
        self.numberOfThreads     = numberOfThreads
        self.preSelectMode       = preSelectMode
        self.simPreSelectMode    = simPreSelectMode
        self.trading             = trading
        self.explorationValue    = explorationValue
        self.virtualWins         = virtualWins

        # TREE BUFFER IS CURRENTLY A BAD IDEA MAINLY BECAUSE OF THE WAY WE STORE PLAYERS AND GAMESTATES, IT WOULD TAKE TOO MUCH SPACE
        # ALSO, WE WOULD HAVE TO CHANGE TOO MUCH STUFF
        #self.lastMctsRootNode    = None #tree buffer

    def DoMove(self, game):

        copyState = None

        # SERVER SPECIAL CASES:
        # If its not our turn and the server is not waiting for discards...
        if game.gameState.currPlayer != self.seatNumber and \
            game.gameState.currState != "WAITING_FOR_DISCARDS":
            return None
        #If the server is waiting for discards, respond, if needed...
        if game.gameState.currState == "WAITING_FOR_DISCARDS":
            copyState = cPickle.loads(cPickle.dumps(game.gameState, -1))
            copyState.playerBeforeDiscards = copyState.currPlayer
            copyState.currPlayer = self.seatNumber

        # If we already done our setup phase, ignore repeated message (strange bug from server)...
        if (game.gameState.currState == "START1A" and self.firstSettlementBuild) or \
           (game.gameState.currState == "START1B" and self.firstRoadBuild) or \
           (game.gameState.currState == "START2A" and self.secondSettlementBuild) or \
           (game.gameState.currState == "START2B" and self.secondRoadBuild):
            return None

        # SPECIAL CASE -> WE JUST GOT OUR TURN AND CAN CLEAR THE "BUFFER"...
        if game.gameState.currState == "PLAY":
            #print("empty buffer! -> PLAY")
            self.movesToDo = []
            self.tradeLock = False

        # IF I HAVE MOVES IN MY "BUFFER", RETURN THOSE...
        if len(self.movesToDo) > 0:

            print("Accessed Move Buffer = {0}".format(self.movesToDo))

            action = self.movesToDo[0]  # get first element
            # SPECIAL CASE -> MONOPOLY ACTION - we don't know what resources will come from the server
            # SPECIAL CASE -> CHOOSEPLAYER ACTION - we don't know what resources will come from the server
            if (isinstance(action, UseDevelopmentCardAction) and \
                action.index == g_developmentCards.index('MONOPOLY')) or \
               (isinstance(action, UseDevelopmentCardAction) and \
                action.index == g_developmentCards.index('YEAR_OF_PLENTY')) or \
                isinstance(action, ChoosePlayerToStealFromAction) or \
                isinstance(action, PlaceRobberAction) or \
                isinstance(action, DiscardResourcesAction):
                print("Clear buffer -> MONOPOLY OR CHOOSEPLAYER")
                self.movesToDo = []
            else:
                self.movesToDo = self.movesToDo[1:]  # remove first element

            print("BUFFER ACTION = \n{0}".format(action))

            return action

        self.simulationCounter = 0

        if copyState is None:
            state = cPickle.loads(cPickle.dumps(game.gameState, -1))
        else:
            state = cPickle.loads(cPickle.dumps(copyState, -1))

        AgentMCTS.PrepareGameStateForSimulation(state)

        if self.multiTreading:

            numCores = self.numberOfThreads if self.numberOfThreads > 0 else mp.cpu_count()

            if self.maxSimulations is not None:
                coreSimCount = int(math.floor(self.maxSimulations / numCores))
            else:
                coreSimCount = None

            coreTime = int(math.floor(self.choiceTime / numCores))
            ct = timedelta(seconds=coreTime)

            manager     = mp.Manager()
            resultNodes = manager.list(range(numCores))

            rootNode = MCTSNode(player=self.seatNumber,
                                state=state,
                                action=None,
                                qValue=listm(0 for i in range(len(state.players))),
                                nValue=0,
                                parent=None,
                                children=[],
                                actionsFunction=self.GetPossibleActions,
                                virtualWins=self.virtualWins)

            if rootNode.possibleActions is None:
                print("MCTS ERROR! POSSIBLE ACTIONS FROM ROOT NODE ARE NONE!!!!")
                return None

            elif len(rootNode.possibleActions) == 1:
                return rootNode.possibleActions[0]

            elif len(rootNode.possibleActions) <= 0:
                print("MCTS ERROR! NO POSSIBLE ACTIONS FROM ROOT NODE!")
                return None

            processes = [mp.Process(target=self.MonteCarloTreeSearch, args=(state, ct, coreSimCount, True, i, resultNodes,
                                                                            cPickle.loads(cPickle.dumps(rootNode, -1))))
                         for i in range(numCores)]  # I am running as many processes as CPU my machine has (is this wise?).
            for proc in processes:
                proc.start()
            for proc in processes:
                proc.join()

            while len(rootNode.possibleActions) > 0:
                self.Expand(rootNode)

            for node in resultNodes:
                rootNode.NValue += node.NValue
                for childNode in node.children:
                    for rootChild in rootNode.children:
                        if childNode.action == rootChild.action:
                            rootChild.QValueHist += childNode.QValueHist
                            rootChild.QValue     += childNode.QValue
                            rootChild.NValue     += childNode.NValue

            self.movesToDo = []

            for childNode in rootNode.children:
                if childNode.NValue <= 0:
                    rootNode.children.remove(childNode)

            bestNode = self.BestChild(rootNode, 0, rootNode.NValue)

            return bestNode.action

        else:

            action = self.MonteCarloTreeSearch(state, timedelta(seconds=self.choiceTime), self.maxSimulations)

            # SPECIAL CASE -> MONOPOLY ACTION - we don't know what resources will come from the server
            # SPECIAL CASE -> CHOOSEPLAYER ACTION - we don't know what resources will come from the server
            if (isinstance(action, UseDevelopmentCardAction) and \
                action.index == g_developmentCards.index('MONOPOLY')) or \
                (isinstance(action, UseDevelopmentCardAction) and \
                action.index == g_developmentCards.index('YEAR_OF_PLENTY')) or \
                isinstance(action, ChoosePlayerToStealFromAction) or \
                isinstance(action, PlaceRobberAction) or \
                isinstance(action, DiscardResourcesAction):
                print("empty buffer! -> MONOPOLY OR CHOOSEPLAYER")
                self.movesToDo = []

        return action

    def MonteCarloTreeSearch(self, gameState, maxDuration, simulationCount,
                             parallel = False, processIndex = None, processList = None, rootNode = None):

        if rootNode is None:
            rootNode = MCTSNode(player=self.seatNumber,
                                state=gameState,
                                action=None,
                                qValue=listm(0 for i in range(len(gameState.players))),
                                nValue=0,
                                parent=None,
                                children=[],
                                actionsFunction=self.GetPossibleActions,
                                virtualWins=self.virtualWins)

        # print("GAME STATE      : {0}".format(gameState.currState))
        # print("POSSIBLE ACTIONS: {0}".format(rootNode.possibleActions))
        #
        # print("RESOURCES = BRICK: {0}\n"
        #       "              ORE: {1}\n"
        #       "             WOOL: {2}\n"
        #       "            GRAIN: {3}\n"
        #       "           LUMBER: {4}".format(
        #     self.resources[0],
        #     self.resources[1],
        #     self.resources[2],
        #     self.resources[3],
        #     self.resources[4]
        # ))
        #
        # if sum(self.developmentCards) > 0:
        #     print("DEVELOPMENT CARDS = KNIGHT:        {0}\n"
        #           "                    ROAD_BUILDING: {1}\n"
        #           "                    YEAR_OF_PLENTY:{2}\n"
        #           "                    MONOPOLY:      {3}\n"
        #           "                    VICTORY_POINT: {4}".format(
        #         self.developmentCards[0],
        #         self.developmentCards[1],
        #         self.developmentCards[2],
        #         self.developmentCards[3],
        #         self.developmentCards[4]
        #     ))

        if rootNode.possibleActions is None:
            print("MCTS ERROR! POSSIBLE ACTIONS FROM ROOT NODE ARE NONE!!!!")
            return None

        elif len(rootNode.possibleActions) == 1:
            return rootNode.possibleActions[0]

        elif len(rootNode.possibleActions) <= 0:
            print("MCTS ERROR! NO POSSIBLE ACTIONS FROM ROOT NODE!")
            return None

        msg = "Player {0} is a {1} agent".format(self.name,
                                                 self.agentName) \
               + "\n his resources are: ({0})".format(g_resources) \
               + "\n RESOURCES       = {0} ".format(self.resources) \
               + "\n his devcards are: ({0})".format(g_developmentCards) \
               + "\n DEV CARDS       = {0} ".format(self.developmentCards)

        print(msg)

        startTime = datetime.utcnow()

        # if a simulation count is given, ignore time constraints
        def Condition():
            if simulationCount is None:
                return (datetime.utcnow() - startTime) < maxDuration
            else:
                return self.simulationCounter < simulationCount

        while Condition():

            nextNode = self.TreePolicy(rootNode, rootNode.NValue)
            reward   = self.SimulationPolicy(nextNode.GetStateCopy())
            self.BackUp(nextNode, reward)
            self.simulationCounter += 1

        print("TOTAL SIMULATIONS = {0}".format(self.simulationCounter))
        print("TOTAL TIME        = {0}".format((datetime.utcnow() - startTime)))

        print("POSSIBLE MOVE COUNT = {0}".format(len(rootNode.children)))
        print("POSSIBLE MOVES = {0}".format([child.action for child in rootNode.children]))

        best = self.BestChild(rootNode, 0, rootNode.NValue)

        print("CHOSEN ACTION = \n{0}".format(best.action))

        # KEEP FUTURE ACTIONS IN A "BUFFER"...
        # IF WE ARE CHOOSING A PLAYER TO STEAL FROM, DON'T KEEP BUFFER -> WE DON'T KNOW WHAT RESOURCE WE WILL STEAL!
        if not parallel:
            if gameState.currState != 'WAITING_FOR_CHOICE':

                bestChild = self.BestChild(best, 0, rootNode.NValue)
                while bestChild is not None and \
                    bestChild.actingPlayer == self.seatNumber and \
                        not bestChild.isTerminal:
                    self.movesToDo.append(bestChild.action)
                    bestChild = self.BestChild(bestChild, 0, rootNode.NValue)

                    print("Created Move Buffer = {0}".format(self.movesToDo))

            return best.action

        else:
            #movesToDo = []
            #if gameState.currState != 'WAITING_FOR_CHOICE':
            #    bestChild = self.BestChild(best, 0, rootNode.NValue)
            #    while bestChild is not None and \
            #                    bestChild.actingPlayer == self.seatNumber and \
            #            not bestChild.isTerminal:
            #        movesToDo.append(bestChild.action)
            #        bestChild = self.BestChild(bestChild, 0, rootNode.NValue)
            #
            #        print("Created Move Buffer = {0}".format(self.movesToDo))

            processList[processIndex] = rootNode

            #processList[processIndex] = (
            #best.action, movesToDo, (float(best.QValue[self.seatNumber]) / float(best.NValue)))

    def TreePolicy(self, node, totalNValue):

        while node.isTerminal is False and node.possibleActions is not None:
            # There are still actions to try in this node...
            if len(node.possibleActions) > 0:
                return self.Expand(node)

            node = self.BestChild(node, self.explorationValue, totalNValue)

        return node

    def Expand(self, node):

        chosenAction = random.choice(node.possibleActions)

        node.possibleActions.remove(chosenAction)

        nextGameState = node.GetStateCopy()

        chosenAction.ApplyAction(nextGameState)

        childNode = MCTSNode(player=node.currentPlayer,
                             state=nextGameState,
                             action=chosenAction,
                             qValue=listm(0 for i in range(len(node.QValue))),
                             #qValue=estimatedQValues,
                             nValue=0,
                             parent=node,
                             children=[],
                             actionsFunction=self.GetPossibleActions,
                             virtualWins=self.virtualWins)

        node.children.append(childNode)

        return childNode

    def BestChild(self, node, explorationValue, totalNValue, player=None):

        if len(node.children) <= 0:
            return None

        tgtPlayer = node.currentPlayer if player is None else player

        # Returns the Child Node with the max 'Q-Value'
        return max(node.children, key=lambda child: child.QValue[tgtPlayer]/child.NValue)

    def SimulationPolicy(self, gameState):

        while not gameState.IsTerminal():

            possibleActions = self.GetPossibleActions(gameState,
                                                      gameState.players[gameState.currPlayer],
                                                      atRandom=True)
            #if possibleActions is None:
            #    print("ERROR!")
            #    possibleActions = self.GetPossibleActions(gameState,
            #                                              gameState.players[gameState.currPlayer],
            #                                              atRandom=True)

            if len(possibleActions) > 1:
                action = random.choice(possibleActions)
            else:
                action = possibleActions[0]

            action.ApplyAction(gameState)

        return self.Utility(gameState)

    def BackUp(self, node, reward):
        while node is not None:
            node.UpdateNValue()
            node.UpdateQValue(reward)
            node = node.parent

    def Utility(self, gameState):

        vp = listm(0 for i in range(len(gameState.players)))

        vp[gameState.winner] += 1

        return vp

    @staticmethod
    def PrepareGameStateForSimulation(gameState):

        for player in gameState.players:

            if player is None:
                continue

            quantity = player.resources[g_resources.index('UNKNOWN')]

            if quantity > 0:

                player.resources[g_resources.index('UNKNOWN')] = 0

                resources = [0, 0, 0, 0, 0, 0]

                for i in range(0, quantity):
                    resources[random.randint(0, 4)] += 1

                player.resources = player.resources + resources

    def GetPossibleActions(self, gameState, player, atRandom=False, fromRootNode=False):

        if not gameState.setupDone:
            return self.GetPossibleActions_SetupTurns(gameState, player)
        elif gameState.currState == "PLAY":
            if fromRootNode or atRandom:
                return super(AgentMCTS, self).GetPossibleActions_PreDiceRoll(player)
            else:
                return self.GetPossibleActions_PreDiceRoll(player)
        elif gameState.currState == "PLAY1":
            if atRandom:
                return [self.GetRandomAction_RegularTurns(gameState, player, self.simPreSelectMode)]
            else:
                return self.GetPossibleActions_RegularTurns(gameState, player, self.preSelectMode, fromRootNode)
        else:
            return self.GetPossibleActions_SpecialTurns(gameState, player, atRandom)

    def GetPossibleBankTrades(self, gameState, player):

        if player is None:
            player = self

        possibleTrades = []

        for i in range(5):
            if int(player.resources[i] / self.tradeRates[i]) > 0:
                give = [0, 0, 0, 0, 0]
                give[i] = self.tradeRates[i]
                for j in range(1, 5):
                    get = [0, 0, 0, 0, 0]
                    index = (i + j) % 5
                    get[index] = 1
                    possibleTrades.append(BankTradeOfferAction(player.seatNumber, give, get))

        return possibleTrades

    def ChooseRobberPosition(self, gameState, player):

        playerHexes = []
        for s in player.settlements:
            playerHexes += gameState.boardNodes[s].adjacentHexes
        for c in player.cities:
            playerHexes += gameState.boardNodes[c].adjacentHexes

        def CheckHex(hexPosition):

            if hexPosition in playerHexes or \
               hexPosition == gameState.robberPos:
                return False
            return True

        possiblePositions = []

        for otherPlayer in gameState.players:

            if otherPlayer.seatNumber == player.seatNumber:
                continue

            for settlementPos in otherPlayer.settlements:
                for hexPos in gameState.boardNodes[settlementPos].adjacentHexes:
                    if hexPos in gameState.possibleRobberPos and CheckHex(hexPos):
                        possiblePositions.append(hexPos)

            for cityPos in otherPlayer.cities:
                for hexPos in gameState.boardNodes[cityPos].adjacentHexes:
                    if hexPos in gameState.possibleRobberPos and CheckHex(hexPos):
                        possiblePositions.append(hexPos)

        return [PlaceRobberAction(player.seatNumber, pos) for pos in possiblePositions]

    def ChoosePlayerToStealFrom(self, gameState, player):

        if player is None:
            player = self

        possiblePlayers = gameState.GetPossiblePlayersToSteal(player.seatNumber)

        if len(possiblePlayers) > 0:
            return [ChoosePlayerToStealFromAction(player.seatNumber, p) for p in possiblePlayers]

        return None

    def ChooseCardsToDiscard(self, player = None):

        if player is None:
            player = self

        if sum(player.resources) <= 7:
            return [DiscardResourcesAction(player.seatNumber, [0, 0, 0, 0, 0, 0])]

        resourcesPopulation = [0 for i in range(0, player.resources[0])] + \
                              [1 for j in range(0, player.resources[1])] + \
                              [2 for k in range(0, player.resources[2])] + \
                              [3 for l in range(0, player.resources[3])] + \
                              [4 for m in range(0, player.resources[4])] + \
                              [5 for n in range(0, player.resources[5])]

        discardCardCount = int(math.floor(len(resourcesPopulation) / 2.0))

        resourcesSelected  = []
        tradePossibilities = []

        for i in range(0, 100):

            selectedResources = random.sample(resourcesPopulation, discardCardCount)
            if selectedResources in resourcesSelected:
                continue

            resourcesSelected.append(selectedResources)

            tradePossibilities.append(DiscardResourcesAction(player.seatNumber, [selectedResources.count(0),
                                                                                selectedResources.count(1),
                                                                                selectedResources.count(2),
                                                                                selectedResources.count(3),
                                                                                selectedResources.count(4),
                                                                                selectedResources.count(5)]))

        return tradePossibilities


    def GetMonopolyResource(self, game, player):

        if player is None:
            player = self

        actionPossibilities = []

        for i in xrange(0, len(player.resources) - 1):
            actionPossibilities.append(UseMonopolyCardAction(player.seatNumber, i+1))

        return actionPossibilities

    def GetYearOfPlentyResource(self, game, player):

        if player is None:
            player = self

        actionPossibilities = []

        for i in xrange(0, 5):
            for j in xrange(0, 5):
                chosenResources = [0, 0, 0, 0, 0]
                chosenResources[i] += 1
                chosenResources[j] += 1
                actionPossibilities.append(UseYearOfPlentyCardAction(player.seatNumber, chosenResources))

        return actionPossibilities

    def GetPossibleActions_PreDiceRoll(self, player):

        if not player.rolledTheDices and \
           not player.playedDevCard and \
                player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
                        player.developmentCards[KNIGHT_CARD_INDEX] > 0:

            return [UseKnightsCardAction( player.seatNumber, None, None )]

        # create a new state for each possible dice outcome
        if not player.rolledTheDices:
            return [RollDicesAction( player.seatNumber, i ) for i in xrange(2, 13)]

    def GetPossibleActions_SpecialTurns(self, gameState, player, atRandom):

        if gameState.currState == 'PLACING_ROBBER':

            if atRandom:
                return super(AgentMCTS, self).ChooseRobberPosition(gameState, player)
            else:
                return self.ChooseRobberPosition(gameState, player)

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            if atRandom:
                return [super(AgentMCTS, self).ChooseCardsToDiscard(player)]
            else:
                return self.ChooseCardsToDiscard(player)

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            if atRandom:
                return [super(AgentMCTS, self).ChoosePlayerToStealFrom(gameState, player)]
            else:
                return self.ChoosePlayerToStealFrom(gameState, player)

        elif gameState.currState == "PLACING_FREE_ROAD1":

            possibleRoads = gameState.GetPossibleRoads(player)

            if possibleRoads is None or not possibleRoads or self.numberOfPieces[0] <= 0:
                return [ ChangeGameStateAction("PLAY1") ]

            return [BuildRoadAction(player.seatNumber, roadEdge,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == "PLACING_FREE_ROAD2":

            possibleRoads = gameState.GetPossibleRoads(player)

            if possibleRoads is None or not possibleRoads or self.numberOfPieces[0] <= 0:
                return [ ChangeGameStateAction("PLAY1") ]

            return [BuildRoadAction(player.seatNumber, roadEdge,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == "WAITING_FOR_TRADE":

            return super(AgentMCTS, self).GetPossiblePlayerTradeReactions(gameState, player)

    def GetPossibleActions_RegularTurns(self, gameState, player, preSelectMode, fromRootNode):

        if gameState.currState == 'PLAY':

            if not player.rolledTheDices and \
                    not player.playedDevCard and \
                    player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
                            player.developmentCards[KNIGHT_CARD_INDEX] > 0:
                return [UseKnightsCardAction(player.seatNumber, None, None)]

            if not player.rolledTheDices:
                return [RollDicesAction(player.seatNumber)]

        elif gameState.currState == 'PLAY1':

            possibleActions     = []
            possibleSettlements = gameState.GetPossibleSettlements(player)
            possibleRoads       = gameState.GetPossibleRoads(player)

            if player.settlements and \
                player.HavePiece(g_pieces.index('CITIES')) and \
                player.CanAfford(BuildCityAction.cost):

                possibleCities = gameState.GetPossibleCities(player)

                if possibleCities is not None and len(possibleCities) > 0:

                    if preSelectMode == 'citiesOverSettlements':
                        return [BuildCityAction(player.seatNumber, node, len(player.cities))
                                            for node in possibleCities]
                    else:
                        possibleActions += [BuildCityAction(player.seatNumber, node, len(player.cities))
                                                for node in possibleCities]

            if player.HavePiece(g_pieces.index('SETTLEMENTS')) and \
                    player.CanAfford(BuildSettlementAction.cost) and \
                    possibleSettlements:

                if preSelectMode == 'citiesOverSettlements':
                    return [BuildSettlementAction(player.seatNumber, node, len(player.settlements))
                                        for node in possibleSettlements]
                else:
                    possibleActions +=  [BuildSettlementAction(player.seatNumber, node, len(player.settlements))
                                        for node in possibleSettlements]

            if preSelectMode == 'citiesAndSettlements' and len(possibleActions) > 0:
                return possibleActions

            if player.HavePiece(g_pieces.index('ROADS')) and \
                    player.CanAfford(BuildRoadAction.cost) and \
                    possibleRoads:

                possibleActions += [BuildRoadAction(player.seatNumber, edge, len(player.roads))
                                    for edge in possibleRoads]

            if gameState.CanBuyADevCard(player) and not player.biggestArmy:

                possibleActions += [BuyDevelopmentCardAction(player.seatNumber)]

            if not player.playedDevCard and sum(player.developmentCards[:-1]) > 0:

                possibleCardsToUse = []

                if not player.playedDevCard:

                    if player.developmentCards[MONOPOLY_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[MONOPOLY_CARD_INDEX]:

                            monopolyPick = self.GetMonopolyResource(gameState, player)

                            if monopolyPick is not None:
                                possibleCardsToUse += monopolyPick

                    if player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[YEAR_OF_PLENTY_CARD_INDEX]:

                            yearOfPlentyPick = self.GetYearOfPlentyResource(gameState, player)

                            if yearOfPlentyPick is not None:
                                possibleCardsToUse += yearOfPlentyPick

                    if player.developmentCards[ROAD_BUILDING_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[ROAD_BUILDING_CARD_INDEX] and \
                                    player.numberOfPieces[0] > 0:

                            freeRoads = UseFreeRoadsCardAction(player.seatNumber, None, None)

                            if freeRoads is not None:
                                possibleCardsToUse.append(freeRoads)

                if possibleCardsToUse:
                    possibleActions += possibleCardsToUse

            possibleTrade = self.GetPossibleBankTrades(gameState, player)
            if possibleTrade is not None and possibleTrade:
                possibleActions += possibleTrade

            if self.trading is not None:
                if self.trading == 'Simple' and fromRootNode and not self.tradeLock:
                    possibleActions += self.GetPossiblePlayerTrades(gameState, player)
                elif self.trading == 'Optimistic' and fromRootNode and not self.tradeLock:
                    possibleActions += self.GetOptimisticMoves(gameState, player)

            possibleActions += [EndTurnAction(playerNumber=player.seatNumber)]

            return possibleActions

    def GetOptimisticMoves(self, gameState, player):

        if player is None:
            player = self

        possibleOptimisticMoves = []

        if player.settlements and \
            player.HavePiece(g_pieces.index('CITIES')) and \
            not player.CanAfford(BuildCityAction.cost):
            possibleCities = gameState.GetPossibleCities(player)
            if possibleCities:
                resourceDiff = player.resources - BuildCityAction.cost
                if sum(resourceDiff) >= 0:
                    buildCityActions = [BuildCityAction(player.seatNumber, node, len(player.cities))
                                        for node in possibleCities]
                    for cityAction in buildCityActions:
                        cityAction.tradeOptimistic = True
                    possibleOptimisticMoves += buildCityActions

        #if self.preSelectMode == 'citiesOverSettlements' and len(possibleOptimisticMoves) > 0:
        #    return possibleOptimisticMoves

        if player.HavePiece(g_pieces.index('SETTLEMENTS')) and \
            not player.CanAfford(BuildSettlementAction.cost):
            possibleSettlements = gameState.GetPossibleSettlements(player)
            if possibleSettlements:
                resourceDiff = player.resources - BuildSettlementAction.cost
                if sum(resourceDiff) >= 0:
                    buildSettlementActions = [BuildSettlementAction(player.seatNumber, node, len(player.settlements))
                                              for node in possibleSettlements]
                    for settlementAction in buildSettlementActions:
                        settlementAction.tradeOptimistic = True
                    possibleOptimisticMoves += buildSettlementActions

        #if self.preSelectMode is not None and len(possibleOptimisticMoves) > 0:
        #    return possibleOptimisticMoves

        if player.HavePiece(g_pieces.index('ROADS')) and \
            not player.CanAfford(BuildRoadAction.cost):
            possibleRoads = gameState.GetPossibleRoads(player)
            if possibleRoads:
                resourceDiff = player.resources - BuildRoadAction.cost
                if sum(resourceDiff) >= 0:
                    buildRoadActions = [BuildRoadAction(player.seatNumber, edge, len(player.roads))
                                        for edge in possibleRoads]
                    for roadAction in buildRoadActions:
                        roadAction.tradeOptimistic = True
                    possibleOptimisticMoves += buildRoadActions

        return possibleOptimisticMoves