# Penalty Method for Bilevel Optimization

### Abstract
Bilevel optimization appears in many important machine learning problems, including hyperparmeter tuning, data denoising,  meta-learning, and data poisoning. Different from simultaneous or multi-objective optimization, continuous bilevel optimization requires computing the inverse Hessian of the cost function to get the exact descent direction even for first-order methods. In this paper, we propose an inversion-free method using penalty function to efficiently solve large bilevel problems. We prove convergence of the penalty-based method under mild conditions and show that it computes the exact hypergradients asymptotically. Our method has smaller time and space complexity than forward- and reverse-mode differentiation, which allows us to solve large problems involving deep neural networks with up to 3.8M  upper-level and 1.4M lower-level variables. We apply our algorithm to denoising label noise with MNIST/CIFAR10/SVHN datasets, few-shot learning with Omniglot/Mini-ImageNet datasets, and training-data  poisoning with MNIST/ImageNet datasets. Our method outperforms or is comparable to the previous results in all of these tasks.

### Citing
If you use this package please cite
<pre>
<code>
This is a code block.
</code>
</pre>
