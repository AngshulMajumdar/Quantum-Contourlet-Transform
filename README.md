# Quantum Contourlet Transform: Qiskit Aer and FakeBrisbane Reproducibility Repository

This repository provides a compact, executable implementation of the circuit-level ideas behind a Quantum Contourlet Transform (QCT). It focuses on two questions:

1. Can the filtering and routing primitives used by the QCT be written as explicit quantum circuits?
2. What happens to those circuits after compilation and noisy simulation using an IBM-device calibration model?

The code answers these questions with two reproducible experiments built in Qiskit:

- a six-qubit four-tap FIR filter implemented through a PREP-SELECT-PREP-dagger construction;
- a four-qubit reduced end-to-end Laplacian-pyramid-to-directional-filter-bank QCT circuit.

Both circuits are simulated ideally and with Qiskit Aer using `FakeBrisbane`, which provides a device-derived coupling map, native gate set, gate errors, readout errors, and timing information corresponding to an IBM Brisbane calibration snapshot.

The repository is intentionally small enough to run on an ordinary workstation while still exposing the complete circuit construction, compilation path, noise model, output distributions, and resource counts.

## 1. What the QCT is

The classical contourlet transform combines two ideas:

- a Laplacian pyramid (LP) separates an image into low-frequency and bandpass information;
- a directional filter bank (DFB) then decomposes the bandpass component into directional subbands.

The resulting representation is multiscale and directional, making contourlets useful for edges, contours, and anisotropic image structure.

A quantum version must reproduce the same logical sequence using unitary circuit operations. In a full implementation, this requires amplitude-encoded image states, reversible filtering, branch selection, directional routing, and ancilla management. The present repository isolates those operations in circuits that can be inspected, transpiled, and executed in a noisy simulator.

The experiments are not a claim that a production-scale contourlet transform is already practical on current hardware. They are circuit-level feasibility experiments that make the proposed primitives executable and measurable.

## 2. Repository contents

```text
QCT_FakeBrisbane_Reproducibility/
├── README.md
├── qct_circuits.py
├── requirements.txt
├── results/
│   └── README.md
├── run_all.py
├── run_experiments.py
└── verify_install.py
```

There are no hidden dot-prefixed files or directories in the repository.

### `qct_circuits.py`

Defines the image states and both quantum circuits:

- `four_tap_fir_circuit()`
- `reduced_full_qct_circuit()`

### `run_experiments.py`

Runs ideal and FakeBrisbane-derived noisy simulations, transpiles the circuits, computes distributional metrics, records resource counts, and writes the result files.

### `run_all.py`

Runs the complete reproducibility workflow with the default experimental settings.

### `verify_install.py`

Checks the Python environment, imports the required Qiskit packages, constructs `FakeBrisbane`, and verifies that an Aer simulator can be derived from it.

### `results/`

Receives all generated outputs. The numerical files are created at run time rather than being hard-coded into the repository.

## 3. Experiment A: four-tap FIR circuit

The first experiment implements a small finite-impulse-response filtering primitive. The circuit uses six logical qubits:

- two selector qubits;
- two row-coordinate qubits;
- two column-coordinate qubits.

The input is a normalized 4 x 4 edge-like image,

```text
1.0  1.0  0.2  0.2
1.0  1.0  0.2  0.2
1.0  1.0  0.2  0.2
1.0  1.0  0.2  0.2
```

which is amplitude encoded into the four coordinate qubits.

The filter taps are

```text
[0.42, -0.31, 0.18, 0.09]
```

The absolute tap magnitudes define the selector-state preparation probabilities. The negative coefficient is represented by a phase on the corresponding selector branch. Controlled modular increments implement the four spatial offsets

```text
(0, 0), (1, 0), (0, 1), (1, 1)
```

on the row and column registers.

The logical sequence is

```text
image state preparation
        |
selector PREP
        |
coefficient sign phase
        |
controlled spatial SELECT operations
        |
selector PREP-dagger
        |
measurement
```

Postselection on selector state `00` identifies the block-encoding success branch. The experiment compares the conditional output distribution in the ideal simulator with the corresponding distribution under the FakeBrisbane-derived noise model.

The reported metrics are:

