from enum import Enum, auto
import random
import string
import copy
import time
from anytree.exporter import DotExporter, UniqueDotExporter
from numpy import argmax, argmin
import inspect
#used to test our own trees
from anytree import Node as N, RenderTree

#Enumarator of Colors used for the cards
class Color(Enum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    WILD = auto()

#Enumarator of Values for the cards
class Value(Enum):
    ZERO = auto()
    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    REVERSE = auto()
    DRAW_TWO = auto()
    SKIP = auto()
    WILD_FOUR = auto()
    WILD = auto()

#Node class to represent the nodes of the Min-Max Tree
class Node:
    def __init__(self, state, value=None, action="") -> None:
        self.state = state
        self.value = value
        self.children = []
        self.action = action    #the action that lead to the state
        self.select_path = False
        self.optimal_action = None
        self.optimal_card = None
        self.play_this = None

    def add_child(self, child: object):
        self.children.append(child)

    def __str__(self):
        return str(self.state)

#Card Class used for the uno game
class Card:
    def __init__(self, color: Color, value: Value) -> None:
        self.color = color
        self.value = value

    def get_color(self) -> Color:
        return self.color
    
    def get_value(self) -> Value:
        return self.value

    def set_color(self, color: Color):
        self.color = color

    #checks if the card matches with another card (same color, same value or is wild)
    def match(self, __o: object) -> bool:
        return self.color == __o.color or self.value == __o.value or self.color == Color.WILD #or __o.color == Color.WILD

    #returns a copy of the card
    def copy(self) -> object:
        return copy.deepcopy(self)

    # #depending on the card it might have different effects on the player
    # def act(self, player):
    #     if self.value == Value.DRAW_TWO:
    #         player.draw(2)

    def __eq__(self, __o: object) -> bool:
        return self.value == __o.value and self.color == __o.color

    def __str__(self) -> str:
        return str(self.color.name) + "-" + str(self.value.name) 

    def __repr__(self) -> str:
        return str(self.color.name) + "-" + str(self.value.name) 

#Deck class (a collection of cards)
class Deck:
    def __init__(self) -> None:
        self.cards = []

    #returns size of the deck
    def size(self) -> int:
        return len(self.cards)

    #shuffles the deck
    def shuffle(self) -> None:
        random.shuffle(self.cards)

    #return true if the deck is empty, false otherwise
    def is_empty(self) -> bool:
        return self.cards == []

    #returns amount number of cards and removes them from the deck
    def draw(self, amount: int=1) -> list[Card]:
        if self.size() < amount:
            amount = self.size()

        drawn_cards = []        
        for i in range(amount):
            drawn_cards.append(self.cards.pop(0))

        
        return drawn_cards

    #creates the deck
    def reset(self) -> None:
        colors = list(Color)
        values = list(Value)

        #create 1-9 + special cards (except Wild and Wild +4) for all colors twice
        for i in range(2):
            for c in range(len(colors) - 1):
                for v in range(1, len(values) - 2):
                    color = colors[c]
                    value = values[v]

                    self.cards.append(Card(color, value))

        #create all colored 0's
        for c in range(len(colors) - 1):
            color = colors[c]
            self.cards.append(Card(color, Value.ZERO))

        #create wild cards (4 wild cards and 4 wild +4)
        for v in range(len(values) - 2, len(values)):
            value = values[v]
            for i in range(4):
                self.cards.append(Card(Color.WILD, value))

        #shuffles the deck after done creating
        self.shuffle()

    #returns a copy of the class
    def copy(self) -> object:
        return copy.deepcopy(self)

    #string representation of the deck
    def __str__(self) -> str:
        return str(self.cards)
class Player:
    def __init__(self, name:str=random.choice(string.ascii_letters)) -> None:
        self.name = name
        self.cards = []
        self.score = 0

    def get_cards(self) -> list[Card]:
        return self.cards

    def number_of_cards(self) -> int:
        return len(self.cards)

    def can_play(self, top: Card) -> list[Card]:
        can_play_cards = []
        for card in self.cards:
            if card.match(top):
                can_play_cards.append(card)
        return can_play_cards

    def draw(self, deck: Deck, amount: int = 1):
        self.cards += deck.draw(amount)

    def play(self, state):
        pass

    def has_won(self) -> bool:
        return self.number_of_cards() == 0

    #returns a copy of the class
    # def copy(self):
    #     return copy.deepcopy()

    def __str__(self) -> str:
        return self.name + ":" + str(self.cards)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other):
        return self.name == other.name 

