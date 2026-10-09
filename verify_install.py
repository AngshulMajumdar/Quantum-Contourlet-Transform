#!/usr/bin/env python3
"""Minimal installation and FakeBrisbane availability check."""
import platform
import qiskit
import qiskit_aer
import qiskit_ibm_runtime
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeBrisbane

backend = FakeBrisbane()
simulator = AerSimulator.from_backend(backend)
print("Python:", platform.python_version())
print("Qiskit:", qiskit.__version__)
print("Qiskit Aer:", qiskit_aer.__version__)
print("Qiskit IBM Runtime:", qiskit_ibm_runtime.__version__)
print("Fake backend:", backend.name)
print("Fake backend qubits:", backend.num_qubits)
print("Aer backend derived successfully:", simulator.name)
