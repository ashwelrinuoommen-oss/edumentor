"""
Academic Benchmark Dataset for EduMentor Evaluation Engine (Phase 39).
Contains realistic academic concepts, reference explanations, and student answers
across 5 core Computer Science domains:
1. Operating Systems
2. Computer Networks
3. Database Management Systems (DBMS)
4. Data Structures
5. Software Engineering

Annotated with human expert evaluations (scores, verdicts, feedback, rubrics)
for rigorous validation of Semantic, LLM, and Hybrid scoring engines.
"""

from typing import List, Dict, Any, Optional

ACADEMIC_BENCHMARK_DATASET: List[Dict[str, Any]] = [
    # =========================================================================
    # DOMAIN 1: OPERATING SYSTEMS
    # =========================================================================
    {
        "id": "OS-01-EXC",
        "subject": "Operating Systems",
        "concept": "Virtual Memory & Paging",
        "concept_id": "os_virtual_memory",
        "reference_explanation": (
            "Virtual memory maps process logical addresses to physical RAM frames using page tables "
            "and the hardware Memory Management Unit (MMU). When a requested page is not resident in physical "
            "memory, a page fault occurs, causing the operating system to trap into kernel mode, fetch the required "
            "page from secondary storage into an available physical frame, update the page table, and restart the "
            "instruction. This mechanism provides memory protection, process isolation, and allows processes to exceed physical RAM capacity."
        ),
        "key_points": [
            "Maps logical addresses to physical page frames using page tables and MMU/TLB",
            "Page fault traps to OS kernel to load missing pages from secondary storage",
            "Enables executing programs larger than available physical RAM",
            "Ensures memory isolation and process protection"
        ],
        "student_answer": (
            "Virtual memory separates the logical address space from physical RAM. The CPU issues virtual addresses "
            "which the MMU translates into physical frames using per-process page tables, often accelerated by a TLB cache. "
            "If a program accesses a valid address that isn't currently loaded into a RAM frame, the hardware triggers a "
            "page fault interrupt. The OS steps in, reads the page from disk into a free frame, updates the page table entry, "
            "and resumes the faulting instruction. This protects processes from interfering with each other and allows running large programs."
        ),
        "human_evaluation": {
            "score": 96.0,
            "verdict": "correct",
            "feedback": "Outstanding recall. Accurately details MMU translation, page table role, TLB caching, page fault trap, disk fetching, and process isolation.",
            "rubric_breakdown": {
                "correctness": 98.0,
                "completeness": 95.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "OS-01-PAR",
        "subject": "Operating Systems",
        "concept": "Virtual Memory & Paging",
        "concept_id": "os_virtual_memory",
        "reference_explanation": (
            "Virtual memory maps process logical addresses to physical RAM frames using page tables "
            "and the hardware Memory Management Unit (MMU). When a requested page is not resident in physical "
            "memory, a page fault occurs, causing the operating system to trap into kernel mode, fetch the required "
            "page from secondary storage into an available physical frame, update the page table, and restart the "
            "instruction. This mechanism provides memory protection, process isolation, and allows processes to exceed physical RAM capacity."
        ),
        "key_points": [
            "Maps logical addresses to physical page frames using page tables and MMU/TLB",
            "Page fault traps to OS kernel to load missing pages from secondary storage",
            "Enables executing programs larger than available physical RAM",
            "Ensures memory isolation and process protection"
        ],
        "student_answer": (
            "Virtual memory lets an operating system divide memory into fixed chunks called pages. "
            "The program thinks it has a huge continuous memory space, and the system uses page tables to map "
            "pages to frames in physical RAM. It provides isolation between processes so they don't corrupt each other."
        ),
        "human_evaluation": {
            "score": 68.0,
            "verdict": "almost_correct",
            "feedback": "Understands the basic premise of paging and isolation, but completely omitted the page fault mechanism, secondary storage swapping, and hardware MMU translation.",
            "rubric_breakdown": {
                "correctness": 80.0,
                "completeness": 58.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "OS-01-MIS",
        "subject": "Operating Systems",
        "concept": "Virtual Memory & Paging",
        "concept_id": "os_virtual_memory",
        "reference_explanation": (
            "Virtual memory maps process logical addresses to physical RAM frames using page tables "
            "and the hardware Memory Management Unit (MMU). When a requested page is not resident in physical "
            "memory, a page fault occurs, causing the operating system to trap into kernel mode, fetch the required "
            "page from secondary storage into an available physical frame, update the page table, and restart the "
            "instruction. This mechanism provides memory protection, process isolation, and allows processes to exceed physical RAM capacity."
        ),
        "key_points": [
            "Maps logical addresses to physical page frames using page tables and MMU/TLB",
            "Page fault traps to OS kernel to load missing pages from secondary storage",
            "Enables executing programs larger than available physical RAM",
            "Ensures memory isolation and process protection"
        ],
        "student_answer": (
            "Virtual memory is a special chip you plug into the motherboard to add more physical RAM. "
            "When the computer runs out of memory, it deletes background processes to free up frames in the CPU cache."
        ),
        "human_evaluation": {
            "score": 18.0,
            "verdict": "wrong",
            "feedback": "Major misconception. Confuses virtual memory abstraction with physical hardware upgrade, and incorrectly claims processes are deleted rather than paged to disk.",
            "rubric_breakdown": {
                "correctness": 15.0,
                "completeness": 20.0,
                "misconceptions": [
                    "Virtual memory is a hardware chip rather than an OS/hardware abstraction",
                    "Processes are deleted when memory is full rather than paged/swapped"
                ]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "OS-02-EXC",
        "subject": "Operating Systems",
        "concept": "Deadlocks & Coffman Conditions",
        "concept_id": "os_deadlocks",
        "reference_explanation": (
            "A deadlock is a permanent blocking state where every process in a set is waiting for a resource "
            "held by another process in the same set. Deadlock can occur if and only if all four Coffman conditions "
            "hold simultaneously: Mutual Exclusion (unsharable resources), Hold and Wait (process holding resources "
            "requests others), No Preemption (resources cannot be forcibly confiscated), and Circular Wait (a closed "
            "cycle of dependency exists among waiting processes)."
        ),
        "key_points": [
            "Permanent blocking where processes wait on resources held by each other",
            "Mutual Exclusion: resources cannot be shared simultaneously",
            "Hold and Wait: processes hold resources while awaiting others",
            "No Preemption: resources cannot be forcibly reclaimed",
            "Circular Wait: closed cycle of resource requests"
        ],
        "student_answer": (
            "A deadlock happens when a set of concurrent processes are stuck indefinitely because each process "
            "holds a resource and is blocked waiting for another resource held by another process in the set. "
            "All four Coffman conditions must hold simultaneously: 1. Mutual exclusion, where only one process can use "
            "the resource at a time; 2. Hold and wait, where a process retains already acquired resources while waiting; "
            "3. No preemption, meaning the OS cannot forcibly seize allocated resources; and 4. Circular wait, where "
            "a directed cycle exists such that P0 waits for P1, P1 for P2, and Pn waits for P0."
        ),
        "human_evaluation": {
            "score": 97.0,
            "verdict": "correct",
            "feedback": "Flawless active recall. Clearly defines deadlock and systematically articulates all four Coffman conditions with precise technical definitions.",
            "rubric_breakdown": {
                "correctness": 98.0,
                "completeness": 96.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "OS-02-PAR",
        "subject": "Operating Systems",
        "concept": "Deadlocks & Coffman Conditions",
        "concept_id": "os_deadlocks",
        "reference_explanation": (
            "A deadlock is a permanent blocking state where every process in a set is waiting for a resource "
            "held by another process in the same set. Deadlock can occur if and only if all four Coffman conditions "
            "hold simultaneously: Mutual Exclusion (unsharable resources), Hold and Wait (process holding resources "
            "requests others), No Preemption (resources cannot be forcibly confiscated), and Circular Wait (a closed "
            "cycle of dependency exists among waiting processes)."
        ),
        "key_points": [
            "Permanent blocking where processes wait on resources held by each other",
            "Mutual Exclusion: resources cannot be shared simultaneously",
            "Hold and Wait: processes hold resources while awaiting others",
            "No Preemption: resources cannot be forcibly reclaimed",
            "Circular Wait: closed cycle of resource requests"
        ],
        "student_answer": (
            "Deadlock occurs when processes get frozen in a cycle because process A needs a resource held by B, "
            "and B needs one held by A. It requires circular wait and mutual exclusion to happen."
        ),
        "human_evaluation": {
            "score": 64.0,
            "verdict": "almost_correct",
            "feedback": "Correct intuitive idea and names circular wait and mutual exclusion, but missed the other two critical Coffman conditions: hold-and-wait and no-preemption.",
            "rubric_breakdown": {
                "correctness": 82.0,
                "completeness": 50.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "OS-02-WRG",
        "subject": "Operating Systems",
        "concept": "Deadlocks & Coffman Conditions",
        "concept_id": "os_deadlocks",
        "reference_explanation": (
            "A deadlock is a permanent blocking state where every process in a set is waiting for a resource "
            "held by another process in the same set. Deadlock can occur if and only if all four Coffman conditions "
            "hold simultaneously: Mutual Exclusion (unsharable resources), Hold and Wait (process holding resources "
            "requests others), No Preemption (resources cannot be forcibly confiscated), and Circular Wait (a closed "
            "cycle of dependency exists among waiting processes)."
        ),
        "key_points": [
            "Permanent blocking where processes wait on resources held by each other",
            "Mutual Exclusion: resources cannot be shared simultaneously",
            "Hold and Wait: processes hold resources while awaiting others",
            "No Preemption: resources cannot be forcibly reclaimed",
            "Circular Wait: closed cycle of resource requests"
        ],
        "student_answer": (
            "Deadlock happens when a computer has a deadlock error and turns off the monitor to save electricity. "
            "You prevent it by unlocking the mutex using a password."
        ),
        "human_evaluation": {
            "score": 8.0,
            "verdict": "wrong",
            "feedback": "Completely incorrect. Irrelevant nonsense with zero conceptual grounding in concurrency.",
            "rubric_breakdown": {
                "correctness": 5.0,
                "completeness": 10.0,
                "misconceptions": ["Deadlock turns off monitor", "Mutexes are unlocked with passwords"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },

    # =========================================================================
    # DOMAIN 2: COMPUTER NETWORKS
    # =========================================================================
    {
        "id": "CN-01-EXC",
        "subject": "Computer Networks",
        "concept": "TCP 3-Way Handshake",
        "concept_id": "cn_tcp_handshake",
        "reference_explanation": (
            "The TCP 3-way handshake establishes a reliable, bidirectional transport layer connection between client and server. "
            "1. The client sends a SYN segment with an Initial Sequence Number (ISN_c). "
            "2. The server responds with a SYN-ACK segment, setting ACK = ISN_c + 1 and choosing its own ISN_s. "
            "3. The client replies with an ACK segment, setting ACK = ISN_s + 1. "
            "This exchanges initial sequence numbers, allocates socket buffers, and verifies both transmission and reception directions before data transfer."
        ),
        "key_points": [
            "Step 1: Client sends SYN with initial sequence number (ISN_c)",
            "Step 2: Server replies with SYN-ACK (acknowledging ISN_c and sending ISN_s)",
            "Step 3: Client replies with ACK (acknowledging ISN_s)",
            "Establishes bidirectional reliable communication and synchronizes sequence numbers"
        ],
        "student_answer": (
            "The TCP 3-way handshake creates a reliable connection before data exchange. First, the client sends a SYN packet "
            "containing a randomly chosen initial sequence number. Next, the server acknowledges it by sending SYN-ACK, "
            "where ACK equals the client sequence number plus one, while generating its own initial sequence number. Finally, "
            "the client sends an ACK acknowledging the server's sequence number. Once this step finishes, the TCP connection "
            "is established and application data can safely flow in both directions."
        ),
        "human_evaluation": {
            "score": 98.0,
            "verdict": "correct",
            "feedback": "Mastery level recall. Accurately details the 3 messages (SYN, SYN-ACK, ACK), sequence number increments (+1), and synchronization objective.",
            "rubric_breakdown": {
                "correctness": 99.0,
                "completeness": 97.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "CN-01-PAR",
        "subject": "Computer Networks",
        "concept": "TCP 3-Way Handshake",
        "concept_id": "cn_tcp_handshake",
        "reference_explanation": (
            "The TCP 3-way handshake establishes a reliable, bidirectional transport layer connection between client and server. "
            "1. The client sends a SYN segment with an Initial Sequence Number (ISN_c). "
            "2. The server responds with a SYN-ACK segment, setting ACK = ISN_c + 1 and choosing its own ISN_s. "
            "3. The client replies with an ACK segment, setting ACK = ISN_s + 1. "
            "This exchanges initial sequence numbers, allocates socket buffers, and verifies both transmission and reception directions before data transfer."
        ),
        "key_points": [
            "Step 1: Client sends SYN with initial sequence number (ISN_c)",
            "Step 2: Server replies with SYN-ACK (acknowledging ISN_c and sending ISN_s)",
            "Step 3: Client replies with ACK (acknowledging ISN_s)",
            "Establishes bidirectional reliable communication and synchronizes sequence numbers"
        ],
        "student_answer": (
            "TCP uses a three-way handshake: the client sends a SYN packet to connect, the server sends back a SYN-ACK, "
            "and then the client sends an ACK to confirm. After that, they can start sending web pages."
        ),
        "human_evaluation": {
            "score": 70.0,
            "verdict": "almost_correct",
            "feedback": "Names the 3 packet types correctly, but does not explain WHY sequence numbers are synchronized or how acknowledgment values are incremented.",
            "rubric_breakdown": {
                "correctness": 85.0,
                "completeness": 58.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "CN-01-MIS",
        "subject": "Computer Networks",
        "concept": "TCP 3-Way Handshake",
        "concept_id": "cn_tcp_handshake",
        "reference_explanation": (
            "The TCP 3-way handshake establishes a reliable, bidirectional transport layer connection between client and server. "
            "1. The client sends a SYN segment with an Initial Sequence Number (ISN_c). "
            "2. The server responds with a SYN-ACK segment, setting ACK = ISN_c + 1 and choosing its own ISN_s. "
            "3. The client replies with an ACK segment, setting ACK = ISN_s + 1. "
            "This exchanges initial sequence numbers, allocates socket buffers, and verifies both transmission and reception directions before data transfer."
        ),
        "key_points": [
            "Step 1: Client sends SYN with initial sequence number (ISN_c)",
            "Step 2: Server replies with SYN-ACK (acknowledging ISN_c and sending ISN_s)",
            "Step 3: Client replies with ACK (acknowledging ISN_s)",
            "Establishes bidirectional reliable communication and synchronizes sequence numbers"
        ],
        "student_answer": (
            "In TCP, the handshake is between the client and UDP router. The client broadcasts data packets without waiting, "
            "and if a packet is lost, the router automatically invents a replacement packet."
        ),
        "human_evaluation": {
            "score": 14.0,
            "verdict": "wrong",
            "feedback": "Severe conceptual confusion. Confuses TCP with connectionless UDP broadcast, and invents impossible packet synthesis.",
            "rubric_breakdown": {
                "correctness": 10.0,
                "completeness": 18.0,
                "misconceptions": ["TCP is connectionless broadcast", "Routers invent replacement packets"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "CN-02-EXC",
        "subject": "Computer Networks",
        "concept": "DNS Hierarchical Resolution",
        "concept_id": "cn_dns_resolution",
        "reference_explanation": (
            "Domain Name System (DNS) maps human-readable hostnames to IP addresses using a distributed hierarchical database. "
            "When resolving a query, a local recursive resolver checks its cache; if missing, it queries a Root nameserver ('.'), "
            "which refers it to the Top-Level Domain (TLD) nameserver (e.g. '.com'). The TLD server refers the resolver to the "
            "Authoritative nameserver for that specific domain. The authoritative server provides the actual Resource Record (e.g. A record), "
            "which the resolver caches according to TTL and returns to the client."
        ),
        "key_points": [
            "Translates human hostnames to numerical IP addresses",
            "Hierarchical structure: Root servers -> TLD servers -> Authoritative servers",
            "Recursive resolver queries the hierarchy on behalf of the client",
            "Caching at multiple levels bounded by Time-to-Live (TTL)"
        ],
        "student_answer": (
            "DNS translates domain names like example.com into machine-routable IP addresses. The process starts when the client "
            "asks its local recursive resolver. If the record isn't cached, the recursive resolver performs iterative queries: "
            "first contacting a root DNS server, which delegates to the appropriate TLD server (like .com or .org). The TLD server "
            "then points to the authoritative nameserver that holds the actual zone file. The authoritative server returns the A or AAAA "
            "record, and the resolver caches this response based on its TTL before returning the IP to the client."
        ),
        "human_evaluation": {
            "score": 96.0,
            "verdict": "correct",
            "feedback": "Superb answer. Perfectly differentiates recursive vs iterative roles, traces the exact hierarchy (Root -> TLD -> Authoritative), and notes TTL caching.",
            "rubric_breakdown": {
                "correctness": 97.0,
                "completeness": 95.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "CN-02-PAR",
        "subject": "Computer Networks",
        "concept": "DNS Hierarchical Resolution",
        "concept_id": "cn_dns_resolution",
        "reference_explanation": (
            "Domain Name System (DNS) maps human-readable hostnames to IP addresses using a distributed hierarchical database. "
            "When resolving a query, a local recursive resolver checks its cache; if missing, it queries a Root nameserver ('.'), "
            "which refers it to the Top-Level Domain (TLD) nameserver (e.g. '.com'). The TLD server refers the resolver to the "
            "Authoritative nameserver for that specific domain. The authoritative server provides the actual Resource Record (e.g. A record), "
            "which the resolver caches according to TTL and returns to the client."
        ),
        "key_points": [
            "Translates human hostnames to numerical IP addresses",
            "Hierarchical structure: Root servers -> TLD servers -> Authoritative servers",
            "Recursive resolver queries the hierarchy on behalf of the client",
            "Caching at multiple levels bounded by Time-to-Live (TTL)"
        ],
        "student_answer": (
            "DNS turns domain names into IP addresses. When you type google.com, your computer queries DNS servers "
            "across the internet in a hierarchy to find the IP address, and then your browser connects to that IP."
        ),
        "human_evaluation": {
            "score": 62.0,
            "verdict": "almost_correct",
            "feedback": "Broad high-level understanding, but fails to mention the specific levels of hierarchy (Root, TLD, Authoritative), resolvers, or caching.",
            "rubric_breakdown": {
                "correctness": 80.0,
                "completeness": 48.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "CN-02-WRG",
        "subject": "Computer Networks",
        "concept": "DNS Hierarchical Resolution",
        "concept_id": "cn_dns_resolution",
        "reference_explanation": (
            "Domain Name System (DNS) maps human-readable hostnames to IP addresses using a distributed hierarchical database. "
            "When resolving a query, a local recursive resolver checks its cache; if missing, it queries a Root nameserver ('.'), "
            "which refers it to the Top-Level Domain (TLD) nameserver (e.g. '.com'). The TLD server refers the resolver to the "
            "Authoritative nameserver for that specific domain. The authoritative server provides the actual Resource Record (e.g. A record), "
            "which the resolver caches according to TTL and returns to the client."
        ),
        "key_points": [
            "Translates human hostnames to numerical IP addresses",
            "Hierarchical structure: Root servers -> TLD servers -> Authoritative servers",
            "Recursive resolver queries the hierarchy on behalf of the client",
            "Caching at multiple levels bounded by Time-to-Live (TTL)"
        ],
        "student_answer": (
            "I don't know the exact steps for DNS."
        ),
        "human_evaluation": {
            "score": 0.0,
            "verdict": "wrong",
            "feedback": "Empty / 'I don't know' response. Full score penalty.",
            "rubric_breakdown": {
                "correctness": 0.0,
                "completeness": 0.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },

    # =========================================================================
    # DOMAIN 3: DATABASE MANAGEMENT SYSTEMS (DBMS)
    # =========================================================================
    {
        "id": "DBMS-01-EXC",
        "subject": "DBMS",
        "concept": "ACID Properties of Transactions",
        "concept_id": "dbms_acid_properties",
        "reference_explanation": (
            "ACID properties guarantee reliable transaction processing in database management systems. "
            "Atomicity ensures that all operations in a transaction succeed completely or all are rolled back (all-or-nothing). "
            "Consistency ensures the database transitions from one valid state to another, strictly enforcing all schema constraints. "
            "Isolation ensures that concurrent transactions execute as if they were running serially without intermediate interference. "
            "Durability guarantees that once a transaction commits, its modifications survive crashes, typically via Write-Ahead Logging (WAL)."
        ),
        "key_points": [
            "Atomicity: All-or-nothing execution with rollback on failure",
            "Consistency: Preserves database integrity constraints across states",
            "Isolation: Concurrent transactions execute without mutual interference",
            "Durability: Committed updates persist permanently (e.g. WAL)"
        ],
        "student_answer": (
            "ACID ensures reliable database transactions: "
            "Atomicity means transactions are all-or-nothing; if any query fails, previous changes are rolled back. "
            "Consistency means transaction execution preserves all defined constraints and relational invariants. "
            "Isolation guarantees concurrent transactions don't observe each other's uncommitted modifications, achieved via locking or MVCC. "
            "Durability ensures that once a transaction commits, the changes are permanent on non-volatile disk even if the server crashes right after, usually guaranteed by write-ahead logs."
        ),
        "human_evaluation": {
            "score": 97.0,
            "verdict": "correct",
            "feedback": "Exceptional. Every letter of ACID is accurately defined with mechanisms (rollback, invariants, MVCC/locking, WAL).",
            "rubric_breakdown": {
                "correctness": 98.0,
                "completeness": 96.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DBMS-01-PAR",
        "subject": "DBMS",
        "concept": "ACID Properties of Transactions",
        "concept_id": "dbms_acid_properties",
        "reference_explanation": (
            "ACID properties guarantee reliable transaction processing in database management systems. "
            "Atomicity ensures that all operations in a transaction succeed completely or all are rolled back (all-or-nothing). "
            "Consistency ensures the database transitions from one valid state to another, strictly enforcing all schema constraints. "
            "Isolation ensures that concurrent transactions execute as if they were running serially without intermediate interference. "
            "Durability guarantees that once a transaction commits, its modifications survive crashes, typically via Write-Ahead Logging (WAL)."
        ),
        "key_points": [
            "Atomicity: All-or-nothing execution with rollback on failure",
            "Consistency: Preserves database integrity constraints across states",
            "Isolation: Concurrent transactions execute without mutual interference",
            "Durability: Committed updates persist permanently (e.g. WAL)"
        ],
        "student_answer": (
            "ACID stands for Atomicity, Consistency, Isolation, and Durability. "
            "Atomicity means all or nothing. Durability means data is saved to disk so it won't be lost. "
            "Consistency means the data is always the same across all replicas."
        ),
        "human_evaluation": {
            "score": 66.0,
            "verdict": "almost_correct",
            "feedback": "Good grasp of Atomicity and Durability, but completely omitted Isolation, and gave a distributed consistency definition rather than relational transaction consistency.",
            "rubric_breakdown": {
                "correctness": 75.0,
                "completeness": 55.0,
                "misconceptions": ["Conflated ACID Consistency with distributed replica consistency"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DBMS-01-MIS",
        "subject": "DBMS",
        "concept": "ACID Properties of Transactions",
        "concept_id": "dbms_acid_properties",
        "reference_explanation": (
            "ACID properties guarantee reliable transaction processing in database management systems. "
            "Atomicity ensures that all operations in a transaction succeed completely or all are rolled back (all-or-nothing). "
            "Consistency ensures the database transitions from one valid state to another, strictly enforcing all schema constraints. "
            "Isolation ensures that concurrent transactions execute as if they were running serially without intermediate interference. "
            "Durability guarantees that once a transaction commits, its modifications survive crashes, typically via Write-Ahead Logging (WAL)."
        ),
        "key_points": [
            "Atomicity: All-or-nothing execution with rollback on failure",
            "Consistency: Preserves database integrity constraints across states",
            "Isolation: Concurrent transactions execute without mutual interference",
            "Durability: Committed updates persist permanently (e.g. WAL)"
        ],
        "student_answer": (
            "ACID is a chemical reaction used in hardware manufacturing to etch silicon wafers for SQL databases."
        ),
        "human_evaluation": {
            "score": 5.0,
            "verdict": "wrong",
            "feedback": "Literal pun misunderstanding with zero academic relevance to database transactions.",
            "rubric_breakdown": {
                "correctness": 0.0,
                "completeness": 10.0,
                "misconceptions": ["Believes ACID refers to chemical etching"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DBMS-02-EXC",
        "subject": "DBMS",
        "concept": "B+ Tree Indexing",
        "concept_id": "dbms_bplus_tree",
        "reference_explanation": (
            "A B+ Tree is a self-balancing N-ary search tree optimized for block storage and database indexing. "
            "Unlike standard B-trees, all actual data records (or record pointers) reside exclusively in leaf nodes, "
            "which are doubly linked for high-performance sequential and range scans. Internal nodes hold only router keys "
            "and page pointers, maximizing fan-out, minimizing tree height, and drastically reducing disk I/O operations."
        ),
        "key_points": [
            "Self-balancing balanced search tree optimized for block disk I/O",
            "All data records/pointers are stored exclusively in leaf nodes",
            "Leaf nodes are linked in a list for efficient range queries",
            "Internal nodes store only keys to maximize fan-out and minimize tree height"
        ],
        "student_answer": (
            "B+ Trees are balanced tree data structures tailored for database indexing on disk storage. "
            "Their key feature is that all data pointers or table rows are placed only in leaf nodes, while interior nodes "
            "only store separator keys to guide lookups. This creates a very high branching factor, keeping the tree height shallow "
            "(typically 3 to 4 levels) so lookups need minimal disk page I/Os. Furthermore, leaf nodes are linked together in a linked list, "
            "making range queries (like WHERE age BETWEEN 20 AND 30) extremely fast because the engine just scans sequentially across leaves."
        ),
        "human_evaluation": {
            "score": 96.0,
            "verdict": "correct",
            "feedback": "Exemplary explanation. Captures high fan-out, disk I/O reduction, leaf-only data placement, and linked leaf nodes for range scans.",
            "rubric_breakdown": {
                "correctness": 98.0,
                "completeness": 94.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DBMS-02-PAR",
        "subject": "DBMS",
        "concept": "B+ Tree Indexing",
        "concept_id": "dbms_bplus_tree",
        "reference_explanation": (
            "A B+ Tree is a self-balancing N-ary search tree optimized for block storage and database indexing. "
            "Unlike standard B-trees, all actual data records (or record pointers) reside exclusively in leaf nodes, "
            "which are doubly linked for high-performance sequential and range scans. Internal nodes hold only router keys "
            "and page pointers, maximizing fan-out, minimizing tree height, and drastically reducing disk I/O operations."
        ),
        "key_points": [
            "Self-balancing balanced search tree optimized for block disk I/O",
            "All data records/pointers are stored exclusively in leaf nodes",
            "Leaf nodes are linked in a list for efficient range queries",
            "Internal nodes store only keys to maximize fan-out and minimize tree height"
        ],
        "student_answer": (
            "A B+ tree is like a binary search tree that databases use to find rows fast. "
            "It stays balanced so searching takes O(log n) time."
        ),
        "human_evaluation": {
            "score": 58.0,
            "verdict": "almost_correct",
            "feedback": "Misses the core defining attributes of B+ trees: multi-way branching (not binary), disk block sizing, leaf-only storage, and linked leaves for range queries.",
            "rubric_breakdown": {
                "correctness": 70.0,
                "completeness": 45.0,
                "misconceptions": ["Thinks B+ tree is a binary search tree"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DBMS-02-WRG",
        "subject": "DBMS",
        "concept": "B+ Tree Indexing",
        "concept_id": "dbms_bplus_tree",
        "reference_explanation": (
            "A B+ Tree is a self-balancing N-ary search tree optimized for block storage and database indexing. "
            "Unlike standard B-trees, all actual data records (or record pointers) reside exclusively in leaf nodes, "
            "which are doubly linked for high-performance sequential and range scans. Internal nodes hold only router keys "
            "and page pointers, maximizing fan-out, minimizing tree height, and drastically reducing disk I/O operations."
        ),
        "key_points": [
            "Self-balancing balanced search tree optimized for block disk I/O",
            "All data records/pointers are stored exclusively in leaf nodes",
            "Leaf nodes are linked in a list for efficient range queries",
            "Internal nodes store only keys to maximize fan-out and minimize tree height"
        ],
        "student_answer": (
            "B+ tree is an algorithm that calculates grades for computer science students in university."
        ),
        "human_evaluation": {
            "score": 5.0,
            "verdict": "wrong",
            "feedback": "Completely irrelevant joke answer.",
            "rubric_breakdown": {
                "correctness": 0.0,
                "completeness": 10.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },

    # =========================================================================
    # DOMAIN 4: DATA STRUCTURES
    # =========================================================================
    {
        "id": "DS-01-EXC",
        "subject": "Data Structures",
        "concept": "AVL Tree Balancing & Rotations",
        "concept_id": "ds_avl_trees",
        "reference_explanation": (
            "An AVL tree is a self-balancing binary search tree where the height difference (balance factor = height(left) - height(right)) "
            "between the left and right subtrees of every node is at most 1 (-1, 0, or 1). When an insertion or deletion violates this property, "
            "the tree executes tree rotations to restore balance: single rotations (Left-Left or Right-Right) for linear imbalances, or "
            "double rotations (Left-Right or Right-Left) for zigzag imbalances. This guarantees strictly O(log n) worst-case time for search, insert, and delete."
        ),
        "key_points": [
            "Strict height balance factor: balance factor in {-1, 0, 1}",
            "Single rotations: Left-Left (Right rotation) and Right-Right (Left rotation)",
            "Double rotations: Left-Right and Right-Left for zigzag imbalances",
            "Guarantees O(log n) worst-case search, insertion, and deletion"
        ],
        "student_answer": (
            "An AVL tree is a self-balancing binary search tree that enforces a balance factor for every node, "
            "defined as height of left subtree minus height of right subtree. The balance factor must stay within {-1, 0, 1}. "
            "If an insertion causes an imbalance of +/-2, it triggers rotations: single rotations (LL or RR) when the insertion is in an "
            "outer subtree, and double rotations (LR or RL) when the insertion creates a zigzag shape in an inner subtree. "
            "Because height is strictly maintained around 1.44 log2(n), operations like search, insertion, and deletion are guaranteed O(log n)."
        ),
        "human_evaluation": {
            "score": 97.0,
            "verdict": "correct",
            "feedback": "Outstanding precision. Mentions exact balance factor formula, domain {-1, 0, 1}, single vs double rotations, and O(log n) guarantees.",
            "rubric_breakdown": {
                "correctness": 99.0,
                "completeness": 95.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DS-01-PAR",
        "subject": "Data Structures",
        "concept": "AVL Tree Balancing & Rotations",
        "concept_id": "ds_avl_trees",
        "reference_explanation": (
            "An AVL tree is a self-balancing binary search tree where the height difference (balance factor = height(left) - height(right)) "
            "between the left and right subtrees of every node is at most 1 (-1, 0, or 1). When an insertion or deletion violates this property, "
            "the tree executes tree rotations to restore balance: single rotations (Left-Left or Right-Right) for linear imbalances, or "
            "double rotations (Left-Right or Right-Left) for zigzag imbalances. This guarantees strictly O(log n) worst-case time for search, insert, and delete."
        ),
        "key_points": [
            "Strict height balance factor: balance factor in {-1, 0, 1}",
            "Single rotations: Left-Left (Right rotation) and Right-Right (Left rotation)",
            "Double rotations: Left-Right and Right-Left for zigzag imbalances",
            "Guarantees O(log n) worst-case search, insertion, and deletion"
        ],
        "student_answer": (
            "An AVL tree is a BST that rotates nodes when one branch becomes too long compared to the other. "
            "It keeps the tree balanced so searches don't become O(n)."
        ),
        "human_evaluation": {
            "score": 64.0,
            "verdict": "almost_correct",
            "feedback": "Correct intuition and knows it prevents O(n) skew, but fails to define balance factor values or describe the specific rotation mechanisms (LL, RR, LR, RL).",
            "rubric_breakdown": {
                "correctness": 82.0,
                "completeness": 48.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DS-01-WRG",
        "subject": "Data Structures",
        "concept": "AVL Tree Balancing & Rotations",
        "concept_id": "ds_avl_trees",
        "reference_explanation": (
            "An AVL tree is a self-balancing binary search tree where the height difference (balance factor = height(left) - height(right)) "
            "between the left and right subtrees of every node is at most 1 (-1, 0, or 1). When an insertion or deletion violates this property, "
            "the tree executes tree rotations to restore balance: single rotations (Left-Left or Right-Right) for linear imbalances, or "
            "double rotations (Left-Right or Right-Left) for zigzag imbalances. This guarantees strictly O(log n) worst-case time for search, insert, and delete."
        ),
        "key_points": [
            "Strict height balance factor: balance factor in {-1, 0, 1}",
            "Single rotations: Left-Left (Right rotation) and Right-Right (Left rotation)",
            "Double rotations: Left-Right and Right-Left for zigzag imbalances",
            "Guarantees O(log n) worst-case search, insertion, and deletion"
        ],
        "student_answer": (
            "AVL trees balance by sorting all items into a linked list and picking the middle element every millisecond."
        ),
        "human_evaluation": {
            "score": 12.0,
            "verdict": "wrong",
            "feedback": "Blatantly incorrect. Confuses AVL tree with repeated array middle-picking.",
            "rubric_breakdown": {
                "correctness": 10.0,
                "completeness": 15.0,
                "misconceptions": ["Converts to linked list continuously"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DS-02-EXC",
        "subject": "Data Structures",
        "concept": "Hash Table Collision Resolution",
        "concept_id": "ds_hash_collisions",
        "reference_explanation": (
            "Hash tables map arbitrary keys to bucket indices using a hash function. A collision occurs when two distinct keys produce the same index. "
            "Primary resolution strategies include: "
            "1. Separate Chaining: Each bucket holds a secondary data structure (linked list or self-balancing tree) storing all colliding elements. "
            "2. Open Addressing: All elements reside directly in the bucket array; on collision, the algorithm probes alternative slots using linear probing, "
            "quadratic probing, or double hashing. Performance depends on maintaining a healthy load factor (alpha = n/m)."
        ),
        "key_points": [
            "Collisions occur when two distinct keys yield identical bucket hashes",
            "Separate Chaining: Buckets store linked lists or red-black trees",
            "Open Addressing: Probes array slots via linear, quadratic, or double hashing",
            "Load factor management (resizing when threshold exceeded)"
        ],
        "student_answer": (
            "In hash tables, collisions occur when two different keys map to the same bucket index via the hash function. "
            "The two main ways to resolve them are separate chaining and open addressing. In separate chaining, each bucket contains a linked list "
            "or balanced tree holding colliding entries. In open addressing, all elements live directly in the table array; when a collision happens, "
            "the algorithm searches for the next available slot using linear probing, quadratic probing, or double hashing. "
            "Both methods rely on keeping the load factor low (typically under 0.7) by rehashing and resizing when needed."
        ),
        "human_evaluation": {
            "score": 96.0,
            "verdict": "correct",
            "feedback": "Comprehensive and technically accurate. Explains collision cause, contrasts chaining vs open addressing, lists probing variants, and identifies load factor resizing.",
            "rubric_breakdown": {
                "correctness": 98.0,
                "completeness": 95.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DS-02-PAR",
        "subject": "Data Structures",
        "concept": "Hash Table Collision Resolution",
        "concept_id": "ds_hash_collisions",
        "reference_explanation": (
            "Hash tables map arbitrary keys to bucket indices using a hash function. A collision occurs when two distinct keys produce the same index. "
            "Primary resolution strategies include: "
            "1. Separate Chaining: Each bucket holds a secondary data structure (linked list or self-balancing tree) storing all colliding elements. "
            "2. Open Addressing: All elements reside directly in the bucket array; on collision, the algorithm probes alternative slots using linear probing, "
            "quadratic probing, or double hashing. Performance depends on maintaining a healthy load factor (alpha = n/m)."
        ),
        "key_points": [
            "Collisions occur when two distinct keys yield identical bucket hashes",
            "Separate Chaining: Buckets store linked lists or red-black trees",
            "Open Addressing: Probes array slots via linear, quadratic, or double hashing",
            "Load factor management (resizing when threshold exceeded)"
        ],
        "student_answer": (
            "When two keys hash to the same bucket, it's called a collision. The simplest fix is chaining, "
            "where each bucket has a linked list to store multiple items."
        ),
        "human_evaluation": {
            "score": 67.0,
            "verdict": "almost_correct",
            "feedback": "Correct definition of collision and chaining, but omitted open addressing (linear/quadratic probing) and load factor considerations.",
            "rubric_breakdown": {
                "correctness": 85.0,
                "completeness": 52.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "DS-02-WRG",
        "subject": "Data Structures",
        "concept": "Hash Table Collision Resolution",
        "concept_id": "ds_hash_collisions",
        "reference_explanation": (
            "Hash tables map arbitrary keys to bucket indices using a hash function. A collision occurs when two distinct keys produce the same index. "
            "Primary resolution strategies include: "
            "1. Separate Chaining: Each bucket holds a secondary data structure (linked list or self-balancing tree) storing all colliding elements. "
            "2. Open Addressing: All elements reside directly in the bucket array; on collision, the algorithm probes alternative slots using linear probing, "
            "quadratic probing, or double hashing. Performance depends on maintaining a healthy load factor (alpha = n/m)."
        ),
        "key_points": [
            "Collisions occur when two distinct keys yield identical bucket hashes",
            "Separate Chaining: Buckets store linked lists or red-black trees",
            "Open Addressing: Probes array slots via linear, quadratic, or double hashing",
            "Load factor management (resizing when threshold exceeded)"
        ],
        "student_answer": (
            "A collision means the computer crashed because the hash was too heavy to fit into RAM."
        ),
        "human_evaluation": {
            "score": 10.0,
            "verdict": "wrong",
            "feedback": "Complete misunderstanding of hash collisions.",
            "rubric_breakdown": {
                "correctness": 5.0,
                "completeness": 15.0,
                "misconceptions": ["Believes collision is a computer crash"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },

    # =========================================================================
    # DOMAIN 5: SOFTWARE ENGINEERING
    # =========================================================================
    {
        "id": "SE-01-EXC",
        "subject": "Software Engineering",
        "concept": "SOLID Design Principles",
        "concept_id": "se_solid_principles",
        "reference_explanation": (
            "SOLID is an acronym for five foundational object-oriented design principles: "
            "1. Single Responsibility (SRP): A class should have only one reason to change. "
            "2. Open-Closed (OCP): Software entities should be open for extension, but closed for modification. "
            "3. Liskov Substitution (LSP): Subtypes must be substitutable for their base types without altering correctness. "
            "4. Interface Segregation (ISP): Clients should not be forced to depend on interfaces they do not use. "
            "5. Dependency Inversion (DIP): High-level modules should depend on abstractions (interfaces) rather than concrete implementations."
        ),
        "key_points": [
            "SRP: Single reason to change per class",
            "OCP: Open for extension, closed for modification",
            "LSP: Derived classes must be substitutable for base classes",
            "ISP: Fine-grained, client-specific interfaces rather than fat interfaces",
            "DIP: Depend on abstractions rather than concrete classes"
        ],
        "student_answer": (
            "SOLID represents five core object-oriented principles: "
            "S - Single Responsibility: Every module should do one cohesive job and have one reason to change. "
            "O - Open/Closed: Classes should be open to extend via polymorphism, but closed for modifying existing source code. "
            "L - Liskov Substitution: Child classes must adhere to parent contracts so they can substitute parents without breaking behavior. "
            "I - Interface Segregation: Keep interfaces small and specific so callers aren't burdened with methods they don't need. "
            "D - Dependency Inversion: High-level business logic should depend on abstract interfaces rather than concrete low-level implementations."
        ),
        "human_evaluation": {
            "score": 98.0,
            "verdict": "correct",
            "feedback": "Perfect recall across all five SOLID principles with accurate pedagogical definitions.",
            "rubric_breakdown": {
                "correctness": 99.0,
                "completeness": 97.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "SE-01-PAR",
        "subject": "Software Engineering",
        "concept": "SOLID Design Principles",
        "concept_id": "se_solid_principles",
        "reference_explanation": (
            "SOLID is an acronym for five foundational object-oriented design principles: "
            "1. Single Responsibility (SRP): A class should have only one reason to change. "
            "2. Open-Closed (OCP): Software entities should be open for extension, but closed for modification. "
            "3. Liskov Substitution (LSP): Subtypes must be substitutable for their base types without altering correctness. "
            "4. Interface Segregation (ISP): Clients should not be forced to depend on interfaces they do not use. "
            "5. Dependency Inversion (DIP): High-level modules should depend on abstractions (interfaces) rather than concrete implementations."
        ),
        "key_points": [
            "SRP: Single reason to change per class",
            "OCP: Open for extension, closed for modification",
            "LSP: Derived classes must be substitutable for base classes",
            "ISP: Fine-grained, client-specific interfaces rather than fat interfaces",
            "DIP: Depend on abstractions rather than concrete classes"
        ],
        "student_answer": (
            "SOLID means writing good code. S is single responsibility so a class does one thing. "
            "O is open closed, where code is open for modification and closed for extension. "
            "The rest are about interfaces and dependencies."
        ),
        "human_evaluation": {
            "score": 52.0,
            "verdict": "wrong",
            "feedback": "Has SRP right, but inverted Open-Closed (claimed open for modification, closed for extension!), and skipped L, I, and D.",
            "rubric_breakdown": {
                "correctness": 60.0,
                "completeness": 40.0,
                "misconceptions": ["Inverted Open-Closed principle definition"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "SE-01-WRG",
        "subject": "Software Engineering",
        "concept": "SOLID Design Principles",
        "concept_id": "se_solid_principles",
        "reference_explanation": (
            "SOLID is an acronym for five foundational object-oriented design principles: "
            "1. Single Responsibility (SRP): A class should have only one reason to change. "
            "2. Open-Closed (OCP): Software entities should be open for extension, but closed for modification. "
            "3. Liskov Substitution (LSP): Subtypes must be substitutable for their base types without altering correctness. "
            "4. Interface Segregation (ISP): Clients should not be forced to depend on interfaces they do not use. "
            "5. Dependency Inversion (DIP): High-level modules should depend on abstractions (interfaces) rather than concrete implementations."
        ),
        "key_points": [
            "SRP: Single reason to change per class",
            "OCP: Open for extension, closed for modification",
            "LSP: Derived classes must be substitutable for base classes",
            "ISP: Fine-grained, client-specific interfaces rather than fat interfaces",
            "DIP: Depend on abstractions rather than concrete classes"
        ],
        "student_answer": (
            "SOLID is a database query language for querying solid state drives (SSDs)."
        ),
        "human_evaluation": {
            "score": 5.0,
            "verdict": "wrong",
            "feedback": "Complete confusion with hardware SSDs.",
            "rubric_breakdown": {
                "correctness": 0.0,
                "completeness": 10.0,
                "misconceptions": ["Believes SOLID is a hardware SSD query language"]
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "SE-02-EXC",
        "subject": "Software Engineering",
        "concept": "Continuous Integration & Deployment (CI/CD)",
        "concept_id": "se_cicd_pipelines",
        "reference_explanation": (
            "Continuous Integration (CI) and Continuous Deployment (CD) are automated DevOps practices. "
            "CI automatically builds code and executes automated unit, integration, and linting test suites whenever changes "
            "are pushed to the repository, detecting defects early. Continuous Delivery/Deployment (CD) automatically packages "
            "successful builds into release artifacts and deploys them to staging and production environments without manual intervention, "
            "enabling rapid, low-risk release cycles."
        ),
        "key_points": [
            "CI: Automated building, linting, and testing on every code commit",
            "Early regression detection and trunk-based integration",
            "CD: Automated packaging and zero-touch deployment to environments",
            "Shortens feedback loop and reduces manual deployment errors"
        ],
        "student_answer": (
            "CI/CD automates the software delivery pipeline. Continuous Integration involves developers frequently merging code "
            "into a main branch, triggering automated build and testing pipelines (unit tests, integration tests, static analysis) "
            "to catch bugs immediately. Continuous Delivery and Continuous Deployment take passed builds and automate the deployment "
            "process into staging and production environments, eliminating manual release friction and enabling fast, reliable releases."
        ),
        "human_evaluation": {
            "score": 95.0,
            "verdict": "correct",
            "feedback": "Clear, professional synthesis of CI (automated tests on commit) and CD (automated release to staging/prod) benefits.",
            "rubric_breakdown": {
                "correctness": 96.0,
                "completeness": 94.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "SE-02-PAR",
        "subject": "Software Engineering",
        "concept": "Continuous Integration & Deployment (CI/CD)",
        "concept_id": "se_cicd_pipelines",
        "reference_explanation": (
            "Continuous Integration (CI) and Continuous Deployment (CD) are automated DevOps practices. "
            "CI automatically builds code and executes automated unit, integration, and linting test suites whenever changes "
            "are pushed to the repository, detecting defects early. Continuous Delivery/Deployment (CD) automatically packages "
            "successful builds into release artifacts and deploys them to staging and production environments without manual intervention, "
            "enabling rapid, low-risk release cycles."
        ),
        "key_points": [
            "CI: Automated building, linting, and testing on every code commit",
            "Early regression detection and trunk-based integration",
            "CD: Automated packaging and zero-touch deployment to environments",
            "Shortens feedback loop and reduces manual deployment errors"
        ],
        "student_answer": (
            "CI/CD is using GitHub Actions to run pytest automatically when you push code."
        ),
        "human_evaluation": {
            "score": 62.0,
            "verdict": "almost_correct",
            "feedback": "Accurate concrete tool example of CI, but very brief and leaves out Continuous Deployment, environment stages, and conceptual rationale.",
            "rubric_breakdown": {
                "correctness": 80.0,
                "completeness": 45.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    },
    {
        "id": "SE-02-WRG",
        "subject": "Software Engineering",
        "concept": "Continuous Integration & Deployment (CI/CD)",
        "concept_id": "se_cicd_pipelines",
        "reference_explanation": (
            "Continuous Integration (CI) and Continuous Deployment (CD) are automated DevOps practices. "
            "CI automatically builds code and executes automated unit, integration, and linting test suites whenever changes "
            "are pushed to the repository, detecting defects early. Continuous Delivery/Deployment (CD) automatically packages "
            "successful builds into release artifacts and deploys them to staging and production environments without manual intervention, "
            "enabling rapid, low-risk release cycles."
        ),
        "key_points": [
            "CI: Automated building, linting, and testing on every code commit",
            "Early regression detection and trunk-based integration",
            "CD: Automated packaging and zero-touch deployment to environments",
            "Shortens feedback loop and reduces manual deployment errors"
        ],
        "student_answer": (
            "CI/CD means constant programming without sleeping so software ships faster."
        ),
        "human_evaluation": {
            "score": 5.0,
            "verdict": "wrong",
            "feedback": "Humorous but completely erroneous answer.",
            "rubric_breakdown": {
                "correctness": 0.0,
                "completeness": 10.0,
                "misconceptions": []
            }
        },
        "semantic_score": None,
        "llm_score": None,
        "hybrid_score": None
    }
]


def get_academic_dataset() -> List[Dict[str, Any]]:
    """Return a copy of the academic benchmark dataset."""
    import copy
    return copy.deepcopy(ACADEMIC_BENCHMARK_DATASET)


def get_dataset_by_subject(subject_name: str) -> List[Dict[str, Any]]:
    """Filter benchmark dataset by subject name."""
    clean = subject_name.strip().lower()
    return [
        entry for entry in ACADEMIC_BENCHMARK_DATASET
        if entry["subject"].lower() == clean
    ]
