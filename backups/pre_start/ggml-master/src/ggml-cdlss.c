#include "ggml-cdlss.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

// Internal storm state (opaque to user)
struct ggml_cdlss_storm {
    int32_t vocab_size;
    int32_t max_trajectories;
    struct ggml_cdlss_trajectory * trajectories;

    float * base_logits;               // Original quantized output
    float * refined_logits;            // Collapsed result
    float * consensus_embedding;       // Cached embedding for visualization

    struct ggml_cdlss_result result;

    // Scratch buffers for computation
    float * softmax_buf;               // For softmax computation
    float * dcx_scores;                // DCX scores for each trajectory
    float * trajectory_embeddings;     // 2D embeddings for clustering
};

// ============================================================================
// Utility: Math functions
// ============================================================================

static float softmax_scaled(const float * logits, int32_t idx, float temperature, int32_t vocab_size) {
    float max_logit = logits[0];
    for (int32_t i = 1; i < vocab_size; i++) {
        if (logits[i] > max_logit) max_logit = logits[i];
    }

    float exp_sum = 0.0f;
    for (int32_t i = 0; i < vocab_size; i++) {
        exp_sum += expf((logits[i] - max_logit) / temperature);
    }

    return expf((logits[idx] - max_logit) / temperature) / (exp_sum + 1e-10f);
}

