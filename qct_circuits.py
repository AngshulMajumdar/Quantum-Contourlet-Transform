"""Circuit constructors used by the QCT FakeBrisbane reproducibility study."""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation


def normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=complex)
    nrm = np.linalg.norm(v)
    if nrm == 0:
        raise ValueError("zero vector")
    return v / nrm


def edge_state_4x4() -> np.ndarray:
    image = np.array([
        [1.0, 1.0, 0.20, 0.20],
        [1.0, 1.0, 0.20, 0.20],
        [1.0, 1.0, 0.20, 0.20],
        [1.0, 1.0, 0.20, 0.20],
    ], dtype=float)
    return normalize(image.reshape(-1))


def edge_state_2x2() -> np.ndarray:
    image = np.array([[1.0, 0.20], [1.0, 0.20]], dtype=float)
    return normalize(image.reshape(-1))


def selector_to_basis(qc: QuantumCircuit, selectors: list[int], t: int) -> list[int]:
    flipped: list[int] = []
    for k, qb in enumerate(selectors):
        if ((t >> k) & 1) == 0:
            qc.x(qb)
            flipped.append(qb)
    return flipped


def undo_flips(qc: QuantumCircuit, flipped: list[int]) -> None:
    for qb in reversed(flipped):
        qc.x(qb)


def controlled_increment_mod4(qc: QuantumCircuit, selectors: list[int], reg: list[int], t: int) -> None:
    """Increment a two-qubit little-endian coordinate mod 4 when selector=t."""
    if len(reg) != 2:
        raise ValueError("reproducibility circuit uses two-bit coordinates")
    flipped = selector_to_basis(qc, selectors, t)
    qc.mcx(selectors + [reg[0]], reg[1])
    qc.mcx(selectors, reg[0])
    undo_flips(qc, flipped)


def four_tap_fir_circuit(measure: bool = True) -> QuantumCircuit:
    """Six-qubit four-tap PREP-SELECT-PREP-dagger FIR block encoding."""
    qc = QuantumCircuit(6, 6 if measure else 0, name="four_tap_FIR")
    selector = [0, 1]
    row = [2, 3]
    col = [4, 5]

    qc.append(StatePreparation(edge_state_4x4()), col + row)

    taps = np.array([0.42, -0.31, 0.18, 0.09], dtype=float)
    probabilities = np.abs(taps) / np.sum(np.abs(taps))
    prep = StatePreparation(np.sqrt(probabilities))
    qc.append(prep, selector)

    # The sole negative coefficient is tap 1. Mark selector |01> with a phase.
    qc.x(selector[1])
    qc.cz(selector[0], selector[1])
    qc.x(selector[1])

    # Tap offsets: (0,0), (1,0), (0,1), (1,1).
    controlled_increment_mod4(qc, selector, row, 1)
    controlled_increment_mod4(qc, selector, col, 2)
    controlled_increment_mod4(qc, selector, row, 3)
    controlled_increment_mod4(qc, selector, col, 3)

    qc.append(prep.inverse(), selector)
    if measure:
        qc.measure(range(6), range(6))
    return qc


def reduced_full_qct_circuit(measure: bool = True) -> QuantumCircuit:
    """Four-qubit complete reduced LP -> two-direction DFB structural QCT circuit.

    Qubit layout: q0=row, q1=column, q2=LP band label b, q3=direction label d.
    This circuit is deliberately small: it validates the complete routing structure,
    not the quality of a production contourlet filter bank.
    """
    qc = QuantumCircuit(4, 4 if measure else 0, name="reduced_full_QCT")
    row, col, band, direction = 0, 1, 2, 3
    qc.append(StatePreparation(edge_state_2x2()), [col, row])

    # LP split: H_b -- controlled X_row -- H_b.
    qc.h(band)
    qc.cx(band, row)
    qc.h(band)

    # DFB split only on the bandpass branch b=1.
    qc.ch(band, direction)
    qc.ccx(band, direction, col)
    qc.ch(band, direction)

    if measure:
        qc.measure(range(4), range(4))
    return qc
