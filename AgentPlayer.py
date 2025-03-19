# AI Agent. It will learn and play the snake game
import os
import torch
import numpy as np
from SnakeGame import SnakeGame, Direction  
from Model import Linear_QNet  
from Helper import plot

class Agent:

    def __init__(self):
        if torch.cuda.is_available():
            torch.device = 'cuda'
        else:
            torch.device = 'cpu'

        self.n_games = 0
        self.model = Linear_QNet(11, 256, 3)
 
    def get_state(self, game):
        point_l = (game.headx - 20, game.heady)
        point_r = (game.headx + 20, game.heady)
        point_u = (game.headx, game.heady + 20)
        point_d = (game.headx, game.heady - 20)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.iscollision(point_r)) or 
            (dir_l and game.iscollision(point_l)) or 
            (dir_u and game.iscollision(point_u)) or 
            (dir_d and game.iscollision(point_d)),

            # Danger right
            (dir_u and game.iscollision(point_r)) or 
            (dir_d and game.iscollision(point_l)) or 
            (dir_l and game.iscollision(point_u)) or 
            (dir_r and game.iscollision(point_d)),

            # Danger left
            (dir_d and game.iscollision(point_r)) or 
            (dir_u and game.iscollision(point_l)) or 
            (dir_r and game.iscollision(point_u)) or 
            (dir_l and game.iscollision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Apple location 
            game.applex < game.headx,  # Apple left
            game.applex > game.headx,  # Apple right
            game.appley > game.heady,  # Apple up
            game.appley < game.heady   # Apple down
            ]

        return np.array(state, dtype=int)

    def get_action(self, state):
        final_move = [0,0,0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
        return final_move

def get_trained_model(file_name='model79.pth'):
    trained_model = None
    model_folder_path = './model'
    file_name = os.path.join(model_folder_path, file_name)
    if os.path.exists(file_name):
        try:
            trained_model = Linear_QNet(11, 256, 3)
            checkpoint = torch.load(file_name)
            trained_model.load_state_dict(checkpoint['model_state_dict']) 
        except:
            print("Continue...")
        return trained_model

def play():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    trained_model = get_trained_model()
    if trained_model is None:
        print("no trained model found. ")
        quit
    else:
        agent.model = trained_model
        agent.model.eval()

    game = SnakeGame(delay=0.000)
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        action = agent.get_action(state_old)

        # perform move and get new state
        game.play_step(action)
        score = game.score 
        done = game.game_over
        if done:
            # plot result
            game.reset()
            agent.n_games += 1

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores,"Playing...")


if __name__ == '__main__':
    play()