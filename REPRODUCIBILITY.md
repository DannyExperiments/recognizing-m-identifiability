# Reproducibility

Run from the repository root with Python 3.11 or later.

    python3 -I scripts/verify_repository.py
    python3 -I verification/src/replay.py

The standard-library replay reconstructs and checks all certifications on three satisfying instances with 65, 177 and 217 latent factors. It checks the cut lemma on 4,096 small networks and compares exhaustive search with latent-label peeling on all 256 incidence patterns with four observed nodes and two factors. Two worked graphs exercise the certificate before and after adding the extra latent s. [Recorded replay](verification/results/replay.txt).

Open index.html from the [offline explorer archive](visualization/matching-pivot-explorer.zip) to see the two worked graphs. [Build the paper](paper/BUILD.md).
