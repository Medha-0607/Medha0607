# REACTRA — Technical & Forensic Limitations

**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Document Principle:** Scientific honesty and technical credibility.

---

## Mandatory Operational Limitations

1. **Presumptive Nature:**
   Colorimetric chemical spot tests are qualitative presumptive indicators only. They cannot separate complex cutting agents, determine chemical purity, or substitute for laboratory confirmatory methods (e.g., GC-MS or HPLC).
2. **Controlled Synthetic Prototype Data:**
   Due to safety and regulatory constraints, all demonstration benchmarks utilize mathematically synthesized imagery with known CIE Lab ground truth. No illicit narcotics were handled during prototype development.
3. **Staged Multi-Reagent Assay Profiles:**
   Profiles for real chemical kits (`MARQUIS-001` and `SCOTT-001`) are staged with `null` centroids and require real-world physical spectrophotometric calibration prior to operational deployment.
4. **Camera Sensor & Lens Variability:**
   Different mobile devices feature varying sensor dynamic ranges, lens distortions, and automated ISP white-balance algorithms. While CIE Lab reference patch calibration compensates for linear illumination shifts, extreme chromatic aberrations require per-device profiling.
5. **No Direct eSakshya Backend Integration:**
   REACTRA exports standard, self-contained, portable digital evidence envelopes. It does not claim unauthorized live API connectivity to the National Informatics Centre (NIC) eSakshya system.
6. **Browser Geolocation Constraints:**
   High-accuracy GPS availability depends on browser permissions, device hardware, and operating system location services. When unavailable, coordinates are marked `UNAVAILABLE`.
7. **No Claim of Legal Admissibility:**
   Digital evidence records provide cryptographic proof of data integrity and non-repudiation (Section 65B Indian Evidence Act compliant primitives), but judicial admissibility remains subject to court discretion and statutory procedural rules.