class SimpleAgent(Player):

    def play(self, state):
        if not self.can_play(state.top):
            #print("Cannot play: Drawing Card")
            self.draw(state.deck)

        if self.can_play(state.top) != []:
            playThis = self.can_play(state.top)[0]
            cardToPlay = Card(playThis.color, playThis.value)
            
            if cardToPlay.color == Color.WILD:
                cardToPlay.color = Color.RED
            # print ("Playing " + str(cardToPlay))
            return cardToPlay

        return None
class Agent(Player):

    def play(self, state):
        if not self.can_play(state.top):
            #TODO: Uncomment this
            # print("Cannot play: Drawing Card")
            self.draw(state.deck)

        if not self.can_play(state.top):
            return None

        # logic to choose
        # (make minmax tree)
        tree = self.create_minimax_tree(state)

        # run search on it with pruning
        value, action = self.max_value_alphabeta(tree, float("-inf"), float("+inf"))

        # pop the optimal card
        bestCard = tree.play_this

        print("Action: " + str(action))
        print("Value: " + str(value))

        return bestCard


    def create_minimax_tree(self, state):
        state = state.copy()
        root = Node(state)
        queue = [root]

        flag = state.player1_turn

        height = 3

        while queue != []:
            node = queue.pop(0)
            state = node.state.copy()

            if flag != state.player1_turn:
                height -= 1
                flag = state.player1_turn

            if height <= 0:
                break

            #check for terminal state
            if state.player1.has_won() or state.player2.has_won() or state.deck.is_empty():
                #node.add_child(Node(state.copy()))
                continue

            #get the player
            current_player = state.player1 if state.player1_turn else state.player2

            #check the cards that can be played
            playable_cards = current_player.can_play(state.top)
        
            #if the player doesn't have a card, the draw from the 
            if playable_cards == []:
                current_player.draw(state.deck)

            #check the cards that can be played
            playable_cards = current_player.can_play(state.top)

            final_cards = []
            for card in playable_cards:
                if card.color == Color.WILD:
                    for color in list(Color)[:-1]:
                        final_cards.append(Card(color, card.value))
                else:
                    final_cards.append(card)

            if playable_cards == []:
                final_cards.append(None)

            for card in final_cards:
                state2 = state.copy()
                action = state2.update(card)
                child = Node(state2, action=action)
                node.add_child(child)
                queue.append(child)
                child.got_here = card  
        
        #get all the leaves, and calculate their value using the heuristic
        me = self
        queue = [root]
        while queue != []:
            n = queue.pop(0)
            current_player = n.state.player1 if n.state.player1_turn else n.state.player2
            # print('current_player name: ' + current_player.name)
            # print(n.state.player1_turn)
            
            #leaf node
            if n.children == []:

                #print('current_player name: ' + current_player.name)
                #print(n.state.player1_turn)
                #if MAX Node
                if me != current_player:
                    #print("hi")
                    n.value = self.h(n.state)
                else:
                    #print("bye")
                    n.value = -self.h(n.state)
                continue
                #n.value = self.h(n.state)

            queue += n.children
        
        return root

    def h(self, state):
        # currentPlayer = state.player1 if state.player1_turn else state.player2
        # otherPlayer = state.player2 if state.player1_turn else state.player1

        me = self
        other = state.player1 if state.player2 is self else state.player2

        score = 0

        #first the difference in cards
        score += (len(other.cards) - len(me.cards))
        # # score -= lenlen(me.cards)

        # #second, the number of trap cards the opposing player have vs the current player
        # opposing_trapcards = 0
        # for card in other.cards:
        #     if card in [Value.WILD_FOUR, Value.SKIP, Value.DRAW_TWO, Value.REVERSE]:
        #         opposing_trapcards += 1

        # current_trapcards = 0
        # for card in me.cards:
        #     if card in [Value.WILD_FOUR, Value.SKIP, Value.DRAW_TWO, Value.REVERSE]:
        #         current_trapcards += 1
        
        # score += current_trapcards - opposing_trapcards

        # #third, if current player has one card and it matches top
        # if len(me.cards) == 1:
        #     score += 1
        #     if me.cards[0].match(state.top):
        #         score += 1
        
        # if len(other.cards) == 1:
        #     score -= 1
        #     if other.cards[0].match(state.top):
        #         score -= 1

        #fourth if any player won
        if me.has_won():
            score += 100
        
        if other.has_won():
            score -= 100

        return score

    def max_value_alphabeta(self, node, alpha, beta):
        #if state is terminal
        if node.children == []:
            return node.value, node.action

        values = []
        for c in node.children:
            v = self.min_value_alphabeta(c, alpha, beta)[0]
            values.append(v)

            if v >= beta:
                return v, c.action 
            alpha = max(alpha, v)

        value = max(values)
        action = node.children[argmax(values)].action
        #node.children[argmax(values)].select_path = True
        node.optimal_action = argmax(values)
        node.play_this = node.children[argmax(values)].got_here

        node.value = value

        return value, action
        
    def min_value_alphabeta(self, node, alpha, beta):
        #if state is terminal
        if node.children == []:
            return node.value, node.action

        values = []
        for c in node.children:
            v = self.max_value_alphabeta(c, alpha, beta)[0]
            values.append(v)

            if v <= alpha:
                return v, c.action 
            beta = min(beta, v)

        value = min(values)
        action = node.children[argmin(values)].action
        #node.children[argmin(values)].select_path = True
        node.optimal_action = argmin(values)
        node.play_this = node.children[argmin(values)].got_here

        node.value = value

        return value, action
