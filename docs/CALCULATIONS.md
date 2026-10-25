# Mathematics and evidence contract

## Unified capacity

NVIDIA reports DGX Spark 128 GB unified system memory. The reference implementation uses `128 × 10^9 / 2^30` ≈ **119.21 GiB** of physical unified memory (decimal GB differs from binary GiB). The hardware bandwidth reference is 273 GB/s; it is recorded for context but never used to guess tokens/sec.

## Weight storage

`weights_gib = parameters_b × 10^9 × weight_bits / 8 × packing_multiplier / 2^30`

Assumes effective quantized bits per parameter, adjustable packing/layout overhead, and whole-model residency. Real checkpoints may include unquantized layers, embeddings, optimizer state, metadata and runtime-specific allocations.

## KV-cache estimate

`kv_bytes_per_token = 2 × transformer_layers × key_value_heads × attention_head_dim × kv_element_bytes`

`kv_gib = kv_bytes_per_token × context_tokens × concurrent_sequences × effective_KV_utilization / 2^30`

This is dense, per-sequence KV accounting, **not** paged-attention allocator behavior. Prefix reuse and GQA/MQA must be described by correct KV head count. A 4-bit KV format can have group scaling/metadata overhead beyond the nominal half byte.

## Headroom and heuristics

`estimated_total = weights + KV + OS_reserve + runtime_reserve + activation_reserve + (physical_GiB × safety_fraction)`

`headroom = physical_GiB − estimated_total`

The label `fits-estimate` means a first-order calculation passes, not that software/kernel/runtime support, fragmentation and service reliability are proven. `tight` means small remaining margin; `exceeds` means modeled requirements over capacity. The displayed memory-only bound on simultaneous sequences is not a throughput/concurrency SLA.

## Benchmark calibration

The app requires at least two claimed **measured** observations matching the selected device profile and exact weight precision, with model size ≤1.35× ratio, context ≤2× ratio and concurrency ≤2× ratio. It uses nearby weighted observations and shows the observed range, source labels and low/medium qualitative confidence. Model revisions and serving kernels are not fully identified in the current MVP—**do not treat this as scientifically validated performance prediction**.

Real future calibration must identify checkpoint hashes, backend version, prompt/output token distributions, batch scheduler, model revision and thermal state, then compare held-out predictions against measured ground truth.

## Sources

- [NVIDIA DGX Spark Hardware Overview](https://docs.nvidia.com/dgx/dgx-spark/hardware.html)
- Model geometry and quantization must be sourced from the specific deployed checkpoint/configuration.
