# Quiz 5
import os
from zli284_assignment_2 import (
    import_data,
    attack_multiplier,
    fight,
    tournament,
)

filedir = 'data/'
dataList = os.listdir(filedir)
#print(dataList)

for item in dataList:
    #print(import_data(os.path.join(filedir, item)))
    participants = import_data(os.path.join(filedir, item))
    print(participants, '\n')


    #--------Testing the functions of attack_multiplier and fight----------------#
    # testAttackMulti = [['Water', 'Fire'], ['Electric', 'Water'], ['Ground', 'Electric'], ['Fire', 'Grass'], ['Grass', 'Water']]
    # for item in testAttackMulti:
    #     print(attack_multiplier(item[0], item[1]))

    for i in range(len(participants)-1):
        for j in range(i+1, len(participants)):
            pass   # disable pass and enable some of the following print to see results
        #===============enabling those prints will take a few minutes to finish printing======================#
#             print('type ', participants[i][1], participants[j][1], )
#             print('factor' , attack_multiplier(participants[i][1], participants[j][1]))
#             print(fight(participants[i], participants[j], 1))
#             print('factor ', attack_multiplier(participants[j][1], participants[i][1]))
#             print(fight(participants[i], participants[j], 2), '\n')
    print(tournament(participants))
print('finished')
