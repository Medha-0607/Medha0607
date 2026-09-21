# 06 — Cryptographic Verification & Local Audit Chain

## 1. Cryptographic Primitive Selection

RECTRA uses proven asymmetric and hashing primitives:

1. **Hashing:** SHA-256 (FIPS 180-4) for image integrity and canonical serialization preimage calculation.
2. **Digital Signatures:** Ed25519 (Edwards-curve Digital Signature Algorithm, RFC 8032):
   - Fast signature generation and verification on low-power mobile hardware.
   - High security resilience against side-channel attacks.
   - Fixed 64-byte (128-hex) signature representation.
3. **Audit Hash Chain:** Backward-linking hash chain:
   - Each evidence entry records `previous_record_hash` pointing to the digest of the prior entry.
   - Genesis record has `previous_record_hash = None`.

---

## 2. Standalone Evidence Envelope Verification Algorithm

Any party (court, defense counsel, forensic laboratory) can independently verify an exported `RECTRA_EVIDENCE_*.json` envelope:

```
[ INCOMING EVIDENCE ENVELOPE ]
               |
               v
1. Extract 'evidence_record' dictionary
               |
               v
2. Strip variable cryptographic fields:
   'record_digest', 'signature', 'public_key_fingerprint'
               |
               v
3. Serialize clean dictionary with 'json-sort-keys-compact-utf8-v1'
               |
               v
4. Compute SHA-256 digest of canonical bytes
               |
               +---> Compare with stored 'record_digest'
               |     If mismatch -> FAIL ("Digest mismatch: record content has been altered")
               v
5. Verify Ed25519 digital signature:
   Verify signature_bytes against stored record_digest using public_key.pem
               |
               +---> If invalid -> FAIL ("Digital signature verification failed")
               v
[ RECORD VERIFIED: Integrity & Authenticity Guaranteed ]
```

---

## 3. Local Audit Chain Verification Algorithm

The SQLite repository enforces backward-linking continuity across all saved tests:

```
[ Genesis: Record 0 ] <--- [ Record 1 ] <--- [ Record 2 ] <--- [ Record 3 ]
prev_hash = None           prev_hash = H(0)  prev_hash = H(1)  prev_hash = H(2)
```

The verification loop iterates in `rowid ASC` order:
1. For record 0 (Genesis), asserts `previous_record_hash is None`.
2. Verifies internal canonical digest matches stored `record_digest`.
3. Verifies Ed25519 signature of `record_digest`.
4. For record $i > 0$, asserts `previous_record_hash == record[i-1].record_digest`.
5. If an attacker deletes record 1, record 2 will point to `H(1)`, creating a detected hash gap: `CHAIN COMPROMISED: Audit chain broken at record 2`.
6. If an attacker tampers with record 1 in SQLite, recomputed digest $H'(1) \ne H(1)$, and signature verification fails: `CHAIN COMPROMISED: Integrity check failed at record 1`.
