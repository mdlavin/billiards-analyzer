import analyzer.markov as markov
import sympy

class Chain(markov.Chain):
    
    def _create_matrix(self):
        return sympy.Matrix([0])

    def _grow_matrix(self, matrix):
        new_row = sympy.zeros(1, matrix.cols)
        matrix = matrix.row_insert(matrix.rows, new_row)
        new_col = sympy.zeros(matrix.rows, 1)
        matrix = matrix.col_insert(matrix.cols, new_col)
        return matrix

    def _matrix_size(self, matrix):
        return matrix.cols

    def _zero_diagnoal(self, matrix):
        zero_diag = sympy.eye(matrix.rows)
        zero_diag = zero_diag - sympy.ones(matrix.rows, matrix.cols)
        zero_diag = zero_diag * zero_diag
        return matrix * zero_diag
        
    def _fill_in_diagnoal_transitions(self, matrix):
        matrix = self._zero_diagnoal(self.matrix)
        for col in range(matrix.cols):
            matrix[col, col] = 1 - sum(matrix[:,col])
        return matrix

    def _set_transition(self, matrix, row, col, chance):
        matrix[row, col] = chance
        
    def steady_state(self, start_state=None):
        # Initialize the probabilities for transisions to the same state
        matrix = self._fill_in_diagnoal_transitions(self.matrix)

        # Subtract the identity matrix
        matrix = matrix - sympy.eye(matrix.rows)

        # Add a row at the bottom of the matrix for the equation that all
        # variable probabilities must add up to 1
        matrix = matrix.row_insert(matrix.rows, sympy.ones(1, matrix.cols))

        # Add a column for the target values
        matrix = matrix.col_insert(matrix.cols, sympy.zeros(matrix.rows, 1))
        matrix[matrix.rows-1, matrix.cols-1] = 1

        symbols = []
        for col in range(self._matrix_size(self.matrix)):
            symbols.append(sympy.Symbol("col_" + str(col)))
        solution = sympy.solve_linear_system(matrix, *symbols)

        result = {}
        for state in self.states:
            state_index = self.states[state]
            result[state] = solution[symbols[state_index]]
            
        return result
