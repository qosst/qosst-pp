# Privacy amplification

The privacy amplification procedure of qosst-pp directly uses the [cryptomite](https://github.com/CQCL/cryptomite) library.

We strongly encourage the interested reader to refer to their [documentation](https://cqcl.github.io/cryptomite/) and their [paper](https://quantum-journal.org/papers/q-2025-01-08-1584/). However, we here give a quick introduction.

The goal of privacy amplification is for Alice and Bob, by using an extractor function {math}`G:\{0,1\}^n\rightarrow\{0,1\}^m`, to reduce the eavesdropper's information to {math}`0`, or in practice to a negligible amount {math}`\varepsilon`.

The length of the final key {math}`m` is such that it should be {math}`m=Kn` where {math}`K` is the secret key ratio.

In practice, 2-universal hashing functions are used for privacy amplification, and an example of such is the Toeplitz hashing. A Toeplitz matrix has the following form:

```{math}
T_{n\times n} = \begin{bmatrix}
  a_0 & a_{-1}   & a_{-2} & \cdots & \cdots & a_{-(n-1)} \\
  a_1 & a_0      & a_{-1} & \ddots &        & \vdots \\
  a_2 & a_1      & \ddots & \ddots & \ddots & \vdots \\ 
 \vdots & \ddots & \ddots & \ddots & a_{-1} & a_{-2} \\
 \vdots &        & \ddots & a_1    & a_0    & a_{-1} \\
a_{n-1} & \cdots & \cdots & a_2    & a_1    & a_0
\end{bmatrix}
```

_i.e._ the diagonals are equal to a single element. Such a matrix has {math}`n^2-1` independent coefficients where {math}`n` is the size of the square matrix. While the initial definition is only for square matrix, it can be extended to non-square matrix in the following form:


```{math}
T_{m\times n} = \begin{bmatrix}
  a_0 & a_{-1}   & a_{-2} & \cdots & \cdots & a_{-(n-1)} \\
  a_1 & a_0      & a_{-1} & \ddots &        & \vdots \\
  a_2 & a_1      & \ddots & \ddots & \ddots & \vdots \\ 
 \vdots & \ddots & \ddots & \ddots & a_{-1} & a_{-2} \\
 \vdots &        & \ddots & a_1    & a_0    & a_{-1} \\
a_{m-1} & \cdots & \cdots & a_2    & a_1    & a_0
\end{bmatrix}
```

with this times {math}`n\times m-1` free coefficients. Toeplitz hashing is then performed by generating a {math}`m\times n` random Toeplitz matrix, and multiplying the input {math}`n\times 1` vector to get a {math}`m\times 1` vector, reducing a string of length {math}`n` into length {math}`m`. In the case of binary inputs and outputs all the operation are made modulo 2. Here is an example with {math}`n=4` and {math}`m=3`,

```{math}
h = T\cdot k
= \begin{bmatrix}1 & 1 & 0 & 1 \\0 & 1 & 1 & 0 \\1 & 0 & 1 & 1 \\\end{bmatrix}
\cdot \begin{bmatrix}1\\1\\0\\0\\\end{bmatrix}
= \begin{bmatrix}0 \\1 \\1 \\\end{bmatrix}
```

The hashing function requires a seed, that is used to generate the Toeplitz matrix. In the case of the Toeplitz matrix, a seed of length {math}`n+m-1`, which represents the free coefficients of the matrix. This seed needs to be exchanged on the classical channel for Alice and Bob to use the same Toeplitz extractor.