static float cosine_similarity(const float * a, const float * b, int32_t dim) {
    float dot = 0.0f, norm_a = 0.0f, norm_b = 0.0f;
    for (int32_t i = 0; i < dim; i++) {
        dot += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    float denom = sqrtf(norm_a) * sqrtf(norm_b);
    return denom > 1e-10f ? dot / denom : 0.0f;
}

static float frand() {
    return (float)rand() / (float)RAND_MAX;
}

// ============================================================================
// Trajectory generation
// ============================================================================

// Sample one trajectory from base logits using temperature-scaled sampling
static void generate_trajectory(struct ggml_cdlss_storm * storm,
                               float * trajectory_logits,
                               float temperature) {
    const float * base = storm->base_logits;
    int32_t vocab = storm->vocab_size;

    // Copy base logits as starting point
    memcpy(trajectory_logits, base, vocab * sizeof(float));

    // Add noise sampled from temperature-scaled distribution
    for (int32_t i = 0; i < vocab; i++) {
        float prob = softmax_scaled(base, i, temperature, vocab);
        // Perturbation: sample from logistic distribution scaled by temperature
        float noise = logf(frand() + 1e-10f) - logf(1.0f - frand() + 1e-10f);
        trajectory_logits[i] += temperature * noise * 0.1f;  // Scale noise appropriately
    }
}

// ============================================================================
// DCX (Divergence-Correlation) scoring
// ============================================================================

// Compute embedding from logits (use softmax as embedding)
static void logits_to_embedding(const float * logits, float * embedding, int32_t vocab_size, float temperature) {
    float max_logit = logits[0];
    for (int32_t i = 1; i < vocab_size; i++) {
        if (logits[i] > max_logit) max_logit = logits[i];
    }

    float exp_sum = 0.0f;
    for (int32_t i = 0; i < vocab_size; i++) {
        embedding[i] = expf((logits[i] - max_logit) / temperature);
        exp_sum += embedding[i];
    }

    for (int32_t i = 0; i < vocab_size; i++) {
        embedding[i] /= (exp_sum + 1e-10f);
    }
}

// Compute DCX score between trajectory and consensus
// High DCX = divergent (likely hallucination), Low DCX = coherent
static float compute_dcx_score(const float * traj_embedding,
                              const float * consensus_embedding,
                              int32_t vocab_size,
                              float temporal_decay_lambda,
                              int32_t traj_index,
                              int32_t total_trajectories) {
    // Cosine similarity
    float similarity = cosine_similarity(traj_embedding, consensus_embedding, vocab_size);

    // Temporal decay: trajectories generated later have less weight
    float time_decay = expf(-temporal_decay_lambda * fabsf((float)traj_index - total_trajectories / 2.0f) / (float)total_trajectories);

    // DCX = (1 - similarity) * time_decay
    // Low values = high correlation (coherent), High values = divergent (hallucination)
    return (1.0f - fabsf(similarity)) * time_decay;
}

// ============================================================================
// Wave collapse (ensemble)
// ============================================================================

// Compute mean embedding (consensus)
static void compute_consensus(struct ggml_cdlss_storm * storm,
                             float * consensus,
                             float temperature) {
    int32_t vocab = storm->vocab_size;
    memset(consensus, 0, vocab * sizeof(float));

    // Average softmax of all trajectories
    for (int32_t t = 0; t < storm->max_trajectories; t++) {
        float * traj = storm->trajectories[t].logits;
        float max_logit = traj[0];
        for (int32_t i = 1; i < vocab; i++) {
            if (traj[i] > max_logit) max_logit = traj[i];
        }

        for (int32_t i = 0; i < vocab; i++) {
            consensus[i] += expf((traj[i] - max_logit) / temperature);
        }
    }

    // Normalize
    for (int32_t i = 0; i < vocab; i++) {
        consensus[i] /= (storm->max_trajectories + 1e-10f);
    }
}

// Ensemble high-coherence trajectories into refined logits
static void ensemble_trajectories(struct ggml_cdlss_storm * storm,
                                 float dcx_threshold) {
    int32_t vocab = storm->vocab_size;
    memset(storm->refined_logits, 0, vocab * sizeof(float));

    float weight_sum = 0.0f;
    int32_t kept_count = 0;

    for (int32_t t = 0; t < storm->max_trajectories; t++) {
        if (storm->trajectories[t].dcx_score < dcx_threshold) {
            // This trajectory is coherent enough to keep
            float weight = 1.0f - storm->trajectories[t].dcx_score;

            for (int32_t i = 0; i < vocab; i++) {
                storm->refined_logits[i] += weight * storm->trajectories[t].logits[i];
            }
            weight_sum += weight;
            kept_count++;
        } else {
            // Mark as pruned
            storm->trajectories[t].cluster_id = -1;
        }
    }

    // Normalize
    if (weight_sum > 1e-10f) {
        for (int32_t i = 0; i < vocab; i++) {
            storm->refined_logits[i] /= weight_sum;
        }
    }

    // Update result metadata
    storm->result.n_trajectories_pruned = storm->max_trajectories - kept_count;

    // Compute average DCX of kept trajectories
    float dcx_sum = 0.0f;
    for (int32_t t = 0; t < storm->max_trajectories; t++) {
        if (storm->trajectories[t].dcx_score < dcx_threshold) {
            dcx_sum += storm->trajectories[t].dcx_score;
        }
    }
    storm->result.avg_dcx_score = kept_count > 0 ? dcx_sum / kept_count : 0.0f;
}

// ============================================================================
// Public API Implementation
// ============================================================================

GGML_API ggml_cdlss_storm_t ggml_cdlss_storm_new(int32_t vocab_size, int32_t num_trajectories) {
    struct ggml_cdlss_storm * storm = malloc(sizeof(struct ggml_cdlss_storm));

    storm->vocab_size = vocab_size;
    storm->max_trajectories = num_trajectories;

    // Allocate trajectory array
    storm->trajectories = calloc(num_trajectories, sizeof(struct ggml_cdlss_trajectory));

    // Allocate logits for each trajectory
    for (int32_t i = 0; i < num_trajectories; i++) {
        storm->trajectories[i].logits = malloc(vocab_size * sizeof(float));
        storm->trajectories[i].cluster_id = 0;
        storm->trajectories[i].dcx_score = 0.0f;
    }

    // Allocate buffers
    storm->base_logits = malloc(vocab_size * sizeof(float));
    storm->refined_logits = malloc(vocab_size * sizeof(float));
    storm->softmax_buf = malloc(vocab_size * sizeof(float));
    storm->dcx_scores = malloc(num_trajectories * sizeof(float));
    storm->trajectory_embeddings = malloc(num_trajectories * vocab_size * sizeof(float));
    storm->consensus_embedding = malloc(vocab_size * sizeof(float));

    // Initialize result
    memset(&storm->result, 0, sizeof(struct ggml_cdlss_result));
    storm->result.n_trajectories_generated = num_trajectories;

    return storm;
}

GGML_API void ggml_cdlss_storm_free(ggml_cdlss_storm_t storm_ptr) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;

    for (int32_t i = 0; i < storm->max_trajectories; i++) {
        free(storm->trajectories[i].logits);
    }
    free(storm->trajectories);
    free(storm->base_logits);
    free(storm->refined_logits);
    free(storm->softmax_buf);
    free(storm->dcx_scores);
    free(storm->trajectory_embeddings);
    free(storm->consensus_embedding);
    free(storm);
}

