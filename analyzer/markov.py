import numpy as np
import numpy.linalg as npl
import sys

npf64_zero = np.float64(0.)
npf64_one = np.float64(1.)

class Chain(object):
    def __init__(self):
        self.matrix = None
        self.states = {}
        self.states_by_label = {}

    def _create_matrix(self):
        """
        Create a 1x1 matrix with the initial value of 0.  Return the
        newly created matrix
        """
        return np.matrix(np.array([0]), np.float64)

    def _grow_matrix(self, matrix):
        """
        Increase the size of the matrix by one row and one column without
        disturbing the rest of the matrix.  The new elements should all 
        default to a 0 value.

        Return the newly grown matrix.  It is ok to modify the matrix object
        in place and return that for efficiency.
        """
        (x,y) = matrix.shape
        matrix.resize((x+1,y+1), refcheck=False)
        return matrix

    def _matrix_size(self, matrix):
        """
        Returns the size of the matrix
        """
        (x,y) = matrix.shape
        return x

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
            self.matrix = self._create_matrix() 
        else:
            new_index = self._matrix_size(self.matrix)
            self.matrix = self._grow_matrix(self.matrix)

        new_state.index = new_index
        self.states[new_state] = new_index
        return new_state

    def is_absorbing(self):
        """
        Returns True if the chain represents an absorbing Markov chain.  The
        two requirements of an absorbing Markov chain are that (1) there is at
        least one absorbing state, with no outgoing transitions, and (2) it is
        possible to transition from any state to at least one absorbing state in
        a finite number of steps
        """
        (absorbing, transient, unknown) = self._analyze_for_absorbing()
        return len(unknown) == 0

    def _analyze_for_absorbing(self):
        absorbing_states = set([state for state in self.states
                                if self._is_absorbing_state(state)])
        
        transient_states = set()
        
        progress=True
        while progress:
            unknown_states = set(self.states) - absorbing_states \
                             - transient_states
            known_states = absorbing_states | transient_states
            progress=False
            for state in unknown_states:
                for known in known_states:
                    trans = self.get_transition(state, known)
                    if not self._is_zero(trans):
                        transient_states.add(state)
                        progress=True
                        break
       
        return (absorbing_states, transient_states, unknown_states)
        
    def _swap_indices(self, matrix, index1, index2):
        # Swap rows
        temp = np.copy(matrix[index2,:])
        matrix[index2,:] = matrix[index1,:]
        matrix[index1,:] = temp
        
        # Swap columns
        temp = np.copy(matrix[:,index2])
        matrix[:,index2] = matrix[:,index1]
        matrix[:,index1] = temp
                
    def get_absorbing_probabilities(self):
        (absorbing, transient, unknown) = self._analyze_for_absorbing()
        if len(unknown) != 0:
            raise Error("The matrix is not an absorbing matrix")
        
        matrix = self._fill_in_diagonal_transistions(self.matrix)
            
        state_to_index = {}
        index_to_state = {}
        for state in self.states:
            state_to_index[state] = state.index
            index_to_state[state.index] = state
            
        cannonical = matrix.copy()

        def move_state_to_index(s, new_index):
            old_index = state_to_index[s]
            old_state = index_to_state[new_index]
            index_to_state[new_index] = s
            state_to_index[s] = new_index
            index_to_state[old_index] = old_state
            state_to_index[old_state] = old_index
            self._swap_indices(cannonical, new_index, old_index)

        new_index = 0
        for s in transient:
            move_state_to_index(s, new_index)
            new_index = new_index + 1

        for a in absorbing:
            move_state_to_index(a, new_index)
            new_index = new_index + 1
            
        trans_count = len(transient)
        q = cannonical[:trans_count,:trans_count]
        fund = npl.inv(np.eye(trans_count) - q)
        r = cannonical[trans_count:,:trans_count]
        
        probs = (r * fund)
        result = {}
        for t in transient:
            result[t] = {}
            for a in absorbing:
                absorbing_index=state_to_index[a]-trans_count
                result[t][a] = probs[absorbing_index, state_to_index[t]] 
        return result
                

    def _is_zero(self, trans):
        return np.float64(trans) == self._get_zero()
        
    def _is_absorbing_state(self, state):
        for end_state in [x for x in self.states if x != state]:
            trans = self.get_transition(state, end_state) 
            if not self._is_zero(trans):
                return False
                
        return True
            
    def get_state(self, label):
        if label in self.states_by_label:
            return self.states_by_label[label]
        else:
            return None
    
    def _get_zero(self):
        return npf64_zero

    def _set_transition(self, matrix, row, col, chance):
        npf64_chance = np.float64(chance)
        if npf64_chance < npf64_zero or npf64_chance > npf64_chance:
            raise Exception("The chance of the state transition must not be " +
                            "less than 0 or greater than 1, but the value " + 
                            repr(chance) + " was provided")
        
        matrix[row, col] = npf64_chance
        
    def set_transition(self, from_state, to_state, chance):
        if from_state.index == to_state.index:
            raise Exception("The from_state and to_state much be different")

        self._set_transition(self.matrix, to_state.index,
                             from_state.index, chance)

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

    def get_end_states(self):
        """
        Return the states that have no outgoing transistions
        """
        end_states = []
        for start in self.states:
            is_end = True
            for end in self.states:
                if end == start:
                    continue

                if self.get_transition(start,end) != self._get_zero():
                    is_end = False
                    break
            
            if is_end:
                end_states.append(start)

        return end_states 
                
class State(object):
    def __init__(self, label=None):
        self.label = label
    
    def __str__(self):
        if self.label is not None:
            return str(self.label)
        else:
            return object.__str__(self)
