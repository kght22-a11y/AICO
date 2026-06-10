// cdlss.c - Cache Directory Logic System implementation for GGML
#include "cdlss.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Simple LRU cache implementation
cdlss_cache_t* cdlss_init(size_t capacity) {
    cdlss_cache_t* cache = (cdlss_cache_t*)malloc(sizeof(cdlss_cache_t));
    if (!cache) return NULL;
    
    cache->entries = (cdlss_entry_t*)calloc(capacity, sizeof(cdlss_entry_t));
    if (!cache->entries) {
        free(cache);
        return NULL;
    }
    
    cache->capacity = capacity;
    cache->count = 0;
    cache->hit_count = 0;
    cache->miss_count = 0;
    
    return cache;
}

void cdlss_free(cdlss_cache_t* cache) {
    if (!cache) return;
    
    // Free all cached data
    for (size_t i = 0; i < cache->count; i++) {
        if (cache->entries[i].data) {
            free(cache->entries[i].data);
        }
    }
    
    free(cache->entries);
    free(cache);
}

void* cdlss_get(cdlss_cache_t* cache, uint64_t key) {
    if (!cache) return NULL;
    
    // Linear search for the key
    for (size_t i = 0; i < cache->count; i++) {
        if (cache->entries[i].key == key) {
            cache->hit_count++;
            // Update timestamp (LRU behavior)
            cache->entries[i].timestamp = time(NULL);
            return cache->entries[i].data;
        }
    }
    
    cache->miss_count++;
    return NULL;
}

bool cdlss_put(cdlss_cache_t* cache, uint64_t key, void* data, size_t size) {
    if (!cache || !data || size == 0) return false;
    
    // Check if item already exists
    for (size_t i = 0; i < cache->count; i++) {
        if (cache->entries[i].key == key) {
            // Update existing entry
            free(cache->entries[i].data);
            cache->entries[i].data = malloc(size);
            if (!cache->entries[i].data) return false;
            memcpy(cache->entries[i].data, data, size);
            cache->entries[i].size = size;
            cache->entries[i].timestamp = time(NULL);
            return true;
        }
    }
    
    // Add new entry
    if (cache->count >= cache->capacity) {
        // Evict oldest entry (simple LRU)
        size_t oldest_idx = 0;
        uint64_t oldest_time = cache->entries[0].timestamp;
        
        for (size_t i = 1; i < cache->count; i++) {
            if (cache->entries[i].timestamp < oldest_time) {
                oldest_time = cache->entries[i].timestamp;
                oldest_idx = i;
            }
        }
        
        free(cache->entries[oldest_idx].data);
        cache->entries[oldest_idx].key = key;
        cache->entries[oldest_idx].data = malloc(size);
        if (!cache->entries[oldest_idx].data) return false;
        memcpy(cache->entries[oldest_idx].data, data, size);
        cache->entries[oldest_idx].size = size;
        cache->entries[oldest_idx].timestamp = time(NULL);
        cache->entries[oldest_idx].is_valid = true;
    } else {
        // Add to end
        cache->entries[cache->count].key = key;
        cache->entries[cache->count].data = malloc(size);
        if (!cache->entries[cache->count].data) return false;
        memcpy(cache->entries[cache->count].data, data, size);
        cache->entries[cache->count].size = size;
        cache->entries[cache->count].timestamp = time(NULL);
        cache->entries[cache->count].is_valid = true;
        cache->count++;
    }
    
    return true;
}

bool cdlss_remove(cdlss_cache_t* cache, uint64_t key) {
    if (!cache) return false;
    
    for (size_t i = 0; i < cache->count; i++) {
        if (cache->entries[i].key == key) {
            free(cache->entries[i].data);
            // Shift entries to fill gap