GGML_API void ggml_cdlss_storm_generate(ggml_cdlss_storm_t storm_ptr,
                                        const float * base_logits,
                                        struct ggml_cdlss_params params) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;

    // Store base logits
    memcpy(storm->base_logits, base_logits, storm->vocab_size * sizeof(float));

    // Update trajectory count if needed
    if (params.num_trajectories != storm->max_trajectories) {
        // For now, just cap at current max
        params.num_trajectories = (params.num_trajectories < storm->max_trajectories)
            ? params.num_trajectories : storm->max_trajectories;
    }

    // Generate hallucination storm
    srand(time(NULL));  // Seed RNG
    for (int32_t t = 0; t < params.num_trajectories; t++) {
        generate_trajectory(storm, storm->trajectories[t].logits, params.temperature);
    }

    // Compute embeddings for all trajectories
    for (int32_t t = 0; t < params.num_trajectories; t++) {
        logits_to_embedding(storm->trajectories[t].logits,
                           storm->trajectory_embeddings + t * storm->vocab_size,
                           storm->vocab_size,
                           params.temperature);
    }

    // Compute consensus embedding
    compute_consensus(storm, storm->consensus_embedding, params.temperature);

    // Score each trajectory with DCX
    for (int32_t t = 0; t < params.num_trajectories; t++) {
        float * traj_emb = storm->trajectory_embeddings + t * storm->vocab_size;
        storm->trajectories[t].dcx_score = compute_dcx_score(
            traj_emb,
            storm->consensus_embedding,
            storm->vocab_size,
            params.temporal_decay_lambda,
            t,
            params.num_trajectories
        );
    }
}

GGML_API void ggml_cdlss_storm_collapse(ggml_cdlss_storm_t storm_ptr) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;

    // Ensemble trajectories with default threshold
    float dcx_threshold = 0.7f;  // Keep trajectories with DCX < 0.7
    ensemble_trajectories(storm, dcx_threshold);
}

GGML_API float * ggml_cdlss_storm_get_refined_logits(ggml_cdlss_storm_t storm_ptr) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;
    return storm->refined_logits;
}

GGML_API struct ggml_cdlss_trajectory * ggml_cdlss_storm_get_trajectories(ggml_cdlss_storm_t storm_ptr,
                                                                          int32_t * out_count) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;
    if (out_count) *out_count = storm->max_trajectories;
    return storm->trajectories;
}

GGML_API struct ggml_cdlss_result * ggml_cdlss_storm_get_result(ggml_cdlss_storm_t storm_ptr) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;
    return &storm->result;
}

GGML_API float * ggml_cdlss_compute_consensus_embedding(ggml_cdlss_storm_t storm_ptr,
                                                        int32_t * out_embedding_dim) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;
    if (out_embedding_dim) *out_embedding_dim = storm->vocab_size;
    return storm->consensus_embedding;
}

GGML_API void ggml_cdlss_assign_clusters(ggml_cdlss_storm_t storm_ptr, int32_t num_clusters) {
    struct ggml_cdlss_storm * storm = (struct ggml_cdlss_storm *)storm_ptr;

    // Simple k-means-like clustering based on DCX scores
    // Group trajectories into num_clusters based on DCX score ranges
    float min_dcx = 1e10f, max_dcx = -1e10f;
    for (int32_t t = 0; t < storm->max_trajectories; t++) {
        float dcx = storm->trajectories[t].dcx_score;
        if (dcx < min_dcx) min_dcx = dcx;
        if (dcx > max_dcx) max_dcx = dcx;
    }

    float dcx_range = max_dcx - min_dcx + 1e-10f;
    for (int32_t t = 0; t < storm->max_trajectories; t++) {
        float normalized_dcx = (storm->trajectories[t].dcx_score - min_dcx) / dcx_range;
        storm->trajectories[t].cluster_id = (int32_t)(normalized_dcx * (num_clusters - 1));
    }
}
