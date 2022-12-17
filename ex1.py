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
            - self.position_client : positions des clients / unashable
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
        drone_initial = {}
        for key in d.keys():
            drone_initial[key] = tuple(
                [d[key], tuple()])  # quand on rajoute un package mettre une virgule ex  ('package 1',)

        client_initial = {}
        c = initial['clients']
        for key, val in c.items():
            # list_pack_to_client = [0 for i in range(len(val['packages']))]
            client_initial[key] = tuple([val['path'][0], tuple()])  # tuple(list_pack_to_client)]
        package_initial = []
        for key in initial["packages"].keys():
            package_initial.append(key)

        package_initial = tuple(package_initial)
        drone_initial = utils.hashabledict(drone_initial)
        client_initial = utils.hashabledict(client_initial)
        initial = {}
        initial = {"Drones": drone_initial, "Clients": client_initial, "PackageAv": package_initial}
        initial = utils.hashabledict(initial)
        print("initial= ", initial)

        search.Problem.__init__(self, initial)

    def actions(self, state):

        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""

        actions = []
        actions_list = []
        # print("state", state)
        package_available = state["PackageAv"]
        # print("Pack Vail Action:    ",package_available)
        """ package_available : tous les packages au sol quand on recoit le state """
        client = state["Clients"]
        for key, val in state["Drones"].items():
            """for each drone tuple (name, pos, bagage), on check les 4 possibilités qu'on ajoute dans actions """
            actions.append(
                tuple(self.allPosibilityOneDrone(key, val, package_available, client)))  # on tuple apres

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

        # print(state)
        # print("action=", actions)
        return tuple(actions)

    def result(self, statee, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        state = statee.copy()
        drones = state["Drones"].copy()
        clients = state["Clients"].copy()
        update_package_available = list(state["PackageAv"])

        for act in action:
            drone_name_from_action = act[1]
            type_of_action = act[0]
            a = 0
            if type_of_action == "wait":
                continue

            if type_of_action == "move":
                new_pos = act[2]
                drones[drone_name_from_action] = ((new_pos), drones[drone_name_from_action][1])
            if type_of_action == "pick up":
                bagage_drone = list(drones[drone_name_from_action][1])

                package_to_pick_up = act[2]
                bagage_drone.append(package_to_pick_up)

                drones[drone_name_from_action] = (drones[drone_name_from_action][0], tuple(bagage_drone))

                update_package_available.remove(package_to_pick_up)

            if type_of_action == "deliver":
                package_to_deliver = act[3]
                name_to_deliver = act[2]
                bagage_drone = list(drones[drone_name_from_action][1])
                bagage_drone.remove(package_to_deliver)
                drones[drone_name_from_action] = (drones[drone_name_from_action][0], tuple(bagage_drone))
                packages_client = list(clients[name_to_deliver][1])
                packages_client.append(package_to_deliver)
                clients[name_to_deliver] = (clients[name_to_deliver][0], tuple(packages_client))

        for client_name in clients.keys():
            path = self.position_client[client_name]
            # print("path= ",path)
            i = path.index(clients[client_name][0])
            # print("index", i)
            len_path = len(path)
            new_pos = path[(i + 1) % len(path)]
            # print("Newpos=", new_pos)
            clients[client_name] = (new_pos, clients[client_name][1])
            check = 0

        new_state = {"Drones": utils.hashabledict(drones), "Clients": utils.hashabledict(clients),
                     "PackageAv": tuple(update_package_available)}

        return utils.hashabledict(new_state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        # print("On entre dans goal state.\n")
        # print('State: goal state', state)
        drones = state["Drones"]
        clients = state["Clients"]
        packages = state["PackageAv"]
        # print(packages)

        if len(packages) > 0:
            return False
        for drone in drones.keys():
            if len(drones[drone][1]) == 0:
                # print('State avant de finir= ', state)
                continue
            else:

                return False

        return True

    def h(self, node):
        h = 0
        drones = node.state["Drones"]
        dist_drone_package = {}
        dist_drone_min_path = {}
        package_available = node.state["PackageAv"]
        client_available = node.state["Clients"]


        c = {}

        for package in self.position_package.keys():
            if package in package_available:
                h += 5

        if node.action:
            for drone in drones.keys():
                dist_drone_package[drone] = []
                dist_drone_min_path[drone] = []

            for key in dist_drone_package.keys():
                dist_drone_package[key] = {}
                dist_drone_min_path[key] = {}
                dist_min = self.m + self.n
                pos_drone = drones[key][0]
                for pack in package_available:
                    pos_package = self.position_package[pack]

                    dist = distance(pos_drone, pos_package)
                    dist_drone_package[key][pack] = dist

                for k, val in self.position_client.items():
                    for pos in val:
                        dm = distance(pos, pos_drone)
                        if dm < dist_min:
                            dist_min = dm
                            dist_drone_min_path[key][k] = (dm, pos)
                        else:
                            dist_drone_min_path[key][k] = (dist_min, pos)

        clients = node.state["Clients"]
        """if  node.parent:
            for act in node.action:
                if act[0]=="deliver":
                    h-= 10"""
        if node.state["PackageAv"]:
            h += 10
        """else:
            h -= 10"""
        """for k, v in client_available.items():
            if len(v[1])==0:
                h+=10"""
        if node.action:
            for act in node.action:
                if act[0]=='deliver' or act[0]=='pick up':
                    h-=10

        if node.parent:
            for drone in drones.keys():
                if drones[drone][1] == node.parent.state["Drones"][drone][1]:
                    h += 5
        for key, val in clients.items():
            pack_client = val[1]
            nbr_of_order_pack = len(self.package_for_client[key])
            if len(pack_client):
                h -= len(pack_client)
            else:
                h += nbr_of_order_pack

        # estimate_nbr_pack = len(self.position_package.keys()) / len(drones.keys())
        count_bad_wait = {}
        a = {}


        return h

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def distance_with_i(self, x, y):
        return

    def check_legal_position(self, i, j):  # enlever le map des inputs et changer le map par self.map dans la fct

        if i < 0 or i > self.n - 1:
            return False
        if j < 0 or j > self.m - 1:
            return False
        if self.map[i][j] == "I":
            return False
        return True

    def allPosibilityOneDrone(self, key, drone, package_available, clients):  # enlever les map
        """get in function attributes self, drone=(name, pos, baggage), package_available=list[p1, p2], clients=(name, pos, package delivered)"""
        moves = []
        pick_up = []
        delivery = []
        name_drone = key
        position_drone = drone[0]
        i = position_drone[0]
        j = position_drone[1]
        baggage_drone = drone[1]
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
        if len(drone[1]) < 2:
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
            for client, val in clients.items():
                position_client = val[0]
                if position_drone == position_client:

                    for b in baggage_drone:
                        if b in self.package_for_client[client]:
                            delivery.append(("deliver", name_drone, client, b))

        moves.extend(pick_up)
        moves.extend(delivery)
        moves.append(("wait", name_drone))
        # print("move=", moves)
        return moves

    def min_dict(self, dic):
        min = self.m + self.n + 3
        min_pack = ''
        # print("DICC", dic)
        for key in dic.keys():
            if dic[key] < min:
                min = dic[key]
                min_pack = key
        return min, min_pack


def max_dict(dic):
    max = 0
    for key in dic.keys():
        if dic[key] > max:
            max = dic[key]
    return max


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def create_drone_problem(game):
    return DroneProblem(game)