- ideal selector-00 success probability;
- noisy selector-00 success probability;
- conditional Hellinger fidelity;
- conditional total variation distance;
- transpiled circuit depth;
- transpiled circuit size;
- native operation counts after FakeBrisbane compilation.

## 4. Experiment B: reduced end-to-end QCT circuit

The second experiment implements a complete reduced LP-to-DFB routing pipeline rather than an isolated filtering primitive.

It uses four logical qubits:

| Qubit | Role |
|---|---|
| q0 | row coordinate |
| q1 | column coordinate |
| q2 | Laplacian-pyramid band label |
| q3 | directional-filter-bank label |

The input is a normalized 2 x 2 edge state,

```text
1.0  0.2
1.0  0.2
```

The LP split is implemented as

```text
H(band)
CX(band, row)
H(band)
```

The directional split is applied only to the bandpass branch:

```text
CH(band, direction)
CCX(band, direction, column)
CH(band, direction)
```

This gives six logical transform operations after state preparation and creates an explicit circuit containing both the multiscale LP routing and the directional DFB routing.

The circuit is deliberately reduced in spatial size so that the complete transformation structure can be compiled and simulated directly. Its purpose is to validate the end-to-end circuit organization and expose the cost introduced by mapping that organization to a realistic backend topology.

The reported metrics are:

- logical qubit count;
- number of logical transform operations;
- ideal-versus-noisy Hellinger fidelity;
- ideal-versus-noisy total variation distance;
- transpiled depth;
- transpiled size;
- native operation counts;
- complete ideal and noisy output counts in the JSON result file.

## 5. FakeBrisbane and Qiskit Aer

`FakeBrisbane` is supplied by the Qiskit IBM Runtime fake-provider package. It reproduces backend information from an IBM Brisbane calibration snapshot without requiring access to the physical quantum processor.

The noisy simulator is constructed with

```python
fake = FakeBrisbane()
noisy = AerSimulator.from_backend(fake)
```

The code therefore uses the fake backend for both transpilation constraints and the Aer noise model.

The simulator is configured with the matrix-product-state method for the noisy runs. All circuits are transpiled with

```text
optimization level = 3
seed_transpiler = 271828
```

and simulated with

```text
shots = 8192
seed_simulator = 271828
```

unless different values are supplied on the command line.

This is noisy simulation derived from a device calibration snapshot. It is not live execution on IBM Brisbane.

## 6. Software environment

The repository pins the Python dependencies used by the experiment:

```text
qiskit==2.5.2
qiskit-aer==0.17.2
qiskit-ibm-runtime==0.50.0
numpy==2.3.5
```

A clean virtual environment is recommended.

Example with Python `venv`:

```bash
python -m venv qctenv
```

On Linux or macOS:

```bash
source qctenv/bin/activate
```

On Windows PowerShell:

```powershell
qctenv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

No IBM Quantum account or API token is required because the experiments use a local fake backend and Qiskit Aer.

## 7. Run the complete experiment

From the repository root:

```bash
python run_all.py
```

This performs two steps:

```text
1. verify the installed Qiskit environment and FakeBrisbane availability
2. run both ideal and noisy circuit experiments
```

The default run uses 8192 shots and seed 271828.

## 8. Run with custom settings

The experiment runner exposes the shot count, random seed, and output directory.

Example:

```bash
python run_experiments.py --shots 16384 --seed 12345 --output-dir results
```

Available arguments:

| Argument | Meaning | Default |
|---|---|---:|
| `--shots` | number of simulator shots | 8192 |
| `--seed` | transpiler and simulator seed | 271828 |
| `--output-dir` | directory for generated results | `results` |

Using the same package versions, backend snapshot, shot count, and seed makes the experiment deterministic to the extent permitted by the simulator and transpiler versions.

## 9. Generated outputs

A successful run creates three files in `results/`.

### `results/RESULTS.md`

Human-readable summary containing:

- software versions;
- backend name and physical qubit count;
- shot count and seed;
- FIR metrics;
- end-to-end QCT metrics;
- transpiled depths, sizes, and native operation counts.

### `results/fake_brisbane_results.json`

Complete machine-readable record of the run. It includes all summary metrics and, for the reduced full QCT experiment, the ideal and noisy measurement counts.

### `results/fake_brisbane_summary.csv`

Flat table containing the scalar metrics from both experiments. This is convenient for spreadsheets, plots, or downstream statistical analysis.

The repository does not contain pre-filled numerical results. Running the code generates the numbers from the installed pinned environment.

## 10. Metrics

### Hellinger fidelity

For discrete probability distributions p and q, the code computes

```text
F_H(p,q) = (sum_x sqrt(p_x q_x))^2
```

A value close to 1 indicates similar distributions.

### Total variation distance

The code computes

```text
TVD(p,q) = 0.5 sum_x |p_x - q_x|
```

A value close to 0 indicates similar distributions.

For the FIR experiment, both metrics are evaluated after conditioning on successful selector postselection. For the reduced end-to-end QCT, the full ideal and noisy measurement distributions are compared directly.

## 11. Resource accounting

The code reports resources after transpilation against the FakeBrisbane-derived Aer backend rather than only counting the high-level logical gates.

For each experiment it records:

- transpiled depth;
- transpiled size;
- native operation counts.

This distinction matters because controlled and multi-controlled logical operations can expand substantially when decomposed into the native instruction set and routed through a restricted coupling graph.

The reduced QCT experiment therefore exposes two different scales of cost:

```text
logical circuit cost
        versus
