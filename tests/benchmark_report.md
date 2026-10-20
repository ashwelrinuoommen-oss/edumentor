# Academic Benchmark Evaluation Report (Phase 39)
**Total Samples Evaluated**: 30 across 5 Academic CS Domains

## 1. Engine Correlation Against Human Judgment
| Evaluation Signal | Pearson Correlation ($r$) | Mean Absolute Error (MAE) | Verdict Agreement |
| :--- | :---: | :---: | :---: |
| **Hybrid Engine (Master)** | **0.831** | **15.2 pts** | **76.7%** |
| LLM-as-Judge Alone | 0.780 | 21.6 pts | — |
| Semantic Similarity Alone | 0.828 | 20.1 pts | — |

- **Spearman Rank Correlation (rho)**: 0.907
- **Root Mean Squared Error (RMSE)**: 22.36
- **Tolerance Match (±12 pts)**: 60.0%

## 2. Domain Breakdown
| Academic Subject | Samples | Pearson $r$ | Spearman $ho$ | MAE | Verdict Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Computer Networks | 6 | 0.863 | 0.943 | 14.7 | 83.3% |
| DBMS | 6 | 0.861 | 0.943 | 16.2 | 66.7% |
| Data Structures | 6 | 0.834 | 0.943 | 15.5 | 66.7% |
| Operating Systems | 6 | 0.998 | 1.000 | 4.4 | 100.0% |
| Software Engineering | 6 | 0.696 | 0.829 | 25.2 | 66.7% |

## 3. Sample Case Evaluations
| ID | Subject | Concept | Human Score | Semantic | LLM | Hybrid | Human Verdict | System Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `OS-01-EXC` | Operating Systems | Virtual Memory & Paging | 96 | 91.7 | 90.1 | **90.7** | `correct` | `correct` |
| `OS-01-PAR` | Operating Systems | Virtual Memory & Paging | 68 | 84.1 | 61.2 | **69.2** | `almost_correct` | `almost_correct` |
| `OS-01-MIS` | Operating Systems | Virtual Memory & Paging | 18 | 68.1 | 3.5 | **26.1** | `wrong` | `wrong` |
| `OS-02-EXC` | Operating Systems | Deadlocks & Coffman Cond | 97 | 100.0 | 96.0 | **97.4** | `correct` | `correct` |
| `OS-02-PAR` | Operating Systems | Deadlocks & Coffman Cond | 64 | 88.5 | 58.0 | **68.7** | `almost_correct` | `almost_correct` |
| `OS-02-WRG` | Operating Systems | Deadlocks & Coffman Cond | 8 | 42.5 | 0.0 | **14.9** | `wrong` | `wrong` |
| `CN-01-EXC` | Computer Networks | TCP 3-Way Handshake | 98 | 96.9 | 92.1 | **93.8** | `correct` | `correct` |
| `CN-01-PAR` | Computer Networks | TCP 3-Way Handshake | 70 | 61.4 | 56.9 | **58.5** | `almost_correct` | `almost_correct` |
| `CN-01-MIS` | Computer Networks | TCP 3-Way Handshake | 14 | 57.6 | 1.7 | **21.3** | `wrong` | `wrong` |
| `CN-02-EXC` | Computer Networks | DNS Hierarchical Resolut | 96 | 90.9 | 91.8 | **91.5** | `correct` | `correct` |
| `CN-02-PAR` | Computer Networks | DNS Hierarchical Resolut | 62 | 45.7 | 2.6 | **17.7** | `almost_correct` | `wrong` |
| `CN-02-WRG` | Computer Networks | DNS Hierarchical Resolut | 0 | 46.7 | 0.0 | **16.3** | `wrong` | `wrong` |
| `DBMS-01-EXC` | DBMS | ACID Properties of Trans | 97 | 98.9 | 90.9 | **93.7** | `correct` | `correct` |
| `DBMS-01-PAR` | DBMS | ACID Properties of Trans | 66 | 67.2 | 2.9 | **25.4** | `almost_correct` | `wrong` |
| `DBMS-01-MIS` | DBMS | ACID Properties of Trans | 5 | 32.0 | 0.0 | **11.2** | `wrong` | `wrong` |
| `DBMS-02-EXC` | DBMS | B+ Tree Indexing | 96 | 96.1 | 89.6 | **91.9** | `correct` | `correct` |
| `DBMS-02-PAR` | DBMS | B+ Tree Indexing | 58 | 87.0 | 0.0 | **30.4** | `almost_correct` | `wrong` |
| `DBMS-02-WRG` | DBMS | B+ Tree Indexing | 5 | 57.9 | 0.0 | **20.3** | `wrong` | `wrong` |
| `DS-01-EXC` | Data Structures | AVL Tree Balancing & Rot | 97 | 100.0 | 95.3 | **96.9** | `correct` | `correct` |
| `DS-01-PAR` | Data Structures | AVL Tree Balancing & Rot | 64 | 83.4 | 0.0 | **29.2** | `almost_correct` | `wrong` |
| `DS-01-WRG` | Data Structures | AVL Tree Balancing & Rot | 12 | 68.9 | 0.0 | **24.1** | `wrong` | `wrong` |
| `DS-02-EXC` | Data Structures | Hash Table Collision Res | 96 | 93.9 | 94.0 | **94.0** | `correct` | `correct` |
| `DS-02-PAR` | Data Structures | Hash Table Collision Res | 67 | 60.6 | 4.6 | **24.2** | `almost_correct` | `wrong` |
| `DS-02-WRG` | Data Structures | Hash Table Collision Res | 10 | 31.9 | 0.0 | **11.2** | `wrong` | `wrong` |
| `SE-01-EXC` | Software Engineering | SOLID Design Principles | 98 | 95.2 | 93.2 | **93.9** | `correct` | `correct` |
| `SE-01-PAR` | Software Engineering | SOLID Design Principles | 52 | 76.5 | 7.1 | **31.4** | `wrong` | `wrong` |
| `SE-01-WRG` | Software Engineering | SOLID Design Principles | 5 | 29.0 | 0.0 | **10.1** | `wrong` | `wrong` |
| `SE-02-EXC` | Software Engineering | Continuous Integration & | 95 | 100.0 | 0.0 | **35.0** | `correct` | `wrong` |
| `SE-02-PAR` | Software Engineering | Continuous Integration & | 62 | 43.3 | 0.0 | **15.2** | `almost_correct` | `wrong` |
| `SE-02-WRG` | Software Engineering | Continuous Integration & | 5 | 56.4 | 0.0 | **19.7** | `wrong` | `wrong` |