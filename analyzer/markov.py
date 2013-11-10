import numpy as np
import sys

npf64_zero = np.float64(0.)
npf64_one = np.float64(1.)

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

        new_state.index = new_index
        self.states[new_state] = new_index
        return new_state


    def get_state(self, label):
        if label in self.states_by_label:
            return self.states_by_label[label]
        else:
            return None

    def set_transition(self, from_state, to_state, chance):
        if from_state.index == to_state.index:
            raise Exception("The from_state and to_state much be different")

        npf64_chance = np.float64(chance)
        if npf64_chance < npf64_zero or npf64_chance > npf64_chance:
            raise Exception("The chance of the state transition must not be " +
                            "less than 0 or greater than 1, but the value " + 
                            repr(chance) + " was provided")
        
        self.matrix[to_state.index,from_state.index] = npf64_chance

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
        # Use copy() to ensure that pi is a C-continuous matrix and not a view
        pi = pi.transpose().copy()

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


    def find_state_by_index(self, index):
        for (state, i) in self.states.items():
            if index == i:
                return state
        return None

    def _raise_error_for_column_greater_than_one(self, cols, col_sums):
        for col in range(cols):
            sum = col_sums[0, col]
            if sum > npf64_one:
                if (sum - sys.float_info.epsilon) > npf64_one:
                    col_state = self.find_state_by_index(col)
                    raise Exception("The probabilities for transtion " + 
                                    "from state " + str(col_state) + " are " +
                                    repr(trans[:,col]) + " total " + repr(sum) +
                                    " which is larger than 1")
        

    def _fill_in_diagonal_transistions(self, trans):
        # Make a copy of the matrix before it's modified
        trans = self.matrix.copy()

        (rows,cols) = self.matrix.shape
        
        # Verify transition probiblites and calculate the diagonal
        np.fill_diagonal(trans, npf64_zero)
        col_sums = np.squeeze(np.asarray(np.sum(trans, axis=0)))
        max = col_sums.max()
        if max > npf64_one:
            if (max - sys.float_info.epsilon) > npf64_one:
                self._raise_error_for_column_greater_than_one(cols, col_sums)
        
        new_diags = npf64_one - col_sums
        trans[np.diag_indices(cols)] = new_diags
        
        return trans

    def _iterate_until_stable(self, trans, start_state, threshold=10e-10):
        state = self._create_start_vector(start_state)
        state_temp = state.copy()
        while True:
            np.dot(trans, state, state_temp)
            np.dot(trans, state_temp, state)
            if np.linalg.norm(state-state_temp) < threshold:
                break
        
        return state

        

    def steady_state(self,start_state=None, threshold=10e-10):
        trans = self._fill_in_diagonal_transistions(self.matrix)

        steady_state = self._iterate_until_stable(trans, start_state, threshold)

        # Convert pi into a map of states and their chances
        result = {}
        for state in self.states:
            state_index = self.states[state]
            result[state] = steady_state[state_index,0]
            
        return result


class State(object):
    def __init__(self, label=None):
        self.label = label
    
    def __str__(self):
        if self.label is not None:
            return str(self.label)
        else:
            return object.__str__(self)
