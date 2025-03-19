# For human player
# A human player will use keys to control the snake
from SnakeGame import SnakeGame, Direction

# action [straight, right, left]
def go_up():
    global action
    '''
    The result is to turn the snake move up.
    if currently the snake is moving up, it should keep straight [1,0,0]
    if it's moving right, it should turn left [0,0,1] in order to move up.
    if it's moving left, it should turn right [0,1,1] in order to move up.
    if it's moving down, moving up will cause collision. As such game over.
    '''
    if game.direction == Direction.UP:
        action = [1,0,0]
    elif game.direction == Direction.RIGHT:
        action = [0,0,1]  # turn left
    elif game.direction == Direction.LEFT:
        action = [0,1,0]  # turn right
    else: # must be down
        game.game_over = True
    
    game.direction = Direction.UP
    return action

def go_down():
    global action
    if game.direction == Direction.DOWN:
        action = [1,0,0]
    elif game.direction == Direction.RIGHT:
        action = [0,1,0]  # turn right
    elif game.direction == Direction.LEFT:
        action = [0,0,1]  # turn left
    else: # must be up
        game.game_over = True
    game.direction = Direction.DOWN
    return action

def go_right():
    global action
    if game.direction == Direction.RIGHT:
        action = [1,0,0]
    elif game.direction == Direction.UP:
        action = [0,1,0]  # turn right
    elif game.direction == Direction.DOWN:
        action = [0,0,1]  # turn left
    else: # must be left
        game.game_over = True
    
    game.direction = Direction.RIGHT
    return action

def go_left():
    global action
    if game.direction == Direction.LEFT:
        action = [1,0,0]
    elif game.direction == Direction.DOWN:
        action = [0,1,0]  # turn right
    elif game.direction == Direction.UP:
        action = [0,0,1]  # turn left
    else: # must be right
        game.game_over = True
    game.direction = Direction.LEFT
    return action

def bindingkeys(win):
    win.listen()
    '''
    The bindingkeys function should take the game screen as input, 
    and bind go_up, go_down, go_left and go_right to w,s,a,d accordingly. 
    '''
    win.onkey(go_up,"w")
    win.onkey(go_down,"s")
    win.onkey(go_left,"a")
    win.onkey(go_right,"d")   

# action [straight, right, left]
action = [1,0,0]
if __name__ == '__main__':
    game = SnakeGame(delay=0.1)
    bindingkeys(game.win)

    while True :
        game.play_step(action)
        print(action)
        action = [1,0,0]
        if game.game_over == True:
            game.reset()