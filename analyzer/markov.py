import numpy as np

class Chain(object):
    def __init__(self):
        self.matrix = None
        self.states = {}
        self.states_by_label = {}

    def new_state(self, label=None):
        new_state = State(label)
        if label is not None:
            if label in self.states_by_label:
                label_str = str(label)
                raise ValueError("The state label " + label_str + " is " + 
                                 "already taken")
        
            self.states_by_label[label] = new_state

        new_index = 0

        if self.matrix is None:
            self.matrix = np.matrix(np.array([0]), np.float64)
        else:
            (x,y) = self.matrix.shape
            new_index = x
            self.matrix.resize((x+1,y+1))

        self.states[new_state] = new_index
        return new_state


    def get_state(self, label):
        if label in self.states_by_label:
            return self.states_by_label[label]
        else:
            return None

    def set_transition(self, from_state, to_state, chance):
        if from_state not in self.states:
            raise Exception("The from_state is not part of this chain")
        if to_state not in self.states:
            raise Exception("The to_state is not a part of this chain")
        if from_state == to_state:
            raise Exception("The from_state and to_state much be different")

        if chance < 0 or chance > 1:
            raise Exception("The chance of the state transition must not be " +
                            "less than 0 or greater than 1, but the value " + 
                            str(chance) + " was provided")

        from_index = self.states[from_state]
        to_index = self.states[to_state]
        self.matrix[to_index,from_index] = chance

    def get_transition(self, from_state, to_state):
        if from_state not in self.states:
            raise Exception("The from_state is not part of this chain")
        if to_state not in self.states:
            raise Exception("The to_state is not a part of this chain")
        if from_state == to_state:
            raise Exception("The from_state and to_state much be different")
            
        from_index = self.states[from_state]
        to_index = self.states[to_state]
        return self.matrix[to_index,from_index]

    def _create_start_vector(self, start_state=None):
        (rows,cols) = self.matrix.shape

        pi = np.matrix(np.ones(rows), np.float64)
        pi = pi.transpose()

        if start_state is not None:
            if isinstance(start_state, dict):
                if np.sum(start_state.values()) != 1:
                    raise Exception("The sum of the starting state " + 
                                    "probabilities must add up to 1")
                
                
                pi = pi * 0.
                for start in start_state:
                    pi[self.states[start], 0] = start_state[start]

            else:
                if start_state not in self.states:
                    raise Exception("The start_state is not part of this chain")
            
                # Build an initial distribution vector based on the 
                # starting state provided
                pi = pi * 0.
                pi[self.states[start_state], 0] = 1.
        else:
            # Build an initial distribution with an even distribution
            # across all states
            pi = pi * (1./rows)
        
        return pi


    def steady_state(self,start_state=None, threshold=10e-10):
        pi = self._create_start_vector(start_state)

        (rows,cols) = self.matrix.shape

        # Make a copy of the matrix before it's modified
        trans = self.matrix.copy()

        # Verify transition probiblites and calculate the diagonal
        for col in range(cols):
            sum=0.
            for row in range(rows):
                if row != col:
                    sum += trans[row, col]
                
            if sum > 1:
                raise Exception("The combined probabilities for transtion " + 
                                "from state " + col + " are larger than 1")
                
            trans[col,col] = 1. - sum


        trans = trans**100

        while True:
            pi_temp = trans * pi
            pi = trans * pi_temp
            if np.linalg.norm(pi-pi_temp) < threshold:
                break

        # Convert pi into a map of states and their chances
        result = {}
        for state in self.states:
            state_index = self.states[state]
            result[state] = pi[state_index,0]
            
        return result


class State(object):
    def __init__(self, label=None):
        self.label = label
    

