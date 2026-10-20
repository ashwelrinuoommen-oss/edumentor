"""
Pre-curated sample curricula for instant testing and demonstration of EduMentor.
Covers structured concepts, canonical explanations, key points, and dependency graphs.
"""

from typing import Dict, List, Any, Tuple, Optional


SAMPLE_CURRICULA: Dict[str, Dict[str, Any]] = {
    "Operating Systems: Concurrency & Virtual Memory": {
        "title": "Operating Systems: Concurrency & Virtual Memory",
        "description": "Foundations of modern OS architecture: process scheduling, paging, virtual addressing, synchronization, and deadlock prevention.",
        "concepts": [
            {
                "id": "os_process_scheduling",
                "title": "Process Scheduling",
                "summary": "Core operating system mechanism determining which runnable process in the ready queue is assigned the CPU.",
                "canonical_explanation": "Process Scheduling is an essential operating system mechanism that determines which runnable process in the ready queue is assigned the CPU for execution when the CPU becomes available. In a multi-programming system, multiple processes compete for limited CPU resources. The scheduler switches between processes using context switching, balancing CPU utilization, throughput, turnaround time, waiting time, and responsiveness while preventing process starvation.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_1",
                "module_number": 1,
                "module_title": "Module 1: Process Scheduling",
                "document_id": "doc_os_mod1",
                "source_chunk_ids": ["chk_doc_os_mod1_0", "chk_doc_os_mod1_1"],
                "key_points": [
                    "Selects runnable processes from ready queue to execute on the CPU",
                    "Maximizes CPU utilization and system throughput through multi-programming",
                    "Uses context switching to save and restore process state (registers, program counter)",
                    "Balances turnaround time, waiting time, and prevents starvation"
                ],
                "note_chunks": [
                    "Process Scheduling is an essential operating system mechanism that determines which runnable process in the ready queue is assigned the CPU for execution when the CPU becomes available.",
                    "In a multi-programming system, multiple processes compete for limited CPU resources. The scheduler switches between processes using context switching, balancing CPU utilization, throughput, turnaround time, waiting time, and responsiveness while preventing process starvation."
                ],
                "prompt_question": "In your own words, what is process scheduling and why is it needed in an operating system?"
            },
            {
                "id": "os_virtual_memory",
                "title": "Virtual Memory & Address Spaces",
                "summary": "Hardware and OS abstraction giving each process the illusion of a dedicated, continuous address space.",
                "canonical_explanation": "Virtual Memory is a memory management capability of an operating system that uses hardware (MMU) and software to map virtual addresses used by an application into physical addresses in computer memory. It provides memory protection, isolation between processes, and allows systems to execute programs larger than physical RAM via swapping/paging.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_2",
                "module_number": 2,
                "module_title": "Module 2: Virtual Memory & Paging",
                "document_id": "doc_os_mod2",
                "source_chunk_ids": ["chk_doc_os_mod2_0"],
                "key_points": [
                    "Isolates process address spaces preventing corruption between programs",
                    "Translates virtual addresses to physical RAM addresses via Page Tables and MMU",
                    "Enables executing programs larger than physical memory size",
                    "Provides memory protection bits (read, write, execute)"
                ],
                "prompt_question": "Explain the concept of Virtual Memory. Why do operating systems use it instead of giving programs direct access to physical RAM?"
            },
            {
                "id": "os_paging",
                "title": "Paging & Page Tables",
                "summary": "Fixed-size block allocation dividing virtual memory into pages and physical memory into page frames.",
                "canonical_explanation": "Paging divides a process's virtual address space into fixed-size chunks called pages, and physical RAM into frames of the same size. The OS maintains a Page Table per process that maps page numbers to frame numbers. The Memory Management Unit (MMU) uses the Translation Lookaside Buffer (TLB) to cache these translations for high-speed hardware lookups.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_2",
                "module_number": 2,
                "module_title": "Module 2: Virtual Memory & Paging",
                "document_id": "doc_os_mod2",
                "source_chunk_ids": ["chk_doc_os_mod2_1"],
                "key_points": [
                    "Divides virtual address into Virtual Page Number (VPN) and offset",
                    "Eliminates external fragmentation by using uniform fixed-size frames",
                    "Requires multi-level page tables to manage sparse address spaces efficiently",
                    "TLB (Translation Lookaside Buffer) caches recent translations to prevent memory access latency"
                ],
                "prompt_question": "How does Paging work? Describe the roles of pages, frames, the Page Table, and the TLB."
            },
            {
                "id": "os_page_faults",
                "title": "Page Faults & Replacement Algorithms",
                "summary": "Handling accesses to unmapped or swapped-out pages and choosing victim frames (LRU, FIFO).",
                "canonical_explanation": "A Page Fault is a hardware trap raised by the MMU when a program accesses a virtual page that has its valid bit set to 0 (either not yet allocated or paged out to disk). The OS trap handler halts the thread, reads the missing page from disk into a free RAM frame (using replacement algorithms like LRU or Clock if memory is full), updates the page table, and restarts the instruction.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_2",
                "module_number": 2,
                "module_title": "Module 2: Virtual Memory & Paging",
                "document_id": "doc_os_mod2",
                "source_chunk_ids": ["chk_doc_os_mod2_2"],
                "key_points": [
                    "Triggered by MMU when valid/present bit in page table entry is false",
                    "OS suspends faulting process, initiates disk I/O, and switches context",
                    "Uses eviction policies like LRU (Least Recently Used) or Clock algorithm when RAM is full",
                    "Excessive page faulting leads to thrashing where the CPU spends all time swapping"
                ],
                "prompt_question": "What happens step-by-step when a Page Fault occurs? How does the OS resolve it and resume execution?"
            },
            {
                "id": "os_threads_concurrency",
                "title": "Threads & Race Conditions",
                "summary": "Lightweight execution units sharing memory, and the bugs that arise when simultaneous accesses conflict.",
                "canonical_explanation": "Threads are independent sequences of execution within a single process that share the same code, data, and heap, but maintain private stacks and registers. Concurrency introduces Race Conditions, which occur when multiple threads access shared memory concurrently and at least one access is a write, causing the final state to depend unpredictably on thread scheduling.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_3",
                "module_number": 3,
                "module_title": "Module 3: Concurrency & Threads",
                "document_id": "doc_os_mod3",
                "source_chunk_ids": ["chk_doc_os_mod3_0"],
                "key_points": [
                    "Threads share address space (heap, global variables, file descriptors) but have private stacks",
                    "Lighter overhead to create and context-switch compared to full processes",
                    "Race condition: timing-dependent non-deterministic bug from unsynchronized shared memory writes",
                    "Critical Section: portion of code accessing shared resources that must be executed atomically"
                ],
                "prompt_question": "What is the difference between a process and a thread, and how does concurrent memory access lead to a race condition?"
            },
            {
                "id": "os_mutex_deadlock",
                "title": "Synchronization (Mutexes & Semaphores) & Deadlock",
                "summary": "Techniques for mutual exclusion, and the Coffman conditions that produce unresolvable deadlocks.",
                "canonical_explanation": "Mutual exclusion locks (Mutexes) and Semaphores enforce synchronization by ensuring only one or an allowed quota of threads enter a critical section. Deadlock is a state where a set of threads are permanently blocked because each is holding a resource and waiting for another held by another thread. The four Coffman conditions required for deadlock are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_4",
                "module_number": 4,
                "module_title": "Module 4: Synchronization & Deadlocks",
                "document_id": "doc_os_mod4",
                "source_chunk_ids": ["chk_doc_os_mod4_0"],
                "key_points": [
                    "Mutex provides binary mutual exclusion; Semaphores maintain an integer counter for resource quotas",
                    "Deadlock occurs when threads cycle in mutual waiting with un-preemptable resources",
                    "The four Coffman conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait",
                    "Preventing deadlock requires breaking at least one Coffman condition (e.g. strict lock ordering)"
                ],
                "prompt_question": "Explain how a Mutex solves race conditions, and describe the 4 Coffman conditions required for a Deadlock to occur."
            }
        ],
        "dependencies": [
            ("os_process_scheduling", "os_virtual_memory"),
            ("os_process_scheduling", "os_threads_concurrency"),
            ("os_virtual_memory", "os_paging"),
            ("os_paging", "os_page_faults"),
            ("os_threads_concurrency", "os_mutex_deadlock")
        ]
    },
    "Machine Learning Foundations: From Gradients to Regularization": {
        "title": "Machine Learning Foundations: From Gradients to Regularization",
        "description": "Essential mathematical foundations: loss surfaces, gradient descent, logistic classification, and generalization.",
        "concepts": [
            {
                "id": "ml_loss_functions",
                "title": "Loss Functions & Optimization Surfaces",
                "summary": "Quantifying prediction error (MSE, Cross-Entropy) to formulate learning as an optimization problem.",
                "canonical_explanation": "A Loss Function measures the discrepancy between predicted values and ground truth targets for a given set of model parameters. For regression, Mean Squared Error (MSE) provides a convex quadratic surface. For probabilistic classification, Binary Cross-Entropy evaluates the negative log-likelihood of correct class probabilities. Training is formulated as finding parameters that minimize this loss over the dataset.",
                "key_points": [
                    "Quantifies error mathematically: e.g. MSE for continuous targets, Cross-Entropy for probabilities",
                    "Convex loss functions guarantee a global minimum without local traps",
                    "Differentiability allows using calculus-based gradient descent optimization",
                    "Loss drives the backpropagation update signal"
                ],
                "prompt_question": "Why do we need a Loss Function in machine learning? Compare MSE with Cross-Entropy loss."
            },
            {
                "id": "ml_gradient_descent",
                "title": "Gradient Descent & Learning Rate",
                "summary": "Iterative parameter updating following the negative gradient vector of the loss function.",
                "canonical_explanation": "Gradient Descent is a first-order iterative optimization algorithm for finding the minimum of a differentiable function. It computes the partial derivatives of the loss with respect to each model parameter (the gradient vector) and updates parameters in the opposite direction scaled by a learning rate hyperparameter: theta = theta - eta * grad(L). Variants include Batch GD, Stochastic GD (SGD), and Mini-batch GD.",
                "key_points": [
                    "Gradient vector points in direction of steepest ascent; stepping opposite minimizes loss",
                    "Learning rate (eta) determines step size: too high diverges, too low converges sluggishly",
                    "Stochastic Gradient Descent (SGD) introduces noise that helps escape saddle points",
                    "Mini-batch GD balances computational GPU vectorization with gradient stability"
                ],
                "prompt_question": "Explain how Gradient Descent updates model weights. What happens if the learning rate is either too large or too small?"
            },
            {
                "id": "ml_logistic_regression",
                "title": "Logistic Regression & Sigmoid Activation",
                "summary": "Binary classification using a linear combination passed through a non-linear sigmoid link function.",
                "canonical_explanation": "Logistic Regression models the probability that a given input belongs to a binary class. It computes a linear combination of inputs z = w^T x + b and squashes it into the range [0, 1] using the logistic sigmoid function sigma(z) = 1 / (1 + exp(-z)). The decision boundary is the hyperplane where probability equals 0.5 (z = 0), and optimization is performed by maximizing log-likelihood (minimizing cross-entropy).",
                "key_points": [
                    "Squashes unbounded real numbers into a valid probability between 0 and 1",
                    "Decision boundary is linear: w^T x + b = 0",
                    "Optimized using Cross-Entropy loss rather than MSE to maintain convexity",
                    "Odds ratio: exp(w_i) represents the multiplicative change in odds per unit increase in x_i"
                ],
                "prompt_question": "How does Logistic Regression transform linear regression into a probabilistic classifier? Explain the role of the Sigmoid function."
            },
            {
                "id": "ml_overfitting_regularization",
                "title": "Overfitting, Underfitting & L1/L2 Regularization",
                "summary": "The bias-variance tradeoff and parameter shrinkage techniques (Lasso, Ridge) to improve generalization.",
                "canonical_explanation": "Overfitting occurs when a model with excessive capacity memorizes noise and idiosyncrasies of the training data, resulting in low training error but high test error (high variance). Regularization penalizes model complexity by adding a norm penalty to the loss function. L2 regularization (Ridge) adds the sum of squared weights, shrinking weights smoothly towards zero. L1 regularization (Lasso) adds the sum of absolute weights, driving uninformative weights strictly to zero for feature selection.",
                "key_points": [
                    "Overfitting = low training loss, high validation loss (high variance)",
                    "L2 (Ridge) penalty: lambda * sum(w_i^2), shrinks weights evenly and handles collinearity",
                    "L1 (Lasso) penalty: lambda * sum(|w_i|), produces sparse weight vectors (feature selection)",
                    "Hyperparameter lambda controls the balance between fitting data and keeping weights small"
                ],
                "prompt_question": "Explain the difference between L1 (Lasso) and L2 (Ridge) regularization and how they prevent overfitting."
            }
        ],
        "dependencies": [
            ("ml_loss_functions", "ml_gradient_descent"),
            ("ml_gradient_descent", "ml_logistic_regression"),
            ("ml_loss_functions", "ml_overfitting_regularization")
        ]
    },
    "System Design: Scalability, Caching & Distributed Consensus": {
        "title": "System Design: Scalability, Caching & Distributed Consensus",
        "description": "High-scale backend architectures: load balancing, consistent hashing, caching hierarchies, CAP theorem, and distributed consensus.",
        "concepts": [
            {
                "id": "sys_load_balancing",
                "title": "Load Balancing & Reverse Proxies",
                "summary": "Distributing incoming client network requests evenly across a pool of backend servers to prevent hotspots.",
                "canonical_explanation": "A Load Balancer acts as a reverse proxy sitting between clients and server pools, distributing incoming traffic using algorithms like Round Robin, Least Connections, or IP Hash. It provides high availability via continuous health checks, SSL termination, and horizontal scalability by allowing server instances to be added or removed dynamically without client reconfiguration.",
                "key_points": [
                    "Distributes network traffic across server clusters to eliminate single points of failure",
                    "Monitors node health to route traffic only to responsive instances",
                    "Supports Layer 4 (TCP transport) and Layer 7 (HTTP application) routing",
                    "Enables horizontal scaling and zero-downtime rolling deployments"
                ],
                "prompt_question": "How does a Load Balancer improve system reliability and throughput? Contrast Layer 4 with Layer 7 load balancing."
            },
            {
                "id": "sys_consistent_hashing",
                "title": "Consistent Hashing & Virtual Nodes",
                "summary": "Partitioning strategy that maps both servers and keys onto a circular hash ring to minimize rebalancing.",
                "canonical_explanation": "Consistent Hashing maps data keys and server nodes to a circular hash ring (0 to 2^32-1) using a uniform hash function. When a key is queried, the system walks clockwise to the first node encountered. Adding or removing a server only reassigns k/n keys on average (where k is total keys and n is node count), drastically reducing data migration. Virtual nodes map each physical node to multiple points on the ring to guarantee balanced load distribution.",
                "key_points": [
                    "Maps keys and server nodes onto a circular 360-degree hash ring",
                    "Minimizes key migration to k/n when nodes join or leave, preventing cache stampedes",
                    "Uses Virtual Nodes (tokens) per physical server to avoid uneven load skew (hotspots)",
                    "Forms the backbone of distributed key-value stores like DynamoDB and Cassandra"
                ],
                "prompt_question": "Explain how Consistent Hashing works. Why does traditional modular hashing (key % N) fail when scaling distributed caches?"
            },
            {
                "id": "sys_distributed_caching",
                "title": "Distributed Caching (Cache-Aside, Write-Through, Eviction)",
                "summary": "In-memory caching layers (Redis, Memcached) to achieve sub-millisecond read latencies.",
                "canonical_explanation": "Distributed Caching places high-speed in-memory datastores (e.g. Redis, Memcached) in front of persistent databases. Common caching strategies include Cache-Aside (application reads cache, on miss fetches DB and populates cache), Write-Through (writes update cache and DB synchronously), and Write-Back (writes update cache immediately and asynchronously batch-flush to DB). Eviction policies like LRU, LFU, or TTL prevent memory exhaustion.",
                "key_points": [
                    "Serves reads in sub-millisecond latency from RAM rather than disk I/O",
                    "Cache-Aside pattern separates application read logic from storage engine",
                    "Eviction policies (LRU, LFU, TTL expiration) bound cache memory usage",
                    "Mitigates cache stampedes and thundering herds via locking or pre-warming"
                ],
                "prompt_question": "Compare Cache-Aside, Write-Through, and Write-Back caching patterns. What are the trade-offs regarding data consistency and latency?"
            },
            {
                "id": "sys_cap_theorem",
                "title": "CAP Theorem & PACELC Trade-Offs",
                "summary": "Fundamental impossibility result governing consistency, availability, and partition tolerance.",
                "canonical_explanation": "The CAP Theorem proves that a distributed data store can simultaneously provide at most two of three guarantees in the presence of a network partition: Consistency (every read receives the most recent write or an error), Availability (every non-failing node returns a non-error response), and Partition Tolerance (system continues operating despite arbitrary dropped or delayed network messages). Because network partitions are inevitable in real networks, distributed systems must choose between CP and AP. The PACELC theorem extends this by analyzing trade-offs (Latency vs Consistency) during normal non-partition operation.",
                "key_points": [
                    "Network partitions are unavoidable in distributed hardware, so systems must choose CP or AP",
                    "CP systems reject or stall writes during partitions to guarantee linearizable consistency",
                    "AP systems return potentially stale data to ensure continuous client availability",
                    "PACELC theorem: If Partition choose Availability or Consistency; Else choose Latency or Consistency"
                ],
                "prompt_question": "State the CAP Theorem and explain why a distributed system can never achieve both strict Consistency and 100% Availability during a network partition."
            },
            {
                "id": "sys_raft_consensus",
                "title": "Distributed Consensus & Raft Protocol",
                "summary": "Leader election, replicated state machines, and quorum log replication.",
                "canonical_explanation": "Raft is an understandable consensus algorithm designed for replicated state machines across clusters. It decomposes consensus into Leader Election, Log Replication, and Safety. A cluster elects a single Leader via randomized election timers and majority quorum voting. The Leader receives client requests, appends log entries, replicates them to Follower nodes, and commits an entry once a majority of nodes acknowledge receipt, guaranteeing linearizable distributed state.",
                "key_points": [
                    "Requires strict majority quorum (N/2 + 1) to elect leaders and commit log entries",
                    "Uses randomized election timeouts to prevent split-vote deadlocks between candidate nodes",
                    "Log entries flow strictly from Leader to Followers with term-based monotonicity",
                    "Underpins distributed metadata coordination in systems like etcd, Kubernetes, and Kafka KRaft"
                ],
                "prompt_question": "Describe how the Raft consensus algorithm handles Leader Election and Log Replication across nodes."
            }
        ],
        "dependencies": [
            ("sys_load_balancing", "sys_consistent_hashing"),
            ("sys_consistent_hashing", "sys_distributed_caching"),
            ("sys_load_balancing", "sys_cap_theorem"),
            ("sys_cap_theorem", "sys_raft_consensus")
        ]
    },
    "Data Structures & Algorithms: Trees, Graphs & Dynamic Programming": {
        "title": "Data Structures & Algorithms: Trees, Graphs & Dynamic Programming",
        "description": "Core computer science problem-solving structures: BSTs, AVL tree rotations, graph traversals, Dijkstra, and DP memoization.",
        "concepts": [
            {
                "id": "dsa_binary_search_trees",
                "title": "Binary Search Trees (BST) & Invariant Properties",
                "summary": "Hierarchical sorted node organization where left child < root < right child.",
                "canonical_explanation": "A Binary Search Tree (BST) is a node-based binary tree data structure where each node maintains the BST invariant: all keys in the left subtree are strictly less than the node's key, and all keys in the right subtree are strictly greater. In-order traversal of a BST yields keys in ascending sorted order. Search, insertion, and deletion operate in O(h) time, where h is the tree height (O(log n) when balanced, but degrading to O(n) worst-case if degenerate).",
                "key_points": [
                    "BST Invariant: left_subtree < node < right_subtree for all nodes",
                    "In-order traversal produces sorted keys in ascending order",
                    "Search, insertion, and deletion complexity is bounded by height O(h)",
                    "Degenerates into an O(n) linked list when inserting pre-sorted sequential inputs"
                ],
                "prompt_question": "Explain the Binary Search Tree property. What is the time complexity of searching a BST, and what causes worst-case degradation to O(n)?"
            },
            {
                "id": "dsa_avl_tree_rotations",
                "title": "Self-Balancing AVL Trees & Tree Rotations",
                "summary": "Strict height-balanced binary search tree maintaining balance factors between -1 and +1 via rotations.",
                "canonical_explanation": "An AVL Tree is a self-balancing binary search tree where the heights of the two child subtrees of any node differ by at most one (Balance Factor = height(left) - height(right) in {-1, 0, 1}). After insertion or deletion, if a node becomes unbalanced (|BF| > 1), balance is restored in O(1) time using one of four rotations: Left-Left (Single Right), Right-Right (Single Left), Left-Right (Double), or Right-Left (Double), guaranteeing strict O(log n) search bounds.",
                "key_points": [
                    "Balance Factor = height(left) - height(right), strictly maintained in {-1, 0, +1}",
                    "Guarantees worst-case search, insert, and delete performance of strictly O(log n)",
                    "Four rotation cases: Left-Left, Right-Right, Left-Right, and Right-Left",
                    "Local tree rotations rebalance pointers in O(1) time while preserving the BST sorted invariant"
                ],
                "prompt_question": "How does an AVL Tree maintain balance? Describe the Balance Factor and explain when a Left-Right double rotation is needed."
            },
            {
                "id": "dsa_graph_traversals_bfs_dfs",
                "title": "Graph Representations & BFS / DFS Traversals",
                "summary": "Adjacency list/matrix models and queue/stack state exploration.",
                "canonical_explanation": "Graphs consist of vertices connected by directed or undirected edges, represented in memory via Adjacency Lists (O(V+E) space, optimal for sparse graphs) or Adjacency Matrices (O(V^2) space, fast edge lookup). Breadth-First Search (BFS) uses a FIFO queue to explore nodes level-by-level, finding the unweighted shortest path. Depth-First Search (DFS) uses a LIFO call stack or recursion to explore deeply along branches, ideal for cycle detection, topological sorting, and pathfinding.",
                "key_points": [
                    "Adjacency lists optimize memory for sparse graphs (O(V+E)); matrices give O(1) edge lookups",
                    "BFS uses a FIFO queue to discover shortest paths in unweighted graphs level-by-level",
                    "DFS explores paths deeply using recursion/stack, enabling cycle detection and topological sorting",
                    "Visited sets/arrays prevent infinite loops in cyclic graphs"
                ],
                "prompt_question": "Compare Breadth-First Search (BFS) with Depth-First Search (DFS). When would you choose one over the other?"
            },
            {
                "id": "dsa_dijkstra_shortest_path",
                "title": "Dijkstra's Shortest Path Algorithm",
                "summary": "Greedy single-source shortest path algorithm on non-negative weighted graphs using a min-priority heap.",
                "canonical_explanation": "Dijkstra's algorithm finds the shortest path from a single source vertex to all other vertices in a directed or undirected graph with non-negative edge weights. It maintains tentative distances, always greedily selecting the unvisited vertex with the minimum distance using a Min-Priority Queue (Heap). Once selected, it relaxes outgoing edges: if dist[u] + weight(u, v) < dist[v], dist[v] is updated. Its time complexity is O((V + E) log V).",
                "key_points": [
                    "Greedy strategy guarantees optimal shortest paths for graphs with non-negative weights",
                    "Relaxes adjacent edges by updating tentative distance if a shorter path is found",
                    "Min-Priority Queue (Binary Heap) enables efficient selection in O((V + E) log V) time",
                    "Fails on graphs with negative edge weights (which require Bellman-Ford algorithm)"
                ],
                "prompt_question": "Explain how Dijkstra's algorithm works step-by-step. Why does it require edge weights to be non-negative?"
            },
            {
                "id": "dsa_dynamic_programming_memoization",
                "title": "Dynamic Programming: Optimal Substructure & Overlapping Subproblems",
                "summary": "Solving complex recursive optimization problems by storing solutions to overlapping subproblems.",
                "canonical_explanation": "Dynamic Programming (DP) solves complex problems by breaking them down into smaller overlapping subproblems that exhibit optimal substructure (an optimal solution to the problem contains optimal solutions to its subproblems). Rather than recomputing solutions exponentially, DP caches computed results either top-down with recursion and memoization, or bottom-up iteratively using a DP table. This converts exponential O(2^n) recursion into polynomial O(n) or O(n^2) runtime.",
                "key_points": [
                    "Two mandatory properties: Optimal Substructure and Overlapping Subproblems",
                    "Top-down memoization stores recursive subproblem results in a hash map or cache array",
                    "Bottom-up tabulation iteratively builds base cases to target values in a DP array",
                    "Reduces combinatorial exponential runtimes to polynomial time and space"
                ],
                "prompt_question": "What are the two essential characteristics of problems solvable by Dynamic Programming? Contrast Top-Down Memoization with Bottom-Up Tabulation."
            }
        ],
        "dependencies": [
            ("dsa_binary_search_trees", "dsa_avl_tree_rotations"),
            ("dsa_graph_traversals_bfs_dfs", "dsa_dijkstra_shortest_path"),
            ("dsa_graph_traversals_bfs_dfs", "dsa_dynamic_programming_memoization")
        ]
    }
}