class State:
    def __init__(self, p1:Player, p2:Player, number_of_players:int=2) -> None:
        self.deck = Deck()
        self.deck.reset()
        self.player1_turn = True
        self.player1 = p1
        self.player1.draw(self.deck, 7)
        self.player2 = p2
        self.player2.draw(self.deck, 7)
        self.top = self.deck.draw()[0]
        self.discard = []
        
        #replace the top card if a wild color is drawn
        while self.top.get_color() == Color.WILD:
            self.top = self.deck.draw()[0]

        self.gameOver = False
        self.winner = None
        self.cardEffect = False

    def run(self):

        #print("Starting Hands")
        #print(self)

        while not self.gameOver:
            print(self)

            # get the current player
            currentPlayer = self.player1 if self.player1_turn else self.player2
            
            # get the player's next play
            next = currentPlayer.play(self)
            
            # apply the play to the game state
            self.update(next)

        print(self)

    #UPDATE SHOULD RETURN THE ACTION
    def update(self, next: Card):
        currentPlayer = self.player1 if self.player1_turn else self.player2
        otherPlayer = self.player2 if self.player1_turn else self.player1

        #check if deck is empty, if not, re-fill it
        if len(self.deck.cards) == 0:
            self.deck.cards = self.discard

            self.deck.shuffle()
            self.discard = []

        #handles skipping and draw card behaviour
        if self.cardEffect:
            self.cardEffect = False
            self.next_turn()
            return "Skipped turn"

        # handle cannot play
        if not next:
            self.next_turn()
            return "Cannot play, draw a card from deck"

        # play the next card (update top)
        self.play(next)
        #so add
        #print("Next: " + str(next))
        if next.value == Value.WILD_FOUR:
            next = Card(Color.WILD, Value.WILD_FOUR)
        elif next.value == Value.WILD:
            next = Card(Color.WILD, Value.WILD)
        # print("Remove Next: " + str(next))
        # print("Current Player: " + str(currentPlayer.cards))
        currentPlayer.cards.remove(next)

        self.cardEffect = next.value in [Value.WILD_FOUR, Value.SKIP, Value.DRAW_TWO, Value.REVERSE]

        if self.top.get_value() == Value.WILD_FOUR:
            otherPlayer.draw(self.deck, 4)

        elif self.top.get_value() == Value.DRAW_TWO:
            otherPlayer.draw(self.deck, 2)

        # update the turn
        self.next_turn()

        # check win condition
        if currentPlayer.has_won():
                self.gameOver = True
                self.winner = currentPlayer

        return "Play card: " + str(self.top)
            
    def next_turn(self):
        self.player1_turn = not self.player1_turn

    #the player plays the card and updates the top card
    #this also removes the card from the player's hands
    def play(self, card):
        oldCard = self.top
        if oldCard.value == Value.WILD_FOUR:
            oldCard = Card(Color.WILD, Value.WILD_FOUR)
        elif oldCard.value == Value.WILD:
            oldCard = Card(Color.WILD, Value.WILD)

        self.discard.append(oldCard)
        
        if len(self.deck.cards) == 0:
            #print("Discard: " + str(self.discard))
            self.deck.cards = self.discard

            self.deck.shuffle()
            self.discard = []
        
        self.top = card

    #returns a copy of the class
    def copy(self) -> object:
        return copy.deepcopy(self)

    def __str__(self) -> str:
        deck = f"[]"
        if self.deck.cards != []:
            deck = f"[{self.deck.cards[0]} ..."
        string = f"""
                Player 1: {self.player1.get_cards()}
                Top     : {self.top}
                Player 2: {self.player2.get_cards()}
                Deck    : {deck}
                Player {'1' if self.player1_turn else '2'} turn"""
        return string

