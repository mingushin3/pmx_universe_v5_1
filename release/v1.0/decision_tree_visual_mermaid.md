# Decision Tree Visual (Mermaid) — v1.0 (P134)

> Truncated to the **forced-tier** (N0→N1→N8→N2→N3→N4→N5) for readability.  Full
> internal tree has 126 nodes; this BFS-truncated view shows the first 35
> internal nodes + 5 synthetic forced-fail leaves reached within depth ≤6.
> See `config/operational_decision_tree.yaml` for the full structure.

```mermaid
flowchart TD
    tree_N0{N0?}
    tree_N1{N1?}
    tree_N1_v2{N1?}
    tree_N8{N8?}
    tree_N8_v2{N8?}
    tree_N8_v3{N8?}
    tree_N2{N2?}
    tree_N2_v2{N2?}
    tree_N2_v3{N2?}
    tree_N2_v4{N2?}
    tree_N2_v5{N2?}
    tree_N3{N3?}
    tree_N3_v2{N3?}
    tree_N3_v3{N3?}
    tree_N3_v4{N3?}
    tree_N3_v5{N3?}
    tree_N3_v6{N3?}
    tree_N3_v7{N3?}
    tree_N4{N4?}
    tree_N4_v2{N4?}
    tree_N4_v3{N4?}
    tree_N4_v4{N4?}
    tree_N4_v5{N4?}
    tree_N4_v6{N4?}
    tree_N4_v7{N4?}
    tree_N5{N5?}
    tree_N5_v2{N5?}
    tree_N5_v3{N5?}
    tree_N5_v4{N5?}
    tree_N5_v5{N5?}
    tree_N5_v6{N5?}
    tree_N5_v7{N5?}
    tree_N5_v8{N5?}
    tree_N5_v9{N5?}
    tree_N5_v10{N5?}
    leaf_QUARANTINE_Q02_forced_f["QUARANTINE\nQ02"]
    leaf_QUARANTINE_Q03_forced_f["QUARANTINE\nQ03"]
    leaf_QUARANTINE_Q08_forced_f["QUARANTINE\nQ08"]
    leaf_QUARANTINE_Q09_forced_f["QUARANTINE\nQ09"]
    leaf_QUARANTINE_Q15A_forced_f["QUARANTINE\nQ15A"]
    tree_N0 -->|Y| tree_N1
    tree_N0 -->|N| tree_N1_v2
    tree_N1 -->|Y| tree_N8
    tree_N1 -->|N| tree_N8_v2
    tree_N1_v2 -->|Y| tree_N8_v3
    tree_N1_v2 -->|N| leaf_QUARANTINE_Q03_forced_f
    tree_N8 -->|Y| tree_N2
    tree_N8 -->|N| tree_N2_v2
    tree_N8_v2 -->|Y| leaf_QUARANTINE_Q15A_forced_f
    tree_N8_v2 -->|N| tree_N2_v3
    tree_N8_v3 -->|Y| tree_N2_v4
    tree_N8_v3 -->|N| tree_N2_v5
    tree_N2 -->|Y| tree_N3
    tree_N2 -->|N| tree_N3_v2
    tree_N2_v2 -->|Y| tree_N3_v3
    tree_N2_v2 -->|N| tree_N3_v4
    tree_N2_v3 -->|Y| tree_N3_v5
    tree_N2_v3 -->|N| leaf_QUARANTINE_Q02_forced_f
    tree_N2_v4 -->|Y| tree_N3_v6
    tree_N2_v4 -->|N| leaf_QUARANTINE_Q02_forced_f
    tree_N2_v5 -->|Y| tree_N3_v7
    tree_N2_v5 -->|N| leaf_QUARANTINE_Q02_forced_f
    tree_N3 -->|Y| tree_N4
    tree_N3 -->|N| leaf_QUARANTINE_Q08_forced_f
    tree_N3_v2 -->|Y| tree_N4_v2
    tree_N3_v2 -->|N| leaf_QUARANTINE_Q08_forced_f
    tree_N3_v3 -->|Y| tree_N4_v3
    tree_N3_v3 -->|N| leaf_QUARANTINE_Q08_forced_f
    tree_N3_v4 -->|Y| tree_N4_v4
    tree_N3_v4 -->|N| leaf_QUARANTINE_Q08_forced_f
    tree_N3_v5 -->|Y| tree_N4_v5
    tree_N3_v5 -->|N| leaf_QUARANTINE_Q08_forced_f
    tree_N3_v6 -->|Y| tree_N4_v6
    tree_N3_v6 -->|N| leaf_QUARANTINE_Q08_forced_f
    tree_N3_v7 -->|Y| tree_N4_v7
    tree_N3_v7 -->|N| leaf_QUARANTINE_Q08_forced_f
    tree_N4 -->|Y| tree_N5
    tree_N4 -->|N| leaf_QUARANTINE_Q09_forced_f
    tree_N4_v2 -->|Y| tree_N5_v2
    tree_N4_v2 -->|N| leaf_QUARANTINE_Q09_forced_f
    tree_N4_v3 -->|Y| tree_N5_v3
    tree_N4_v3 -->|N| tree_N5_v4
    tree_N4_v4 -->|Y| tree_N5_v5
    tree_N4_v4 -->|N| leaf_QUARANTINE_Q09_forced_f
    tree_N4_v5 -->|Y| tree_N5_v6
    tree_N4_v5 -->|N| leaf_QUARANTINE_Q09_forced_f
    tree_N4_v6 -->|Y| tree_N5_v7
    tree_N4_v6 -->|N| tree_N5_v8
    tree_N4_v7 -->|Y| tree_N5_v9
    tree_N4_v7 -->|N| tree_N5_v10
    classDef auto fill:#cfc,stroke:#080
    classDef repair fill:#ccf,stroke:#008
    classDef quar fill:#ffc,stroke:#aa0
    classDef invalid fill:#fcc,stroke:#a00
    class leaf_QUARANTINE_Q08_forced_f quar
    class leaf_QUARANTINE_Q02_forced_f quar
    class leaf_QUARANTINE_Q03_forced_f quar
    class leaf_QUARANTINE_Q09_forced_f quar
    class leaf_QUARANTINE_Q15A_forced_f quar
```

## Color legend

- AUTO leaves: green
- REPAIR leaves: blue
- QUARANTINE leaves: yellow
- INVALID leaves: red

(Full leaves with AUTO/REPAIR/non-synthetic QUARANTINE/INVALID classes are
beyond depth 6 from root and not rendered in this truncated view.)

---