def load_sample_curriculum(sample_name: str, db_path: Optional[str] = None) -> bool:
    """Load a pre-configured curriculum into the SQLite database."""
    from edumentor.db import save_document, save_concepts_and_dependencies, DEFAULT_DB_PATH
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    sample = SAMPLE_CURRICULA.get(sample_name)
    if not sample:
        return False

    doc_id = save_document(
        title=sample["title"],
        raw_text=sample["description"],
        file_type="sample",
        db_path=db_path
    )

    save_concepts_and_dependencies(
        document_id=doc_id,
        concepts=sample["concepts"],
        dependencies=sample["dependencies"],
        db_path=db_path
    )
    return True


# Phase 20 Multi-Module Data Structure for Subject Management
SAMPLE_OS_MODULES = [
    {
        "subject_id": "operating_systems",
        "subject_title": "Operating Systems",
        "module_id": "mod_os_1",
        "module_number": 1,
        "title": "Module 1: Process Scheduling",
        "filename": "Operating_Systems_Module_1_Process_Scheduling.pdf",
        "document_id": "doc_os_mod1",
        "text": (
            "Process Scheduling is an essential operating system mechanism that determines which "
            "runnable process in the ready queue is assigned the CPU for execution when the CPU becomes available. "
            "In a multi-programming system, multiple processes compete for limited CPU resources. The scheduler "
            "switches between processes using context switching, balancing CPU utilization, throughput, "
            "turnaround time, waiting time, and responsiveness while preventing process starvation."
        ),
        "concepts": [
            {
                "id": "os_process_scheduling",
                "title": "Process Scheduling",
                "summary": "Core operating system mechanism determining which runnable process in the ready queue is assigned the CPU.",
                "canonical_explanation": "Process Scheduling is an essential operating system mechanism that determines which runnable process in the ready queue is assigned the CPU for execution when the CPU becomes available. In a multi-programming system, multiple processes compete for limited CPU resources. The scheduler switches between processes using context switching, balancing CPU utilization, throughput, turnaround time, waiting time, and responsiveness while preventing process starvation.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_1",
                "module_number": 1,
                "module_title": "Module 1: Process Scheduling",
                "document_id": "doc_os_mod1",
                "source_chunk_ids": ["chk_doc_os_mod1_0", "chk_doc_os_mod1_1"],
                "key_points": [
                    "Selects runnable processes from ready queue to execute on the CPU",
                    "Maximizes CPU utilization and system throughput through multi-programming",
                    "Uses context switching to save and restore process state (registers, program counter)",
                    "Balances turnaround time, waiting time, and prevents starvation"
                ],
                "note_chunks": [
                    "Process Scheduling is an essential operating system mechanism that determines which runnable process in the ready queue is assigned the CPU for execution when the CPU becomes available.",
                    "In a multi-programming system, multiple processes compete for limited CPU resources. The scheduler switches between processes using context switching, balancing CPU utilization, throughput, turnaround time, waiting time, and responsiveness while preventing process starvation."
                ],
                "prompt_question": "In your own words, what is process scheduling and why is it needed in an operating system?"
            }
        ],
        "dependencies": []
    },
    {
        "subject_id": "operating_systems",
        "subject_title": "Operating Systems",
        "module_id": "mod_os_2",
        "module_number": 2,
        "title": "Module 2: Virtual Memory",
        "filename": "Operating_Systems_Module_2_Virtual_Memory.pdf",
        "document_id": "doc_os_mod2",
        "text": (
            "Virtual Memory is a memory management capability of an operating system that uses hardware (MMU) "
            "and software to map virtual addresses used by an application into physical addresses in computer memory. "
            "It provides memory protection, isolation between processes, and allows systems to execute programs "
            "larger than physical RAM via swapping/paging. Paging divides virtual memory into pages and physical memory "
            "into frames, managed by Page Tables and TLB caching. When unmapped memory is accessed, a Page Fault trap occurs."
        ),
        "concepts": [
            {
                "id": "os_virtual_memory",
                "title": "Virtual Memory & Address Spaces",
                "summary": "Hardware and OS abstraction giving each process the illusion of a dedicated, continuous address space.",
                "canonical_explanation": "Virtual Memory is a memory management capability of an operating system that uses hardware (MMU) and software to map virtual addresses used by an application into physical addresses in computer memory. It provides memory protection, isolation between processes, and allows systems to execute programs larger than physical RAM via swapping/paging.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_2",
                "module_number": 2,
                "module_title": "Module 2: Virtual Memory",
                "document_id": "doc_os_mod2",
                "source_chunk_ids": ["chk_doc_os_mod2_0"],
                "key_points": [
                    "Isolates process address spaces preventing corruption between programs",
                    "Translates virtual addresses to physical RAM addresses via Page Tables and MMU",
                    "Enables executing programs larger than physical memory size",
                    "Provides memory protection bits (read, write, execute)"
                ],
                "prompt_question": "Explain the concept of Virtual Memory. Why do operating systems use it instead of giving programs direct access to physical RAM?"
            },
            {
                "id": "os_paging",
                "title": "Paging & Page Tables",
                "summary": "Fixed-size block allocation dividing virtual memory into pages and physical memory into page frames.",
                "canonical_explanation": "Paging divides a process's virtual address space into fixed-size chunks called pages, and physical RAM into frames of the same size. The OS maintains a Page Table per process that maps page numbers to frame numbers. The Memory Management Unit (MMU) uses the Translation Lookaside Buffer (TLB) to cache these translations for high-speed hardware lookups.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_2",
                "module_number": 2,
                "module_title": "Module 2: Virtual Memory",
                "document_id": "doc_os_mod2",
                "source_chunk_ids": ["chk_doc_os_mod2_1"],
                "key_points": [
                    "Divides virtual address into Virtual Page Number (VPN) and offset",
                    "Eliminates external fragmentation by using uniform fixed-size frames",
                    "Requires multi-level page tables to manage sparse address spaces efficiently",
                    "TLB (Translation Lookaside Buffer) caches recent translations to prevent memory access latency"
                ],
                "prompt_question": "How does Paging work? Describe the roles of pages, frames, the Page Table, and the TLB."
            },
            {
                "id": "os_page_faults",
                "title": "Page Faults & Replacement Algorithms",
                "summary": "Handling accesses to unmapped or swapped-out pages and choosing victim frames (LRU, FIFO).",
                "canonical_explanation": "A Page Fault is a hardware trap raised by the MMU when a program accesses a virtual page that has its valid bit set to 0 (either not yet allocated or paged out to disk). The OS trap handler halts the thread, reads the missing page from disk into a free RAM frame (using replacement algorithms like LRU or Clock if memory is full), updates the page table, and restarts the instruction.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_2",
                "module_number": 2,
                "module_title": "Module 2: Virtual Memory",
                "document_id": "doc_os_mod2",
                "source_chunk_ids": ["chk_doc_os_mod2_2"],
                "key_points": [
                    "Triggered by MMU when valid/present bit in page table entry is false",
                    "OS suspends faulting process, initiates disk I/O, and switches context",
                    "Uses eviction policies like LRU (Least Recently Used) or Clock algorithm when RAM is full",
                    "Excessive page faulting leads to thrashing where the CPU spends all time swapping"
                ],
                "prompt_question": "What happens step-by-step when a Page Fault occurs? How does the OS resolve it and resume execution?"
            }
        ],
        "dependencies": [
            ("os_process_scheduling", "os_virtual_memory"),
            ("os_virtual_memory", "os_paging"),
            ("os_paging", "os_page_faults")
        ]
    },
    {
        "subject_id": "operating_systems",
        "subject_title": "Operating Systems",
        "module_id": "mod_os_3",
        "module_number": 3,
        "title": "Module 3: Concurrency & Threads",
        "filename": "Operating_Systems_Module_3_Concurrency_Threads.pdf",
        "document_id": "doc_os_mod3",
        "text": (
            "Threads are independent sequences of execution within a single process that share the same code, data, "
            "and heap, but maintain private stacks and registers. Concurrency introduces Race Conditions, which occur "
            "when multiple threads access shared memory concurrently and at least one access is a write, causing the final "
            "state to depend unpredictably on thread scheduling."
        ),
        "concepts": [
            {
                "id": "os_threads_concurrency",
                "title": "Threads & Race Conditions",
                "summary": "Lightweight execution units sharing memory, and the bugs that arise when simultaneous accesses conflict.",
                "canonical_explanation": "Threads are independent sequences of execution within a single process that share the same code, data, and heap, but maintain private stacks and registers. Concurrency introduces Race Conditions, which occur when multiple threads access shared memory concurrently and at least one access is a write, causing the final state to depend unpredictably on thread scheduling.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_3",
                "module_number": 3,
                "module_title": "Module 3: Concurrency & Threads",
                "document_id": "doc_os_mod3",
                "source_chunk_ids": ["chk_doc_os_mod3_0"],
                "key_points": [
                    "Threads share address space (heap, global variables, file descriptors) but have private stacks",
                    "Lighter overhead to create and context-switch compared to full processes",
                    "Race condition: timing-dependent non-deterministic bug from unsynchronized shared memory writes",
                    "Critical Section: portion of code accessing shared resources that must be executed atomically"
                ],
                "prompt_question": "What is the difference between a process and a thread, and how does concurrent memory access lead to a race condition?"
            }
        ],
        "dependencies": [
            ("os_process_scheduling", "os_threads_concurrency")
        ]
    },
    {
        "subject_id": "operating_systems",
        "subject_title": "Operating Systems",
        "module_id": "mod_os_4",
        "module_number": 4,
        "title": "Module 4: Synchronization & Deadlocks",
        "filename": "Operating_Systems_Module_4_Synchronization_Deadlocks.pdf",
        "document_id": "doc_os_mod4",
        "text": (
            "Mutual exclusion locks (Mutexes) and Semaphores enforce synchronization by ensuring only one or an allowed "
            "quota of threads enter a critical section. Deadlock is a state where a set of threads are permanently blocked "
            "because each is holding a resource and waiting for another held by another thread. The four Coffman conditions "
            "required for deadlock are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait."
        ),
        "concepts": [
            {
                "id": "os_mutex_deadlock",
                "title": "Synchronization (Mutexes & Semaphores) & Deadlock",
                "summary": "Techniques for mutual exclusion, and the Coffman conditions that produce unresolvable deadlocks.",
                "canonical_explanation": "Mutual exclusion locks (Mutexes) and Semaphores enforce synchronization by ensuring only one or an allowed quota of threads enter a critical section. Deadlock is a state where a set of threads are permanently blocked because each is holding a resource and waiting for another held by another thread. The four Coffman conditions required for deadlock are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.",
                "subject_id": "operating_systems",
                "module_id": "mod_os_4",
                "module_number": 4,
                "module_title": "Module 4: Synchronization & Deadlocks",
                "document_id": "doc_os_mod4",
                "source_chunk_ids": ["chk_doc_os_mod4_0"],
                "key_points": [
                    "Mutex provides binary mutual exclusion; Semaphores maintain an integer counter for resource quotas",
                    "Deadlock occurs when threads cycle in mutual waiting with un-preemptable resources",
                    "The four Coffman conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait",
                    "Preventing deadlock requires breaking at least one Coffman condition (e.g. strict lock ordering)"
                ],
                "prompt_question": "Explain how a Mutex solves race conditions, and describe the 4 Coffman conditions required for a Deadlock to occur."
            }
        ],
        "dependencies": [
            ("os_threads_concurrency", "os_mutex_deadlock")
        ]
    }
]