backend-mapped circuit cost
```

The latter is the more informative quantity for present-day hardware feasibility.

## 12. Reproducibility design

The repository is structured to make the computational experiment auditable rather than opaque.

The main choices are explicit in the source:

- input image amplitudes;
- FIR coefficients;
- selector probabilities;
- selector phase convention;
- spatial offsets;
- LP circuit;
- DFB circuit;
- backend model;
- transpiler optimization level;
- shot count;
- random seed;
- comparison metrics.

No numerical result is embedded in the source code. Output files are generated from the circuits each time the experiment is run.

## 13. What this implementation demonstrates

The repository demonstrates that:

- a signed multi-tap FIR primitive can be expressed as an explicit PREP-SELECT-PREP-dagger circuit;
- the primitive can be compiled against a realistic IBM backend topology and native gate set;
- a complete reduced LP-to-DFB QCT routing pipeline can be constructed as one executable circuit;
- ideal and backend-derived noisy output distributions can be compared quantitatively;
- the growth from logical circuit structure to backend-mapped depth and gate count can be measured directly.

These are circuit-level statements. They avoid treating asymptotic complexity alone as evidence of near-term implementability.

## 14. What this implementation does not claim

This repository does not claim:

- execution on the physical IBM Brisbane processor;
- quantum advantage over a classical contourlet implementation;
- production-scale image dimensions;
- a fully optimized contourlet filter bank;
- fault-tolerant resource estimates;
- error correction;
- end-to-end state preparation at large image sizes;
- that FakeBrisbane noise exactly predicts the behavior of a future live hardware run.

The reduced end-to-end circuit is a structural implementation of the QCT pipeline. It is designed to make the complete transformation executable at a scale where the compiled circuit can be inspected and simulated in full.

## 15. Extending the repository

The code is intentionally modular. Natural extensions include:

- replacing the 2 x 2 reduced state with larger amplitude-encoded images;
- increasing the number of LP scales;
- increasing the number of directional branches;
- substituting longer FIR filters;
- comparing alternative state-preparation methods;
- testing different fake backends;
- running the same circuits on live IBM hardware;
- adding error mitigation;
- recording gate-by-gate error contributions;
- comparing transpiler optimization strategies;
- constructing a larger reversible contourlet filter bank from the same primitives.

The two circuit constructors in `qct_circuits.py` provide the starting point for these experiments.

## 16. Minimal command summary

Install:

```bash
python -m pip install -r requirements.txt
```

Verify:

```bash
python verify_install.py
```

Run everything:

```bash
python run_all.py
```

Run with custom parameters:

```bash
python run_experiments.py --shots 8192 --seed 271828 --output-dir results
```

Inspect:

```text
results/RESULTS.md
results/fake_brisbane_results.json
results/fake_brisbane_summary.csv
```

## 17. Scope

The repository should be read as an executable circuit-level study of a quantum contourlet architecture. The emphasis is on transparent construction, realistic compilation constraints, reproducible noisy simulation, and explicit end-to-end routing at a reduced scale.

The implementation is small by design, but every experimental component is exposed in source form so that it can be checked, modified, and extended without relying on hidden preprocessing or precomputed numerical outputs.
