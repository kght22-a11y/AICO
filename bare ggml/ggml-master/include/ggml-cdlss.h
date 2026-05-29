#pragma once

#include "ggml.h"
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// CDLSS: Cognitive Deep Learning Super Sampling
// Refines low-precision quantized outputs via speculative trajectory ensemble

typedef struct ggml_cdlss_storm * ggml_cdlss_storm_t;

// CDLSS configuration parameters
struct ggml_cdlss_params {
    int32_t num_trajectories;          // Number of speculative trajectories to generate (10K-1M)
    float temperature;                 // Sampling temperature for storm generation [0.1-2.0]
    float dcx_threshold;               // DCX score threshold for pruning [0.0-1.0] (higher = more aggressive)
    float temporal_decay_lambda;       // Temporal decay factor λ in DCX: exp(-λ|t_i - t_j|) [0.01-0.5]
    bool cache_aware;                  // Reserve for future bare-metal optimization
};

// Per-trajectory metadata (for visualization and analysis)
struct ggml_cdlss_trajectory {
    float * logits;                    // Logits for this trajectory
    float dcx_score;                   // DCX score (lower = more coherent)
    int32_t cluster_id;                // Cluster ID for topography visualization (-1 if pruned)
};

// Storm result metadata
struct ggml_cdlss_result {
    float * refined_logits;            // Refined collapsed logits
    int32_t n_trajectories_generated;  // Total trajectories created
    int32_t n_trajectories_pruned;     // Trajectories removed by DCX threshold
    float avg_dcx_score;               // Average DCX score of surviving trajectories
    float collapse_time_ms;            // Collapse operation latency
};

// Create a new storm engine
// vocab_size: vocabulary size (e.g., 50256 for GPT-2)
// num_trajectories: initial trajectory count (can be modified per call)
GGML_API ggml_cdlss_storm_t ggml_cdlss_storm_new(int32_t vocab_size, int32_t num_trajectories);

// Free storm engine and all buffers
GGML_API void ggml_cdlss_storm_free(ggml_cdlss_storm_t storm);

// Generate hallucination storm from base logits
// base_logits: quantized model output logits [vocab_size]
// params: storm configuration
GGML_API void ggml_cdlss_storm_generate(ggml_cdlss_storm_t storm,
                                        const float * base_logits,
                                        struct ggml_cdlss_params params);

// Collapse wave function via DCX scoring and ensemble
// Produces refined_logits in storm->result
GGML_API void ggml_cdlss_storm_collapse(ggml_cdlss_storm_t storm);

// Retrieve refined logits (pointer to internal buffer, valid until next collapse)
GGML_API float * ggml_cdlss_storm_get_refined_logits(ggml_cdlss_storm_t storm);

// Retrieve trajectory metadata (for analysis/visualization)
// returns pointer to array of n_trajectories
GGML_API struct ggml_cdlss_trajectory * ggml_cdlss_storm_get_trajectories(ggml_cdlss_storm_t storm,
                                                                          int32_t * out_count);

// Retrieve result metadata (scores, timings, etc.)
GGML_API struct ggml_cdlss_result * ggml_cdlss_storm_get_result(ggml_cdlss_storm_t storm);

// Utility: Compute topographic embedding of trajectories
// Returns embedding dimension for each trajectory (for UMAP visualization)
GGML_API float * ggml_cdlss_compute_consensus_embedding(ggml_cdlss_storm_t storm,
                                                        int32_t * out_embedding_dim);

// Utility: Set trajectory cluster IDs based on embedding similarity
GGML_API void ggml_cdlss_assign_clusters(ggml_cdlss_storm_t storm, int32_t num_clusters);

#ifdef __cplusplus
}
#endif
