export interface AgentMemory {
  id: string
  type: 'pattern' | 'fact' | 'preference' | 'bug' | 'workflow' | 'architecture'
  title: string
  content: string
  concepts: string[]
  files: string[]
  createdAt: string
  updatedAt: string
  strength: number
  version: number
  isLatest: boolean
  sessionIds: string[]
  archived?: boolean
  tags?: string[]
  health_score?: number
  health_color?: 'green' | 'yellow' | 'red'
}

// F46: Tags
export interface TagInfo {
  tag: string
  count: number
}

export interface TagsResponse {
  tags: TagInfo[]
}

export interface AgentMemoryResponse {
  memories: AgentMemory[]
}

export interface AgentMemoryPaginatedResponse {
  total: number
  limit: number
  offset: number
  memories: AgentMemory[]
}

export interface ImportResult {
  success: boolean
  imported: number
  skipped: number
  failed: number
  errors: string[]
}

// P3: Decay (F-22)
export interface DecayPoint {
  day: number
  strength: number
}

export interface DecayResponse {
  memory_id: string
  current_strength: number
  initial_strength: number
  decay_rate: number
  days_since_created: number
  predicted_zero_date: string | null
  decay_curve: DecayPoint[]
}

// P3: Health (F-20)
export interface HealthBreakdown {
  strength_score: number
  age_score: number
  concepts_score: number
  recommendation_score: number
}

export interface HealthResponse {
  memory_id: string
  health_score: number
  color: 'green' | 'yellow' | 'red'
  breakdown: HealthBreakdown
  days_since_created: number
  days_until_strength_zero: number | null
}

// P3: Recommendations (F-19)
export interface RecommendationItem {
  memory: AgentMemory
  score: number
  shared_concepts: string[]
}

export interface RecommendationsResponse {
  memory_id: string
  recommendations: RecommendationItem[]
}

// P3: Dedup (F-21)
export interface DuplicatePair {
  memory_a: AgentMemory
  memory_b: AgentMemory
  similarity: number
  concepts_similarity: number
  title_similarity: number
  shared_concepts: string[]
}

export interface DuplicatesResponse {
  pairs: DuplicatePair[]
  total_pairs: number
}

export interface MergeResponse {
  success: boolean
  merged_memory: AgentMemory
}

// P3: Graph (F-18)
export interface GraphNode {
  id: string
  label: string
  type: string
  strength: number
  size: number
}

export interface GraphEdge {
  source: string
  target: string
  weight: number
  shared_concepts: string[]
}

export interface GraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
  meta: {
    node_count: number
    edge_count: number
    max_weight: number
  }
}

// F47: Command Palette - Quick Search
export interface QuickSearchResult {
  id: string
  title: string
  type: string
  snippet: string
  tags?: string[]
}

export interface QuickSearchResponse {
  results: QuickSearchResult[]
  total: number
}

// F48: Smart Collections
export interface SmartCollection {
  id: string
  name: string
  description: string
  count: number
  icon: string
}

export interface CollectionsResponse {
  collections: SmartCollection[]
}

// F49: Memory Templates
export interface MemoryTemplate {
  id: string
  name: string
  icon: string
  type: string
  title_template: string
  content_template: string
  suggested_concepts: string[]
}

export interface TemplatesResponse {
  templates: MemoryTemplate[]
}

// P8: Semantic Search (F-33)
export interface SemanticSearchResult {
  id: string
  title: string
  type: string
  snippet: string
  tags: string[]
  similarity: number
  match_type: 'semantic' | 'keyword'
}

export interface SemanticSearchResponse {
  query: string
  mode: 'semantic' | 'keyword' | 'keyword_fallback'
  results: SemanticSearchResult[]
}

// P8: Auto-Tagging (F-34)
export interface SuggestTagsResponse {
  memory_id: string
  title: string
  suggested_tags: string[]
}

export interface SummarizeResponse {
  memory_id: string
  title: string
  summary: string
}

export interface BulkAutoTagResponse {
  success: boolean
  processed: number
  results: Array<{ id: string; title: string; suggested_tags: string[] }>
}

// P8: Heatmap (F-37)
export type HeatmapData = Record<string, number>

export interface HeatmapSummaryResponse {
  data: HeatmapData
  metric: 'created' | 'accessed' | 'modified'
  days: number
  total_events: number
  max_day_count: number
  active_days: number
  total_days: number
}

// P8: Plugins (F-38)
export interface PluginInfo {
  name: string
  version: string
  description: string
  hooks: string[]
  enabled: boolean
  loaded_at: string
  path: string
}

export interface PluginListResponse {
  plugins: PluginInfo[]
  total: number
}

export interface PluginLogEntry {
  plugin: string
  hook: string
  success: boolean
  duration_ms: number
  error: string
  timestamp: string
}
