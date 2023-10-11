#-- Base vs Continuous Assignment --
import yaml
with open('meta.yaml', 'r') as f:
    data = f.read()
Config = yaml.safe_load(data)

Config['meta']['total_row_monitoring'] = 0
Config['meta']['total_crop_monitoring'] = 0

Config['meta']['rng_seed'] = -1

import os
try:
    os.mkdir('results/')
    os.mkdir('results/e1/')
except:
    pass
Config['meta']['pointset'] = 'riseholme_poly_act_sim.tmap'

uca=[0,1,0,1,0,1]
score=[5,5,10,10,20,20]

from crh_star_ros.roscore import roscore
x=0
for i in range(1,6):
    for j in range(1,10):
        x=x+1

        Config['heuristics']['use_continuous_assignment'] = uca[i]
        Config['meta']['total_cycles'] = 20
        Config['meta']['total_agents'] = score[i]
        Config['meta']['total_logistics'] = score[i]

        [_,_,_,_,_,T] = roscore(Config)
        save("results/e1/"+x+"-"+i+".mat", 'T')
