#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 20:09:13 2020

@author: nitrodubbz
"""

import matplotlib.pyplot as plt
import numpy as np
import autograd.numpy as anp
from pymoo.util.misc import stack
from pymoo.model.problem import Problem
from pymoo.factory import get_termination
from pymoo.algorithms.nsga2 import NSGA2
from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.visualization.scatter import Scatter
from pymoo.performance_indicator.hv import Hypervolume
from pymoo.optimize import minimize

algorithm = NSGA2(
    pop_size=5,
    n_offsprings=2,
    sampling=get_sampling("real_random"),
    crossover=get_crossover("real_sbx", prob=0.1, eta=15),
    mutation=get_mutation("real_pm", eta=20),
    eliminate_duplicates=True
)

termination = get_termination("n_gen", 10)

class SafetyDistance(Problem):

    def __init__(self):
        
        super().__init__(n_var=4, 
             n_obj=2, 
             n_constr=4, 
             xl = anp.array([0,0,0,0]),
             xu = anp.array([10,10,10,10]))        
        
    def _evaluate(self, x, out, *args, **kwargs):
            
        import Generator
        import isintersect
        
        room = Generator.room
        Robot = Generator.Robot
        Goal = Generator.Goal 
        
        wall_left_x = np.array([0.0, 6.0])
        wall_left_y = np.array([6.0, 6.0])
        
        wall_right_x = np.array([4.0, 10.0])
        wall_right_y = np.array([4.0, 4.0])
            
        x1 = x[:,0] 
        x2 = x[:,1]
        y1 = x[:,2]
        y2 = x[:,3]
            
        d1 = np.sqrt(np.square(x1-Robot.x) + np.square(y1-Robot.y))
            
        d2 = np.sqrt(np.square(x1-x2) + np.square(y1-y2))
            
        d3 = np.sqrt(np.square(x2-Goal.x) + np.square(y2-Goal.y))
            
        d_tot = d1 + d2 + d3
        
        """
        Define Safety Distance 
        """
        
        path1_x = np.zeros((np.size(x,0),5))
        path1_y = np.zeros((np.size(x,0),5))
        path2_x = np.zeros((np.size(x,0),5))
        path2_y = np.zeros((np.size(x,0),5))
        path3_x = np.zeros((np.size(x,0),5))
        path3_y = np.zeros((np.size(x,0),5))
        
        for i in np.arange(np.size(x,0)):
            path1_x[i] = np.linspace(Robot.x, x1[i], num=5)
            path1_y[i] = np.linspace(Robot.y, y1[i], num=5)
            path2_x[i] = np.linspace(x1[i], x2[i], num=5)
            path2_y[i] = np.linspace(y1[i], y2[i], num=5)
            path3_x[i] = np.linspace(x2[i], Goal.x, num=5)
            path3_y[i] = np.linspace(y2[i], Goal.y, num=5)
        """            
        path1_x = np.linspace(np.transpose(np.repeat(Robot.x, np.size(x1))),
                                           x1, 
                                           num=5)
        path1_y = np.linspace(np.transpose(np.repeat(Robot.y, np.size(y1))),
                              y1,
                              num=5)
        path2_x = np.linspace(x1, x2, num=5)
        path2_y = np.linspace(y1, y2, num=5)
        path3_x = np.linspace(x2, 
                              np.transpose(np.repeat(Goal.x, np.size(x2))), 
                              num=5)
        path3_y = np.linspace(y2, 
                              np.transpose(np.repeat(Goal.y, np.size(y2))),
                              num=5)
        """     
        
        safety_distance1 = np.zeros((np.size(x,0),5))
        safety_distance2 = np.zeros((np.size(x,0),5)) 
        safety_distance3 = np.zeros((np.size(x,0),5))
        
        safety_distance_min1 = np.zeros(np.size(x,0))
        safety_distance_min2 = np.zeros(np.size(x,0))
        safety_distance_min3 = np.zeros(np.size(x,0))
        
        safety_distance_min_total = np.zeros(np.size(x,0))
        
        for i in np.arange(np.size(x,0)):
            for j in np.arange(5):
                scan_path1 = Generator.Scan(room, 
                                            (path1_x[i,j], path1_y[i,j]), 
                                            0.0, 
                                            8)
                scan_path2 = Generator.Scan(room, 
                                            (path2_x[i,j], path2_y[i,j]), 
                                            0.0, 
                                            8)
                scan_path3 = Generator.Scan(room, 
                                            (path3_x[i,j], path3_y[i,j]),
                                            0.0,
                                            8)
                
                safety_distance1[i,j] = scan_path1.safety_distance()
                safety_distance2[i,j] = scan_path2.safety_distance()
                safety_distance3[i,j] = scan_path3.safety_distance()
        
            safety_distance_min1[i] = np.amin(safety_distance1[i,:], axis=0)
            safety_distance_min2[i] = np.amin(safety_distance2[i,:], axis=0)
            safety_distance_min3[i] = np.amin(safety_distance3[i,:], axis=0)
            
            safety_distance_min_total[i] = min(safety_distance_min1[i], 
                                     safety_distance_min2[i], 
                                     safety_distance_min3[i])
        
        """
            
        for i in np.arange(np.size(path_x)):
            scan = Scan(Room, (path_x[i], path_y[i]), 0.0, 8)
            safety_distance[i] = scan.safety_distance()
                
        safety_distance = np.minimum(safety_distance)
        """
        
        f1 = -safety_distance_min_total
        f2 = d_tot
        
       
        plt.plot([x1[0],x2[0]],[y1[0],y2[0]])
        plt.plot([x1[0],Robot.x],[y1[0],Robot.y])
        plt.plot([Goal.x,x2[0]],[Goal.y,y2[0]])
            
        g1 = path1_y - 6
        g2 = -path3_y + 4
        g3 = path1_x - 4
        g4 = -path3_x + 6

            
        out["F"] = anp.column_stack([f1, f2])
        out["G"] = anp.column_stack([g1, g2])
            
    def _calc_pareto_front(self, flatten=True, **kwargs):
        
        f1_a = np.linspace(0.1**2, 0.4**2, 100)
        f2_a = (np.sqrt(f1_a) - 1)**2
        
        f1_b = np.linspace(0.6**2, 0.9**2, 100)
        f2_b = (np.sqrt(f1_b) - 1)**2
            
        a, b = np.column_stack([f1_a, f2_a]), np.column_stack([f1_b, f2_b])
        return stack(a, b, flatten=flatten)
            
    def _calc_pareto_set(self, flatten=True, **kwargs):
        x1_a = np.linspace(0.1, 0.4, 50)
        x1_b = np.linspace(0.6, 0.9, 50)
        x2 = np.zeros(50)

        a, b = np.column_stack([x1_a, x2]), np.column_stack([x1_b, x2])
        return stack(a,b, flatten=flatten)

problem = SafetyDistance()
            
res = minimize(problem,
               algorithm,
               termination,
               seed=1,
               pf=problem.pareto_front(use_cache=False),
               save_history=True,
               verbose=True)



