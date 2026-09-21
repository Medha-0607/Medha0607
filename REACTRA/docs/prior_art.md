# REACTRA — Prior Art Positioning & Differentiation

**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Document Purpose:** Grounding REACTRA against commercial systems, academic literature, and digital evidence platforms.

---

## 1. Prior Art Overview

| System / Prior Art | Domain | Key Features | What REACTRA Is NOT Claiming | REACTRA Differentiation |
|---|---|---|---|---|
| **DetectaChem MobileDetect** | Commercial Mobile Presumptive App | Automated card scanning, barcode/QR alignment, cloud reporting | REACTRA does not claim to be the first smartphone app for presumptive drug tests. | Open, versioned JSON assay library, transparent pre-classification validity gates, zero cloud dependency, local Ed25519 hash chain. |
| **Academic Smartphone Colorimetry** | Computer Vision / Analytical Chemistry | RGB/Lab extraction, phone-to-phone calibration, polynomial colour transforms | REACTRA does not claim to invent CIE Lab colour correction or affine illumination calibration. | Integrated field workflow binding optical quality gates, CIE Lab calibration, and asymmetric cryptographic evidence into a single offline companion. |
| **Time-Resolved Kinetic Spot Testing (Kineticolor)** | Analytical Forensic Research | Video frame extraction, time-resolved colour trajectories $\Delta E(t)$, kinetic rate analysis | REACTRA does not claim to invent kinetic/temporal colour analysis for presumptive spot tests. | REACTRA designs an extensible architecture for future temporal reaction concordance integrated with local chain-of-custody evidence. |
| **eSakshya (NIC India)** | Criminal Justice Digital Evidence | Centralized digital evidence capture, preservation, and judicial exchange platform | REACTRA does not claim live authorized integration with eSakshya backends. | Portable standardized evidence envelope export ready for downstream ingestion by eSakshya and judicial LIMS repositories. |

---

## 2. Core Architectural Differentiation

REACTRA differentiates itself through an integrated design philosophy:
1. **Separation of Concerns:** Unlike existing systems that blend confidence into an arbitrary percentage (e.g. "95% match"), REACTRA separates:
   - Measurement Validity (Optical Quality Gate)
   - Classification Score (Distance Margin to Centroids)
   - Evidence Integrity (Cryptographic Attestation)
2. **Offline-First Cryptographic Chain of Custody:** Operates without cell service or cloud servers, providing mathematical proof against local record modification or deletion.
3. **Transparent Scientific Honesty:** Explicitly rejects fake GPS, fake device models, and unsupported laboratory confirmation claims.