def queue_maker(root):
    #highlight the edges from root with optimal_action
    queue = [root]
    while queue != []:
        n = queue.pop(0)

        if n.optimal_action is not None:
            n.children[n.optimal_action].select_path = True
            queue.append(n.children[n.optimal_action])

    #Copying
    queue = [root]

    root2 = N(str(root.state) + "\nValue: " + str(root.value), action="", select_path=True)

    queue2 = [root2]

    i = 0
    while queue != []:
        node = queue.pop(0)
        node2 = queue2.pop(0)

        children = node.children
        child_nodes = []
        for child in children:
            child2 = N(str(child.state) + "\nValue: " + str(child.value), action=str(child.action), select_path=child.select_path)
            child_nodes.append(child2)
            queue.append(child)
            queue2.append(child2)
            i += 1
        
        node2.children = child_nodes

    return root2

def nodeattrfunc(node):
    attr = f'label="{node.name}"'
    if node.select_path:
        attr += ', color=red'
    return attr

def edgeattrfunc(node, child):
    attr = f'label="{child.action}"'
    if child.select_path:
        attr += ', color=red'
    return attr


def playEachOther(p1, p2):
    p1Count = 0
    p2Count = 0

    for i in range(1):
        state = State(p1, p2)
        state.run()
        if state.winner == p1:
            print(p1.name + " won")
            p1Count += 1
        else:
            print(p2.name + " won")
            p2Count += 1

    total = p1Count + p2Count
    print(p1.name + " won a total of: " + str(p1Count) + " (" + str((p1Count/total)*100) + "%)")
    print(p2.name + " won a total of: " + str(p2Count) + " (" + str((p2Count/total)*100) + "%)")


if __name__ == '__main__':

    #Max vs Min
    # p1 = Agent(name="Max")
    # p2 =  Agent(name="Min")

    # Max vs Simple
    # p1 = Agent(name="Max")
    # p2 = SimpleAgent(name="Simple")

    # Simple vs Simple
    p1 = Agent(name="Simple 1")
    p2 = Agent(name="Simple 2")
    
    playEachOther(p1,p2)
    # state.player1.cards = [Card(Color.WILD, Value.WILD_FOUR), Card(Color.BLUE, Value.TWO)] #[Card(Color.WILD, Value.WILD), Card(Color.RED, Value.DRAW_TWO)]
    # state.player2.cards = [Card(Color.WILD, Value.WILD), Card(Color.RED, Value.DRAW_TWO)] #[Card(Color.WILD, Value.WILD_FOUR), Card(Color.BLUE, Value.TWO)]

    # state = State(p1,p2)
    # minimax = state.player2.create_minimax_tree(state)

    # value, action = state.player2.max_value_alphabeta(minimax, float("-inf"), float("+inf"))
    # root = minimax

    # #root2 = build_tree(root, N(str(root.state)))
    # root3 = queue_maker(root)

    # UniqueDotExporter(root3,
    #                   edgeattrfunc=edgeattrfunc,
    #                   nodeattrfunc=nodeattrfunc).to_dotfile("minimaxExample.dot")