# import Qiskit
from qiskit import Aer
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
from qiskit.visualization import plot_histogram, plot_state_city

# import helpers 
import numpy as np
from numpy import pi
import random as rand
import pandas as pd
 
# define initialization
def initialize_s(qc, qubits):
    """Apply a H-gate to 'qubits' in qc"""
    for q in qubits:
        qc.h(q)
    return qc

def func(i, target):
    if i==target:
        return -1
    else:
        return 1

def oracle_matrix(target):
    print("\nOracle Matrix:")
    matrix = np.diag([func(0,target),func(1,target),func(2,target),func(3,target),func(4,target),func(5,target),func(6,target),func(7,target)])
    print(matrix)

# define oracle
def oracle(target):
    qc = QuantumCircuit(3)
    # generate oracle matrix from target
    matrix = np.diag([func(0,target),func(1,target),func(2,target),func(3,target),func(4,target),func(5,target),func(6,target),func(7,target)])
    #----------------------------------#
    qc.unitary(matrix, range(3))
    # return oracle as a gate
    oracle_out = qc.to_gate()
    oracle_out.name = "U$_\omega$"
    return oracle_out

# define diffuser gate
def diffuser(nqubits):
    qc = QuantumCircuit(nqubits)
    # Apply transformation |s> -> |00..0> (H-gates)
    for qubit in range(nqubits):
        qc.h(qubit)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    for qubit in range(nqubits):
        qc.x(qubit)
    # Do multi-controlled-Z gate
    qc.h(nqubits-1)
    qc.mct(list(range(nqubits-1)), nqubits-1)  # multi-controlled-toffoli
    qc.h(nqubits-1)
    # Apply transformation |11..1> -> |00..0>
    for qubit in range(nqubits):
        qc.x(qubit)
    # Apply transformation |00..0> -> |s>
    for qubit in range(nqubits):
        qc.h(qubit)
    # We will return the diffuser as a gate
    U_s = qc.to_gate()
    U_s.name = "$U_s$"
    return U_s

# define grover algorithm
def grover(i):
    '''
    Takes in a target and runs the Grover Search Algorithm
    '''
    print("\nTarget:", i)
    grover_circuit = QuantumCircuit(3)
    grover_circuit = initialize_s(grover_circuit, [0,1,2])
    for a in range(2):
        grover_circuit.barrier()
        grover_circuit.append(oracle(i), [0,1,2])
        grover_circuit.barrier()
        grover_circuit.append(diffuser(3), [0,1,2])
    grover_circuit.measure_all()

    grover_circuit.draw(output='mpl', filename='grovers_algorithm.png')


    backend = Aer.get_backend('qasm_simulator')
    answer = execute(grover_circuit, backend=backend, shots=512).result().get_counts()

    # process
    answers = pd.DataFrame.from_dict(answer.items())

    value = answers.loc[answers[1].idxmax(), 0]

    oracle_matrix(i)
    print("\nReturned item", value, '\n\n')

# ------------------------------------------------------
# ----------------------- SCRIPT -----------------------
# ------------------------------------------------------

for i in range(8):
    grover(i)