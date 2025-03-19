
import os
import torch
import random
import numpy as np
from collections import deque
from SnakeGame import SnakeGame, Direction #, Point
from Model import Linear_QNet, QTrainer
from Helper import plot


MAX_MEMORY = 200_000
BATCH_SIZE = 2000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.8 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3 )
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.is_trained_model = False

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

    def get_distance(self,game):
        return game.head.distance(game.apple)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon and self.is_trained_model == False:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def get_trained_model(file_name='model.pth'):
    trained_model = None
    record = 0
    model_folder_path = './model'
    file_name = os.path.join(model_folder_path, file_name)
    if os.path.exists(file_name):
        try:
            trained_model = Linear_QNet(11, 256, 3)
            checkpoint = torch.load(file_name)
            trained_model.load_state_dict(checkpoint['model_state_dict']) 
            record = checkpoint['record']
        except:
            print("Continue...")
  
    return trained_model, record 

def rebuild():
    record = 68
    model_folder_path = './model'
    source_file = 'model68.pth'
    destination_file = 'model.pth'
    source = os.path.join(model_folder_path, source_file)
    destination =  os.path.join(model_folder_path, destination_file)
    trained_model = Linear_QNet(11, 256, 3)
    trained_model.load_state_dict(torch.load(source))
    torch.save(
                {
                    'record': record,
                    'model_state_dict': trained_model.state_dict(),
                }, destination)

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    trained_model, record = get_trained_model()
    if trained_model is not None :
        # load previous save the model and continue training
        # agent.is_trained_model = True
        agent.model = trained_model
        agent.model.train()

    game = SnakeGame(delay=0.01)
    while True:
        # get current state
        state_current = agent.get_state(game)
        distance_current = agent.get_distance(game)

        # get move
        action = agent.get_action(state_current)

        # perform move and get new state
        reward = 0
        game.play_step(action)
        done = game.game_over
        score = game.score

        # assign reward based on result of the move
        if game.game_over:
            reward = -10
        
        if game.eatapple():
            reward = 10

        state_new = agent.get_state(game)
        distance_new = agent.get_distance(game)

        # reward if it moves toward the apple
        if distance_new < distance_current:
            reward  += 1

        # train short memory
        agent.train_short_memory(state_current, action, reward, state_new, done)

        # remember
        agent.remember(state_current, action, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save(record)

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    #rebuild()
    train()