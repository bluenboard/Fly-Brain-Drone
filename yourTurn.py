Your turn
brain.cells(["SomeType"], side="L") finds neurons by cell type. Browse the types in np.unique(brain.cell_type) or look them up on neuPrint (dataset male-cns:v1.0).
brain.stimulate(indices, amount) injects voltage, and brain.step() advances 20 ms and returns which neurons fired.
brain.reset(seed) silences the network and restarts the noise.
To see the same brain play a fighting game, go to sshfighter/.