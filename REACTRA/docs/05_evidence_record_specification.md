# 05 — Evidence Record & Canonical Serialization Specification

## 1. Overview & Canonical Requirements

To achieve tamper-evidence, a digital record must produce the exact same cryptographic hash across different machines, operating systems, and Python versions.

Standard JSON formatting is non-deterministic:
- Dictionary key insertion order may vary.
- Whitespace formatting (spaces after commas or colons) varies between serializers.
- Floating-point representations can differ across platforms.

RECTRA enforces **Canonical Serialization Format `json-sort-keys-compact-utf8-v1`**.

---

## 2. Canonical Serialization Algorithm

1. **Deterministic Sorting:** All dictionary keys at all nesting depths are sorted alphabetically (`sort_keys=True`).
2. **Compact Spacing:** Eliminates all extraneous whitespace: commas `,` and colons `:` with no intervening spaces (`separators=(",", ":")`).
3. **Encoding:** Pure UTF-8 bytes (`ensure_ascii=True`, `.encode("utf-8")`).
4. **Normalized Floats:** Floating-point numbers are rounded to 4 decimal places before serialization (`round(val, 4)`).

---

## 3. Authoritative Canonical Schema

The preimage dictionary includes the following fields:

```json
{
  "algorithm_version": "rectra-algo-v0.1",
  "capture_mode": "LIVE_CAMERA",
  "classification_score": 0.9821,
  "evidence_format_version": "1.0",
  "gps_status": "MANUAL_DEMO",
  "image_sha256": "4a12...89bc",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "measurement_quality": "VALID",
  "model_version": "rectra-model-v0.1",
  "operator_id": "DET-SHARMA-402",
  "previous_record_hash": "e3b0...b855",
  "profile_id": "DEMO-ASSAY-001",
  "profile_version": "1.0",
  "quality_gate_status": "VALID",
  "reference_card_version": "1.0",
  "result": "POSITIVE",
  "test_id": "c1f8a847-75e1-4569-8fd6-43b9e4a8dc81",
  "timestamp_utc": "2026-09-20T12:00:00Z"
}
```

---

## 4. Cryptographic Envelope Fields

Before persisting or exporting, the following variable cryptographic fields are computed and attached to form the complete evidence envelope:

- **`record_digest`:** SHA-256 hash of the canonical preimage bytes.
- **`signature`:** Hex-encoded Ed25519 digital signature of the `record_digest`.
- **`public_key_fingerprint`:** First 16 hexadecimal characters of `SHA-256(public_key_bytes)`.
- **`canonical_algorithm`:** String identifier `json-sort-keys-compact-utf8-v1`.

### Preimage Invariance Rule
When computing or verifying `record_digest`, the fields `record_digest`, `signature`, and `public_key_fingerprint` are excluded from the hash preimage. This prevents cyclic dependencies and ensures deterministic re-hashing.
