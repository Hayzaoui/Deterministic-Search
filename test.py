import search
import utils
import itertools
import random
import math

ids = ["111111111", "111111111"]


class DroneProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        """
        on implémente le state initial : 
        safe (valeurs immuables): 
            - self. map : map de taille self.n x self.m 
            - self.position_package : les positions des package 
            - self.position_client : positions des clients 
            - self.package_for_client : package que doivent recevoir chaque client

        """
        """rajouter liste de drones"""
        self.map = initial["map"]
        self.n = len(self.map)  # number of rows
        self.m = len(self.map[0])  # number of cols
        self.position_package = utils.hashabledict(initial["packages"])
        position_client = {}
        package_for_client = {}
        for key, val in initial["clients"].items():
            position_client.update({key: val["path"]})
            package_for_client.update({key: val["packages"]})

        self.position_client = utils.hashabledict(position_client)
        print(self.position_client)

        self.package_for_client = utils.hashabledict(package_for_client)
        """
        Here, we explain what we choosed for the initial state
        """
        """
        *** drone_initial (liste transormée en tuple dans le state ) 
                = (('nom drone', (position), (nom package dans bagage *si vide =()*) ),) 
                exemple ('drone 1', (0, 0), ()),) ou (('drone 1', (0, 1), ()), ('drone 2', (0, 1), ()))
        *** client_initial (liste transormée en tuple dans le state ) 
                = ((prénom, (position), (0,) *ou ('package 1',)* ),)
                exemple ('Yossi', (0, 2), ('package 1,)),)
        *** package_initial : (liste transormée en tuple dans le state )
                = ('package 1', 'package 2',)

        ---> returns : search.Problem.__init__(self, tuple(initial))
                    exemple tuple(initial) : ((('drone 1', (0, 1), ()), ('drone 2', (0, 1), ())), (('Yossi', (0, 1), (0,)),), ('package 1',), 0 (=temps))

        """
        d = initial['drones']
        package_list = []
        drone_initial = []
        for key in d.keys():
            l = [key, d[key], tuple()]  # quand on rajoute un package mettre une virgule ex  ('package 1',)
            drone_initial.append(tuple(l))

        client_initial = []
        c = initial['clients']
        for key, val in c.items():
            # list_pack_to_client = [0 for i in range(len(val['packages']))]
            l = [key, val['path'][0], tuple()]  # tuple(list_pack_to_client)]
            package_list.append(val['packages'])
            client_initial.append(tuple(l))
        # print("client_initial= ", client_initial)
        package_initial = []
        for val in package_list:
            for pack in val:
                package_initial.append(pack)
        package_initial = tuple(package_initial)

        initial = [tuple(drone_initial), tuple(client_initial), package_initial, 0]
        # print("initial= ", initial)
        search.Problem.__init__(self, tuple(initial))

    def actions(self, state):

        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""

        # print("Premier state de Action: ", state)
        actions = []
        actions_list = []
        package_available = state[2]
        # print("Pack Vail Action:    ",package_available)
        """ package_available : tous les packages au sol quand on recoit le state """
        client = state[1]
        for drone in state[0]:
            """for each drone tuple (name, pos, bagage), on check les 4 possibilités qu'on ajoute dans actions """
            actions.append(
                tuple(self.allPosibilityOneDrone(drone, package_available, client, state[3])))  # on tuple apres

        """cartesian product of all possible actions between all drones"""
        for action in itertools.product(*actions):
            duplicate = 0
            l = []
            """on enlève l'action qui comporte 2 drones voulant pickup le meme package"""
            for act in action:
                if act[0] == "pick up":
                    if act[2] in l:
                        duplicate = 1
                        break
                    l.append(act[2])
            # le if ne doit pas etre incrémenté???, qd estce quon rajoute le l ???, changer actions utilié plusieurs fois???????????
            if duplicate == 1:
                continue
            actions_list.append(action)
        # random.shuffle(actions_list)
        actions = tuple(actions_list)
        """for act in actions:
            print("\n", act)"""
        # print("On sort de actions.\n")
        return tuple(actions)

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # print("State debut result= ", state)
        # print("Action debut result= ", action)
        newState = []
        update_drone = []
        update_pack_client = []
        update_client = []
        drones = state[0]
        clients = state[1]
        update_package_available = list(state[2])
        t = state[3]
        for act in action:
            drone_name_from_action = act[1]

            type_of_action = act[0]
            if type_of_action == "wait":
                # print("On entre dans wait.")
                # print("update drone 1: ", update_drone)
                update_drone.extend(
                    [(drone[0], drone[1], drone[2]) for drone in drones if drone_name_from_action == drone[0]])
                # print("update drone 2:  ", update_drone)
                # print("On sort de wait.")

            if type_of_action == "move":
                # print("On entre dans move.")
                new_pos = act[2]
                # print(name_mover)
                for drone in drones:
                    # print("Drone avant modif: ", drone)

                    if drone_name_from_action == drone[0]:
                        update_drone.append((drone_name_from_action, (new_pos), drone[2]))

            if type_of_action == "pick up":
                # print("Action= ", action)
                # print("On entre dans pickup.")
                package_to_pick_up = act[2]
                # print('package topick up: ', package_to_pick_up)
                # print("DRONES= ", drones)
                # print("Update Drone= ", update_drone)
                for drone in drones:
                    # print("DronesSS=  ", drones)
                    # print("Drone=  ", drone)
                    if drone_name_from_action in drone:
                        # print('drone_name_from_action in drone:', drone_name_from_action)
                        bagage_drone = list(drone[2])
                        # print('bagage_drone: avant append', bagage_drone)
                        bagage_drone.append(package_to_pick_up)
                        # print('bagage drone apres append', bagage_drone)
                        # print('update drone avant append', update_drone)
                        update_drone.append((drone_name_from_action, drone[1], tuple(bagage_drone)))
                        # print('update drone apres append', update_drone)
                        # print('update package available  avanr append', update_package_available)
                        update_package_available.remove(package_to_pick_up)
                        # print('update package available  apres append', update_package_available)

            if type_of_action == "deliver":
                # print("On entre dans deliver.")
                package_to_deliver = act[3]
                name_to_deliver = act[2]
                for drone in drones:
                    if drone_name_from_action in drone:
                        bagage_drone = list(drone[2])
                        for client in clients:
                            if name_to_deliver in client:
                                packages_client = list(client[2])
                                packages_client.append(package_to_deliver)
                                bagage_drone.remove(package_to_deliver)
                                update_drone.append((drone_name_from_action, drone[1], tuple(bagage_drone)))
                                check = 0
                                for i in range(len(update_pack_client)):
                                    if update_pack_client[i][0] == name_to_deliver:
                                        update_pack_client[i][1] += packages_client
                                        update_pack_client[i][1] = list(dict.fromkeys(update_pack_client[i][1]))
                                        check = 1
                                if check == 0:
                                    update_pack_client.append([name_to_deliver, packages_client])
                                # break

        t += 1
        for client in clients:

            client_name = client[0]
            path = list(self.position_client[client_name])
            len_path = len(path)
            new_pos = path[t % len_path]
            check = 0
            for l in update_pack_client:
                if client_name in l:
                    new_pack = l[1]
                    update_client.append((client_name, new_pos, tuple(new_pack)))
                    check = 1
            if check == 0:
                update_client.append((client_name, new_pos, client[2]))

        new_tstate = (tuple(update_drone), tuple(update_client), tuple(update_package_available), t)
        # print('State fin result: ', new_tstate)

        return new_tstate

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        # print("On entre dans goal state.\n")
        # print('State: goal state', state)
        drones = state[0]
        clients = state[1]
        packages = state[2]
        # print(packages)

        if len(packages) > 0:
            return False
        for drone in drones:
            if len(drone[2]) == 0:
                # print('State avant de finir= ', state)
                continue
            else:
                return False
        """for client in clients:
            name = client[0]
            if self.package_for_client[name] == client[2]:
                return True"""
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        """h = 10
        count_pick_up = 0
        count_deliver = 0
        count_pas_bien = 0
        if node.action:
            for act in node.action:
                for drone in node.state[0]:
                    if len(drone[2]) == 0:
                        if act[0] == "pick up":
                            count_pick_up += 100000
                    if len(drone[2]) == 1:
                        if act[0] == "pick up":
                            count_pick_up += 1000000
                        if act[0] == "deliver":
                            count_deliver += 100000
                    if len(drone[2]) == 2:
                        if act[0] == "deliver":
                            count_deliver += 30000

        if len(node.state[2]) == len(self.position_package.keys()):
            count_pick_up += 10
        if count_pick_up and count_deliver:
            count_pick_up+=10000
            count_deliver+=10000
        else:
            count_pas_bien += 1000000

        h = -10*count_pick_up -10*count_deliver+count_pas_bien"""
        """print(node.action)
        count_delpick = 0
        if node.action:
            for act in node.action:
                if act[0] == "pick up" or act[0] == "deliver":
                    count_delpick += 1"""
        """if node.action:
            for act in node.action:
                if (act[0]=='wait'and node.parent and node.parent.state[0]==node.state[0]) or act[0]=='move' :
                    return 3000"""
        h = 0
        """h = -1
        if node.action and node.action[0][0] == 'wait' and node.action[0][0]=="move":
            return h
        if not node.action:
            print("Premier h=", h)
            exit()
                    if node.parent and node.action[0][0]=="wait":
            print("La")
            return 300"""
        count = 0
        """if node.action:
            print(node.action)
            p2 = node.solution()
            print(p2)
            a = utils.mode(p2)
            print("a= ", a)"""

        """communn_action_per_drone = {}
        for drones in node.state[0]:
            communn_action_per_drone[drones[0]] = []
        #dict_to_package =
        pack_available = node.state[2]
        for actions in node.solution():
            for act in actions:
                communn_action_per_drone[act[1]].append(act)

        for key, val in communn_action_per_drone.items():
            for act in val:
                most_commun_act = utils.mode(node.solution())
                for ac in most_commun_act:
                    if ac[0]=="move":
                        print("Enter in h move")
                        h+= (node.depth+node.path_cost)**(len(node.action))
                    elif ac[0] == "wait":
                        h += (node.depth + node.path_cost) ** (len(node.action))
                    else:
                        print(ac)
                        print("Enter in h deliver or pickup")
                        h -= (node.depth + node.path_cost) ** (len(node.action))"""
        # if node.parent():
        """if node.action:
            p = utils.mode(node.solution())
            print("p= ", p)
            for pp in p:
                if pp[0] =='wait':
                    h += (node.depth+node.path_cost)**(len(node.action)*self.n*self.m)
                if pp[0] =='pick up' or pp[0] =='deliver':
                    h -= (node.depth+node.path_cost)**len(node.action)
            for d in node.state[0]:
                if pack_available:
                    if len(d[2]) < 2:
                        dist_min = self.m * self.n
                        pack_min = pack_available[0]
                        pos = d[1]
                        dist_pacp_to_d = 0
                        for pack in pack_available:
                            dist_pacp_to_d = utils.distance(self.position_package[pack], pos)
                            if dist_pacp_to_d < dist_min:
                                dist_min = dist_pacp_to_d
                                pack_min = pack

                        for act in node.action:
                            if act[1]==d and act[0]=="move":
                                dist_new_to_pack = utils.distance(self.position_package[pack_min], act[2])
                                if dist_new_to_pack > dist_pacp_to_d:
                                    h += (node.depth+dist_new_to_pack)**(len(node.action)*self.n)
                                else:
                                    h-= (node.depthd+dist_new_to_pack)**(len(node.action)*self.n)"""

        """if node.action:

            for act in node.action:
                if act[0]=="pick up":
                    print("Okayyyyy",act[0])

                    h -= node.depth**(len(node.action)*19)"""

        drones = node.state[0]
        clients = node.state[1]
        package_available = node.state[2]

        h = len(package_available)
        h += len(packages_client)
        print('ok', drones, packages_client, package_available)
        print("pc[0]: ", pc[0], "d[2] :", d[2], "d[3] :", d[3])

        for d in drones:
            if len(d[2]) == 2:
                for pack in drone[2]:
                    for pc in self.position_client:
                    manh_dist = utils.distance(drone[1], )
                    if node.action[0]=="move":
                    if pc[0] == d[2] or pc[0] == d[3]:
                        h += utils.distance(d[2], d[1])

            else:
                h += utils.distance(pc[3], pc[2])
                h += utils.distance(d[1], pc[3])
                h += len(package_available)

        return h

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def check_legal_position(self, i, j):  # enlever le map des inputs et changer le map par self.map dans la fct

        if i < 0 or i > self.n - 1:
            return False
        if j < 0 or j > self.m - 1:
            return False
        if self.map[i][j] == "I":
            return False
        return True

    def allPosibilityOneDrone(self, drone, package_available, clients, t):  # enlever les map
        """get in function attributes self, drone=(name, pos, baggage), package_available=list[p1, p2], clients=(name, pos, package delivered)"""
        moves = []
        pick_up = []
        delivery = []
        name_drone = drone[0]
        position_drone = drone[1]
        i = position_drone[0]
        j = position_drone[1]
        baggage_drone = drone[2]
        legal_moves = []

        """check all legal moves for a given drone and add all of them (max 4) to list moves"""

        if self.check_legal_position(i - 1, j):
            legal_moves.append((i - 1, j))
        if self.check_legal_position(i + 1, j):
            legal_moves.append((i + 1, j))
        if self.check_legal_position(i, j - 1):
            legal_moves.append((i, j - 1))
        if self.check_legal_position(i, j + 1):
            legal_moves.append((i, j + 1))
        for legal_move in legal_moves:
            moves.append(("move", name_drone, legal_move))

        """first check if the drone baggage is full (=2), if <2 continue to check pickup options"""
        if len(drone[2]) < 2:
            """if the list of package available to pick up on the floor is not empty, continue"""
            if package_available:
                for pack in package_available:
                    """check if the given pack position is on the same tile than the drone position"""
                    if self.position_package[pack] == position_drone:
                        """check if we already added this option to the pick up list, if not add option"""
                        if ("pick up", name_drone, pack) not in pick_up:
                            pick_up.append(("pick up", name_drone, pack))

        """vérifier si le drone a un b dans son baggage, compare pos client & pos drone, si egales, on verifie si le client
        doit recevoir ce baggage b et on ajoute possibilité de deliver """
        if baggage_drone:
            for client in clients:
                position_client = client[1]
                if position_drone == position_client:
                    name_client = client[0]
                    for b in baggage_drone:
                        if b in self.package_for_client[name_client]:
                            delivery.append(("deliver", name_drone, name_client, b))

        moves.extend(pick_up)
        moves.extend(delivery)
        moves.append(("wait", name_drone))

        return moves


def create_drone_problem(game):
    return DroneProblem(game)
