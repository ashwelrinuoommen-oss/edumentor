/**
 * Curated sample note sets for testing EduMentor note ingestion and prerequisite extraction.
 */

export const SAMPLE_NOTE_SETS = [
  {
    id: 'sample-cs-virtual-memory',
    title: 'Operating Systems: Virtual Memory & Paging',
    category: 'Computer Science',
    icon: 'Cpu',
    description: 'Core concepts in modern OS memory management from virtual address spaces to page replacement.',
    content: `# Operating Systems: Virtual Memory & Paging Architecture

## 1. Virtual Address Space
A virtual address space is an abstraction provided by the Operating System that gives each running process the illusion of having a continuous, private, dedicated block of memory. 
- Core components: User space, kernel space, program text, stack, and heap.
- Significance: Isolates processes from each other, protecting memory integrity and preventing rogue programs from overwriting OS kernel data structures.
- Keywords: virtual memory, address space, memory isolation, process protection, contiguous addressing.

## 2. Paging and Page Tables
Paging is the memory management scheme by which the computer stores and retrieves data from secondary storage for use in main physical memory.
- Concept: Physical memory is broken into fixed-sized blocks called "frames", while virtual memory is divided into blocks of the same size called "pages".
- Page Tables: A data structure used by the virtual memory system to store the mapping between virtual addresses and physical addresses.
- Prerequisites: Virtual Address Space.
- Keywords: page table, page frame, physical memory, address mapping, page size, frame allocation.

## 3. Translation Lookaside Buffer (TLB)
The Translation Lookaside Buffer (TLB) is a specialized hardware memory cache used by the Memory Management Unit (MMU) to accelerate virtual-to-physical address translation.
- Mechanism: Without a TLB, every memory access requires at least two physical accesses (one to read the page table, one to access actual data). The TLB provides single-cycle hit times.
- TLB Hit vs TLB Miss: On a hit, physical address is immediately available; on a miss, the MMU must perform a full page table walk.
- Prerequisites: Paging and Page Tables.
- Keywords: TLB, Memory Management Unit, MMU, page table walk, TLB hit, TLB miss, associative cache.

## 4. Page Faults and Demand Paging
A page fault is a hardware interrupt raised by the CPU Memory Management Unit when a program accesses a memory page that is mapped in the virtual address space, but not currently resident in physical RAM.
- Handler Flow: The OS traps the fault, checks validity, allocates an empty physical frame, reads the page from disk swap into RAM, updates the page table valid/invalid bit, and restarts the instruction.
- Demand Paging: Pages are loaded into physical memory only when requested by execution, rather than pre-loading the entire program.
- Prerequisites: Paging and Page Tables.
- Keywords: page fault, demand paging, valid bit, swap space, interrupt handler, backing store.

## 5. Thrashing and Working Set Model
Thrashing occurs when a computer's virtual memory subsystem is in a constant state of paging, rapidly exchanging data in memory for data on disk, leaving very little CPU time for executing actual instructions.
- Working Set Model: Peter Denning's model defining the set of pages a process is actively referencing during a given time window. If the sum of all working sets exceeds available RAM, thrashing occurs.
- Mitigation: Local page replacement, swapping entire inactive processes out, or increasing RAM.
- Prerequisites: Page Faults and Demand Paging, Translation Lookaside Buffer (TLB).
- Keywords: thrashing, working set, page replacement, disk I/O bottleneck, memory overcommit.`
  },
  {
    id: 'sample-neuro-synaptic-plasticity',
    title: 'Cognitive Neuroscience: Synaptic Plasticity & Memory',
    category: 'Neuroscience',
    icon: 'Brain',
    description: 'Mechanisms of cellular memory, synaptic strengthening, and memory consolidation.',
    content: `# Cognitive Neuroscience: Synaptic Plasticity & Memory Consolidation

## 1. Hebbian Learning Theory
Hebbian theory explains how neural circuits adapt during learning: "Neurons that fire together, wire together."
- Principle: When an axon of cell A repeatedly or persistently takes part in firing cell B, some growth process or metabolic change takes place in one or both cells such that A's efficiency in firing B is increased.
- Core significance: Provides the physiological foundation for associative learning and neural network remodeling.
- Keywords: Hebbian learning, synaptic efficacy, associative plasticity, neural circuits, synaptic wiring.

## 2. Long-Term Potentiation (LTP)
Long-Term Potentiation (LTP) is a persistent, long-lasting increase in synaptic strength following high-frequency chemical stimulation of a synapse.
- Induction Mechanism: Rapid bursts of electrical pulses (tetanic stimulation) strengthen neurotransmission across excitatory glutamatergic synapses.
- Phases: Early-LTP (independent of protein synthesis, lasting 1-3 hours) versus Late-LTP (requires gene transcription and protein synthesis, lasting days or weeks).
- Prerequisites: Hebbian Learning Theory.
- Keywords: LTP, synaptic potentiation, tetanic stimulation, glutamate, early LTP, late LTP, synaptic weight.

## 3. NMDA and AMPA Receptor Dynamics
The cellular coincidence detector for synaptic potentiation is the NMDA (N-methyl-D-aspartate) glutamate receptor.
- Voltage-Dependent Block: At resting membrane potential, the NMDA channel pore is physically blocked by an extracellular Magnesium ion (Mg2+).
- Unblocking: Glutamate binds to AMPA receptors, depolarizing the postsynaptic membrane. This positive intracellular charge expels the Mg2+ block, allowing Calcium ions (Ca2+) to flood in.
- Calcium Influx: Triggers intracellular kinase cascades (CaMKII) that insert additional AMPA receptors into the postsynaptic density.
- Prerequisites: Long-Term Potentiation (LTP).
- Keywords: NMDA receptor, AMPA receptor, magnesium block, calcium influx, CaMKII, postsynaptic density, depolarization.

## 4. Systems Memory Consolidation and the Hippocampus
Memory consolidation is the time-dependent neurobiological process where newly formed memories are stabilized and transferred from temporary storage to permanent neocortical storage.
- Two-Stage Memory Model: The hippocampus rapidly encodes episodic memories, while the neocortex slowly learns semantic representations over days, months, and sleep cycles.
- Sharp-Wave Ripples: During slow-wave sleep, hippocampal replays synchronize with neocortical spindles to consolidate memory traces.
- Prerequisites: Long-Term Potentiation (LTP), NMDA and AMPA Receptor Dynamics.
- Keywords: memory consolidation, hippocampus, neocortex, sharp-wave ripples, memory replay, slow-wave sleep.`
  },
  {
    id: 'sample-bio-cellular-respiration',
    title: 'Cellular Biology: Cellular Respiration & ATP Synthesis',
    category: 'Biology',
    icon: 'Activity',
    description: 'The metabolic pathways by which biological cells produce biochemical energy from glucose.',
    content: `# Cellular Biology: Cellular Respiration & ATP Production

## 1. Glycolysis
Glycolysis is the fundamental metabolic pathway in the cytoplasm that breaks down one 6-carbon glucose molecule into two 3-carbon pyruvate molecules.
- Energy Investment & Payoff: Consumes 2 ATP in initial phosphorylation steps, but produces 4 ATP (via substrate-level phosphorylation) and 2 NADH, yielding a net gain of 2 ATP and 2 NADH.
- Anaerobic Nature: Operates completely independently of molecular oxygen.
- Keywords: glycolysis, glucose, pyruvate, substrate-level phosphorylation, NADH, cytoplasm, anaerobic.

## 2. Pyruvate Oxidation and the Citric Acid (Krebs) Cycle
Pyruvate is transported across the mitochondrial double membrane into the mitochondrial matrix, where it is converted into Acetyl-CoA by pyruvate dehydrogenase.
- Krebs Cycle: Acetyl-CoA combines with oxaloacetate (4C) to form citrate (6C). Through an 8-step cyclical enzymatic cascade, carbons are released as CO2.
- High-Energy Yield per Glucose: Generates 6 NADH, 2 FADH2, and 2 GTP/ATP.
- Prerequisites: Glycolysis.
- Keywords: pyruvate oxidation, Acetyl-CoA, Krebs cycle, citric acid cycle, mitochondrial matrix, oxaloacetate, FADH2.

## 3. The Electron Transport Chain (ETC)
The Electron Transport Chain is a series of multiprotein complexes (Complex I, II, III, IV) embedded in the inner mitochondrial cristae membrane.
- Electron Transfer: High-energy electrons donated by NADH and FADH2 cascade down electronegativity gradients to terminal oxygen (forming H2O).
- Proton Pumping: Free energy released during electron movement drives active proton pumping (H+) from the matrix into the intermembrane space, creating an electrochemical gradient.
- Prerequisites: Pyruvate Oxidation and the Citric Acid (Krebs) Cycle.
- Keywords: electron transport chain, inner mitochondrial membrane, proton gradient, Complex I-IV, terminal electron acceptor, oxygen.

## 4. Chemiosmosis and ATP Synthase
Chemiosmosis is the movement of ions across a semipermeable membrane down their electrochemical proton-motive force to drive cellular work.
- ATP Synthase Rotary Motor: Protons stored in the intermembrane space flow back into the matrix through the F0 rotor subunit of ATP Synthase, rotating the catalytic F1 head to phosphorylate ADP into ATP.
- Total Yield: Generates approximately 30-32 ATP molecules per oxidized glucose molecule.
- Prerequisites: The Electron Transport Chain (ETC).
- Keywords: chemiosmosis, ATP synthase, proton motive force, oxidative phosphorylation, ADP phosphorylation, rotary motor.`
  }
];
