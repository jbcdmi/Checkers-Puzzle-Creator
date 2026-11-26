package DraughtsPlay.engine.ai

import DraughtsPlay.engine.core.Move

/** Bound type recorded for a stored search result relative to the alpha-beta window at the time. */
enum class BoundType { EXACT, LOWER_BOUND, UPPER_BOUND }

/** A single cached search result for a position. */
data class TTEntry(
    val key: Long,
    val depth: Int,
    val score: Int,
    val bound: BoundType,
    val bestMove: Move?
)

/**
 * Fixed-capacity transposition table keyed by Zobrist hash, with a simple
 * always-replace-if-deeper-or-equal policy. Backed by a [HashMap] for clarity; the
 * capacity cap prevents unbounded growth during long searches.
 */
class TranspositionTable(private val maxEntries: Int = 1_000_000) {

    private val table = HashMap<Long, TTEntry>(maxEntries)

    /** Looks up a cached entry for position [key], or null if absent. */
    fun get(key: Long): TTEntry? = table[key]

    /**
     * Stores a result for [key], replacing any existing entry unless the existing one was
     * searched to an equal or greater depth (deeper results are more valuable and should
     * not be evicted by shallower re-searches of the same position).
     */
    fun store(key: Long, depth: Int, score: Int, bound: BoundType, bestMove: Move?) {
        val existing = table[key]
        if (existing != null && existing.depth > depth) return
        if (table.size >= maxEntries && existing == null) {
            // Cheap eviction: drop an arbitrary entry rather than maintaining an LRU list.
            val victim = table.keys.firstOrNull()
            if (victim != null) table.remove(victim)
        }
        table[key] = TTEntry(key, depth, score, bound, bestMove)
    }

    /** Clears every cached entry, e.g. between games or when switching variants. */
    fun clear() = table.clear()

    /** Number of entries currently cached. */
    fun size(): Int = table.size
}
