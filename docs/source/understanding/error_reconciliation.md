# Error reconciliation

The error reconciliation procedure of qosst-pp directly uses the [IR_for_CVQKD](https://github.com/erdemeray/IR_for_CVQKD) open source library.

We strongly encourage the interested reader to refer to their [documentation](https://information-reconciliation-for-cv-qkd.readthedocs.io/en/latest/) and their [paper](https://arxiv.org/abs/2408.00569). However, we here give a quick introduction.

The reconciliation procedure is based on the multi-dimensional reconciliation (MDR) scheme with Low-Density Parity-Check (LDPC) codes. Reverse Reconciliation (RR) is used, meaning that Alice will correct her data to match Bob's.

The procedure is described in the following figure:


```{figure} ../_static/reconciliation.png
---
align: center
---
Schema of the reconciliation procedure. From [the IR_for_CVQKD paper](https://arxiv.org/abs/2408.00569).
```

Bob starts by generating a random codeword {math}`c` (in principle using a Quantum Random Number Generator, QRNG). The syndrome of the codeword {math}`s=Hc` is computed, where {math}`H` is the parity matrix of the LDPC code. The channel message {math}`m` is also computed using the multidimensional scheme, the codeword {math}`c` and Bob's data {math}`Y`. The syndrome {math}`s` and the message {math}`m` are sent to Alice over the classical channel, who attempts to decode it, giving the codeword {math}`\hat{c}`. Alice computes the syndrome of this codeword and if {math}`H\hat{c}\neq s` she knows the decoding was a failure and discard this frame (and tells Bob to discard it as well). In this other case, she computes a hash {math}`h_{\hat{c}}` using a Cyclic Redundancy Check (CRC-32 in this case), and sends the hash to Bob. Upon reception, Bob also compute the hash {math}`h_{c}` of his codeword using the same CRC. If both hashes match, Bob keeps the frame and tells Alice to keep it, and they don't match, Bob discards the frame and tells Alice to discard it as well.