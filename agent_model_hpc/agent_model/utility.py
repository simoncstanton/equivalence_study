import re
import importlib

from agent_model.gameforms import agent_topology

class Utility:

    def __init__(self):
        pass


    def strategy_display_names(self):
        strategy_display_names = {
                "tft": "Tit-for-Tat",
                "allc":   "Always Cooperate",
                "alld":   "Always Defect",
                "random":   "Random",
                "bully_naive": "Bully (Naive)",
                "fictitiousplay": "Fictitous Play",
                "bandit_inc_softmax_ap_2ed": "Incremental, Softmax, Action Preferences",   #  S&B 2ed
                "bandit_noninc_softmax_ap_2ed": "NonIncr, Softmax, AP", #  S&B 2ed
                "bandit_pursuit_sav": "Pursuit, Sample-Average",
                "bandit_reinfcomp": "Reinforcement Comparison",
                "bandit_sav_inc": "Sample-Average, Incr",
                "bandit_sav_inc_optimistic_greedy": "Sample-Average, Incr, Optimistic, Greedy",
                "bandit_sav_inc_softmax": "Sample-Average, Incr, Softmax",
                "bandit_sav_noninc": "Sample-Average, NonIncr",
                "bandit_sav_noninc_softmax": "Sample-Average, NonIncr, Softmax",
                "bandit_sl_direct": "Supervised Learning, Direct",
                "bandit_sl_la_lri": "Supervised Learning, Linear-RI",
                "bandit_sl_la_lrp": "Supervised Learning, Linear-RP",
                "bandit_wa": "Weighted-Average",
                "bandit_wa_optimistic_greedy": "Weighted-Average, Optimistic, Greedy",
                "bandit_wa_softmax": "Weighted-Average, Softmax",
                "bandit_wa_softmax_ap_2ed": "Weighted-Average, Softmax, AP",    # , S&B 2ed.
                "bandit_wa_ucb": "Weighted-Average, UCB",
                "actor_critic_1ed": "Actor-Critic", # S&B 1ed.
                "actor_critic_1ed_eligibility_traces": "Actor-Critic w ETraces",    # S&B 1ed. 
                "actor_critic_1ed_replacetrace": "Actor-Critic w RTraces",    # S&B 1ed. 
                "double_qlearning": "Double Q-Learning",
                "expected_sarsa": "Expected SARSA",
                "qlearning": "Q-Learning",
                "rlearning": "R Learning",
                "sarsa": "SARSA",
                "sarsa_lambda": "SARSA Lambda",
                "sarsa_lambda_replacetrace": "SARSA Lambda, w RTraces",
                "watkins_naive_q_lambda": "Watkins (naive) Q, Lambda",
                "watkins_naive_q_lambda_replacetrace": "Watkins (naive) Q, Lambda w RTraces",
                "watkins_q_lambda": "Watkins Q, Lambda",
                "watkins_q_lfa": "Watkins Q, Linear FA",     
        }
        return strategy_display_names
    
    
    def map_strategy_names():
        strategy_names = {
            "Axelrod": {
                "tft": "Tit-for-Tat",
                "allc":   "Always Cooperate",
                "alld":   "Always Defect",
                "random":   "Random",
                "bully_naive": "Bully (Naive)",
            },
            "Crandall": {
                "fictitiousplay": "Fictitous Play",
            },
            "Bandit": {
                "bandit_inc_softmax_ap_2ed": "Incremental, Softmax, Action Preferences",   #  S&B 2ed
                "bandit_noninc_softmax_ap_2ed": "NonIncr, Softmax, AP", #  S&B 2ed
                "bandit_pursuit_sav": "Pursuit, Sample-Average",
                "bandit_reinfcomp": "Reinforcement Comparison",
                "bandit_sav_inc": "Sample-Average, Incr",
                "bandit_sav_inc_optimistic_greedy": "Sample-Average, Incr, Optimistic, Greedy",
                "bandit_sav_inc_softmax": "Sample-Average, Incr, Softmax",
                "bandit_sav_noninc": "Sample-Average, NonIncr",
                "bandit_sav_noninc_softmax": "Sample-Average, NonIncr, Softmax",
                "bandit_sl_direct": "Supervised Learning, Direct",
                "bandit_sl_la_lri": "Supervised Learning, Linear-RI",
                "bandit_sl_la_lrp": "Supervised Learning, Linear-RP",
                "bandit_wa": "Weighted-Average",
                "bandit_wa_optimistic_greedy": "Weighted-Average, Optimistic, Greedy",
                "bandit_wa_softmax": "Weighted-Average, Softmax",
                "bandit_wa_softmax_ap_2ed": "Weighted-Average, Softmax, AP",    # , S&B 2ed.
                "bandit_wa_ucb": "Weighted-Average, UCB",
            },
            "Rlmethods": {
                "actor_critic_1ed": "Actor-Critic", # S&B 1ed.
                "actor_critic_1ed_eligibility_traces": "Actor-Critic w ETraces",    # S&B 1ed. 
                "actor_critic_1ed_replacetrace": "Actor-Critic w RTraces *",    # S&B 1ed. 
                "double_qlearning": "Double Q-Learning",
                "expected_sarsa": "Expected SARSA",
                "qlearning": "Q-Learning",
                "rlearning": "R Learning",
                "sarsa": "SARSA",
                "sarsa_lambda": "SARSA Lambda",
                "sarsa_lambda_replacetrace": "SARSA Lambda, w RTraces",
                "watkins_naive_q_lambda": "Watkins (naive) Q, Lambda",
                "watkins_naive_q_lambda_replacetrace": "Watkins (naive) Q, Lambda w RTraces",
                "watkins_q_lambda": "Watkins Q, Lambda",
                "watkins_q_lfa": "Watkins Q, Linear FA",
            }
                    
        }
        return strategy_names
     
     
    def all_strategy_parameters():
        all_strategy_parameters = [
            "memory_depth", "initial_action", "alpha", "gamma", "beta", "lambda", "temperature", "ref_reward", "epsilon", "optimistic_0", "optimistic_1", "c",
        ]
        return all_strategy_parameters
    



    def map_mode_names():
        mode_names = {
            "onevsone": "One vs One",
            "onevsmany": "One vs Many *",
            "manyvsmany": "Many vs Many *",
        }
        return mode_names


    def map_gameform_names(self):
        gameform_names = {
            "pd": "Prisoner\'s Dilemma",
            "chicken": "Chicken",
            "staghunt": "Stag Hunt",
        }
        return gameform_names


    def map_gameform_modules(self):
        gameform_modules = {
            "pd": "prisoners_dilemma",
            "chicken": "chicken",
            "staghunt": "stag_hunt",
        }
        return gameform_modules


    def map_reward_types():
        reward_types = {
            "scalar": "Scalar",
            "ordinal": "Ordinal",
            "ordinal_transform_1": "Ordinal Transform 1 *",
        }
        return reward_types

        
    def retrieve_matrix(self, gameform, reward_type):       
        import os 
        
        if re.match(r"[g]\d{3}", gameform):
            print(os.path.basename(__file__) + ":: gameform match to topology")
            topology = agent_topology.agent_topology()
            topology_items = topology.gameforms
            canonical_matrix = topology_items[gameform]
            
        else:
            game_properties = {"preferences": reward_type}
            gameform_lookup = self.map_gameform_modules()
            _m = importlib.import_module('agent_model.gameforms.{}'.format(gameform_lookup[gameform]), 'agent_model')
            gameform_module = getattr(_m, str.capitalize(gameform_lookup[gameform]))(game_properties)
            canonical_matrix = gameform_module.matrix
        
        matrix = self.transform_reward_type(canonical_matrix, reward_type)
        
        return matrix
    
    def transform_reward_type(self, canonical_matrix, reward_type):
        import os
        import copy
        
        matrix_transform = copy.deepcopy(canonical_matrix)
        print(os.path.basename(__file__) + " 1. transform_reward_type: ", canonical_matrix, matrix_transform)
        print(os.path.basename(__file__) + " 2. mapping transform_reward_type to:", reward_type)
        
        if reward_type == "ordinal" or reward_type == "scalar":
            print("ord or sca")
            pass
            
        else:
            
            (reward_type, precision) = reward_type.split(".")
            print(os.path.basename(__file__) + " 3. extracted reward_type, precision: ", reward_type, precision)
            
            if reward_type == "ordinal_norm":
                
                values = [1, 2, 3, 4]
                normalised_vector = self.normalise_reward_type(reward_type, int(precision), values)
                
                for i, r in enumerate(canonical_matrix):
                    #print("i, r: ", i, r)
                    for j, c in enumerate(r):
                        #print("j, c: ", j, c)
                        for k, v in enumerate(c):
                            #print("k: v", k, v)
                            #print("transform, v: ", matrix_transform[i][j][k], normalised_vector[v-1])
                            matrix_transform[i][j][k] = normalised_vector[v-1]
                            #print(matrix_transform)
                                
            elif reward_type == "scalar_norm":
                
                values = [0, 1, 3, 5]
                normalised_vector = self.normalise_reward_type(reward_type, int(precision), values)
                
                value_map = {
                    0 : normalised_vector[0],
                    1 : normalised_vector[1],
                    3 : normalised_vector[2],
                    5 : normalised_vector[3],
                }
                
                #print("canonical_matrix", canonical_matrix)
                #print("normalised_vector", normalised_vector)
                
                for i, r in enumerate(canonical_matrix):
                    #print("i, r: ", i, r)
                    for j, c in enumerate(r):
                        #print("j, c: ", j, c)
                        for k, v in enumerate(c):
                            #print("k: v", k, v)
                            #print("transform, v: ", matrix_transform[i][j][k], value_map[v])
                            matrix_transform[i][j][k] = value_map[v]
                            #print(matrix_transform)

                
        print(os.path.basename(__file__) + " 4. transform_reward_type: ", canonical_matrix, matrix_transform)

        return matrix_transform
    
    
    def normalise_reward_type(self, reward_type, precision, values):
                
        max_value = max(values)
        min_value = min(values)
        for i in range(len(values)):
            values[i] = round((values[i] - min_value) / (max_value - min_value), precision)
                
        return values
        
        
    def retrieve_matrix_displayname(self, gameform):
        
        if re.match(r"[g]\d{3}", gameform):
            return gameform
        else:
            gameform_names = self.map_gameform_names()
            return gameform_names[gameform]
