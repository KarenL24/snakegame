# Snake game
# Refactor previous Snake Game

import turtle
import random
import time 
from enum import Enum # num
import numpy as np # new

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class SnakeGame:
    def __init__(self, delay = 0.08):
        #setup variables
        self.delay = delay
        # score
        self.score = 0
        self.n_games = 0
        self.high_score = 0
        self.steps_played = 0
        self.game_over = False

        #Setup screen
        self.win = turtle.Screen()
        self.win.title("Snake Game by AI | Python with AI Level 4")
        self.win.setup(width=600,height=600)

        # Snake head
        self.head = turtle.Turtle()
        self.head = self.head
        self.head.shape("square")
        self.head.color("green")
        self.head.speed(0)
        self.head.penup()

        # Snake body parts, start with empty.
        self.body_parts = []

        # Apple
        self.apple = turtle.Turtle()
        self.apple.speed(0)
        self.apple.shape("circle")
        self.apple.color("red")
        self.apple.penup()
        self.apple.shapesize(1, 1)
        self.apple.goto(0, 0)

        # Pen to write the score board
        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.shape("square")
        self.pen.color("black")
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(0, 260)
        self.reset()

    # Game state
    @property
    def applex(self):
        return self.apple.xcor()
    @property
    def appley(self):
        return self.apple.ycor()
    @property
    def headx(self):
        return self.head.xcor()
    @property
    def heady(self):
        return self.head.ycor()

    def eatapple(self):
        '''return true if the snake eats an apple'''
        return self.head.distance(self.apple) <15

    def play_step(self,action):
        '''
        It takes action and changes snake moving direction. It returns
        reward of the action, game over flag and score.
        '''
        self.steps_played += 1
        self.game_over = False

        if self.iscollision() or self.steps_played > 100* ( len(self.body_parts) + 1 ):
            self.game_over = True
            return 

        if self.eatapple():
            # Snake eats the apple
            # Increase the score
            self.score += 1                 
            if self.score > self.high_score:
                self.high_score = self.score
            #display updated score
            self.update_score(self.score,self.high_score)

            # move the apple to a random position on the screen
            x = random.randint(-280, 280)
            y = random.randint(-280, 280)
            # don't place the apple on the snake body
            while self.iscollision((x,y)):
                x = random.randint(-280, 280)
                y = random.randint(-280, 280)
            self.apple.goto(x, y)

            # grow the snake by adding one body part
            new_part = turtle.Turtle()
            new_part.hideturtle()
            new_part.speed(0)
            new_part.shape("square")
            new_part.color("blue")
            new_part.penup()
            self.body_parts.append(new_part)

        # move body part to follow the previous one
        '''
        for index in range(len(self.body_parts)-1, 0, -1):
            x = self.body_parts[index-1].xcor()
            y = self.body_parts[index-1].ycor()
            self.body_parts[index].goto(x, y)
        '''
        # Move the last part to where the head is
        if len(self.body_parts) > 0:
            x = self.head.xcor()
            y = self.head.ycor()
            # move the last part right after the head
            last_part = self.body_parts.pop()
            self.body_parts.insert(0,last_part)
            last_part.goto(x, y)
            last_part.showturtle()

        # move the snake head by the action
        self.move(action)
        time.sleep(self.delay)
        return 

    def move(self,action):
        # action [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        # decide the moving direction
        if np.array_equal(action, [1, 0, 0]):
            new_dir = self.direction # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        # move the snake head
        if self.direction == Direction.UP:
            ycor = self.head.ycor()
            self.head.sety(ycor + 20)
        
        if self.direction == Direction.DOWN:
            ycor = self.head.ycor()
            self.head.sety(ycor - 20)

        if self.direction == Direction.RIGHT:
            xcor = self.head.xcor()
            self.head.setx(xcor + 20)
        
        if self.direction == Direction.LEFT:
            xcor = self.head.xcor()
            self.head.setx(xcor - 20)

    def iscollision(self,pt = None):
        if pt  == None:
            x = self.head.xcor()
            y = self.head.ycor()
        else:
            x = pt[0]
            y = pt[1]
        
        # Check for border collision
        if x >= 290 or x <= -290 or y >= 290 or y <= -290:
            return True
        
        # Check for body collision
        for index in range(len(self.body_parts)-1,1,-1):
            if self.body_parts[index].distance(self.head) < 20:  
                return True

        return False

    def reset(self):
        self.n_games += 1
        self.steps_played = 0
        self.score = 0
        self.game_over = False
        self.direction = Direction.DOWN
        # change snake and body parts to red after collision
        self.head.color("red")
        for part in self.body_parts:
            part.color("red")

        self.win.update()

        # Hide the body_parts
        for part in self.body_parts:
            #move the snake head to the start point for a new game
            part.goto(1000, 1000)
            part.clear()
        
        # clear part list
        self.body_parts.clear()

        # Move the snake to the home poistion to restart a game
        self.head.color("green")
        self.head.goto(0, 100)

        self.update_score(self.score,self.high_score)

    def update_score(self,score,high_score):
        # update score
        self.pen.clear()
        self.pen.write("Games: {} Score: {} High Score: {}".format(self.n_games,score, high_score), align="center", font=("Courier", 12, "normal"))


if __name__ == '__main__':
    '''Testing
    Expected Output
    The snake should eat one apple and run in square
    '''
    game = SnakeGame(delay=0.1)
    game.direction = Direction.DOWN
    count = 1
    while game.game_over == False:
        action = []
        if count % 10 == 0:
            action = [0,1,0] # right
        else:
            action = [1,0,0] # straight
        game.play_step(action)
        count += 1
    print('looking good')
