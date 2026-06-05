#!/usr/bin/env node
// en-to-i18n.mjs - Replace hardcoded English UI chrome with $t() calls
// Opposite of zh-to-i18n: takes known English labels and wraps them in $t()
import fs from 'fs'
import path from 'path'

const ROOT = '/opt/data/memory-viewer/v2/frontend/src'

// Find files (skip deprecated)
function findFiles() {
  const files = []
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.name === 'deprecated' || entry.name === 'node_modules') continue
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) walk(full)
      else if (entry.name.endsWith('.vue')) files.push(full)
    }
  }
  walk(ROOT)
  return files
}

function extractTemplate(text) {
  const m = text.match(/<template[^>]*>([\s\S]*?)<\/template>/)
  return m ? m[1] : ''
}

function inProtectedZone(text, pos) {
  // Skip if inside {{ }} expression or HTML comment
  // {{...}} brackets
  const before = text.slice(0, pos)
  const opens = (before.match(/\{\{/g) || []).length
  const closes = (before.match(/\}\}/g) || []).length
  if (opens > closes) return true
  // <!-- ... -->
  const lastOpenComment = before.lastIndexOf('<!--')
  const lastCloseComment = before.lastIndexOf('-->')
  if (lastOpenComment > lastCloseComment) return true
  return false
}

// Hardcoded English UI chrome to wrap
// Map of literal text -> placeholder key (will be generated)
const EN_LABELS = [
  // MemoryCard
  ['Concepts', 'en_concepts'],
  ['Files', 'en_files'],
  ['Strength', 'en_strength'],
  ['Updated', 'en_updated'],
  ['Created', 'en_created'],
  // LinkCreator
  ['Source Memory', 'en_source_memory'],
  ['Target Memory *', 'en_target_memory'],
  ['Search for target memory...', 'en_search_target'],
  ['e.g. implements pattern X', 'en_link_label_hint'],
  ['Relation Type *', 'en_relation_type'],
  ['Select a relation type', 'en_select_relation'],
  ['Related', 'en_related'],
  ['Depends On', 'en_depends_on'],
  ['Contradicts', 'en_contradicts'],
  ['Extends', 'en_extends'],
  ['Derived From', 'en_derived_from'],
  ['Duplicates', 'en_duplicates'],
  ['References', 'en_references'],
  ['Label (optional)', 'en_label_optional'],
  // CollectionEditor
  ['Name *', 'en_name_required'],
  ['e.g. Important Patterns', 'en_collection_name_hint'],
  ['What is this collection about?', 'en_collection_desc_hint'],
  ['Icon', 'en_icon'],
  ['Color', 'en_color'],
  ['Query Filters', 'en_query_filters'],
  ['Memory Type', 'en_memory_type'],
  ['All Types', 'en_all_types'],
  ['Tags (comma separated)', 'en_tags_comma'],
  ['e.g. important, python', 'en_tags_hint'],
  ['Min Strength', 'en_min_strength'],
  ['Max Strength', 'en_max_strength'],
  ['Search Query', 'en_search_query'],
  ['Text to match in title/content', 'en_text_match_hint'],
  // CreateMemoryModal
  ['Title', 'en_title'],
  ['Content', 'en_content'],
  ['Type', 'en_type'],
  // Memory type badges (used in many places)
  ['Pattern', 'en_type_pattern'],
  ['Fact', 'en_type_fact'],
  ['Preference', 'en_type_preference'],
  ['Bug', 'en_type_bug'],
  ['Workflow', 'en_type_workflow'],
  ['Architecture', 'en_type_architecture'],
  // EditMemoryModal
  ['Strength:', 'en_strength_label'],
  // RagResponse
  ['🤖 AI Answer', 'en_ai_answer'],
  ['Confidence:', 'en_confidence'],
  ['📚 Sources', 'en_sources'],
  ['💡 Follow-up Questions', 'en_followups'],
  // MemberManager
  ['User ID', 'en_user_id'],
  ['Viewer', 'en_role_viewer'],
  ['Editor', 'en_role_editor'],
  ['Admin', 'en_role_admin'],
  ['Add', 'en_add'],
  ['No members yet', 'en_no_members'],
  // DigestCard
  ['🆕 New Memories', 'en_new_memories'],
  ['🔄 Top Changes', 'en_top_changes'],
  ['🌟 Emerging Themes', 'en_emerging_themes'],
  ['⚠️ Health Alerts', 'en_health_alerts'],
  // WhatsNewModal
  ['🎉 What\'s New', 'en_whats_new'],
  // KeyboardHelp
  ['Ctrl K', 'en_ctrl_k'],
  ['Esc', 'en_esc'],
  // FavoritesPanel
  ['Favorites', 'en_favorites'],
  ['Loading...', 'en_loading_dots'],
  ['No favorites yet', 'en_no_favorites'],
  // AppHeader / Sidebar
  ['Memory Viewer', 'en_app_title'],
  // StatsBar
  ['Profiles', 'en_profiles'],
  // Views
  ['All Sources', 'en_all_sources'],
  ['Categories', 'en_categories'],
  ['Months', 'en_months'],
  ['Left Profile', 'en_left_profile'],
  ['Right Profile', 'en_right_profile'],
  ['Webhook URL', 'en_webhook_url'],
  ['https://example.com/webhook', 'en_webhook_url_hint'],
  ['https://open.feishu.cn/open-apis/bot/v2/hook/...', 'en_feishu_url_hint'],
  ['Secret', 'en_secret'],
  ['Memory Viewer v2', 'en_app_v2'],
  ['Vue 3 + TypeScript + Vite', 'en_stack_info'],
  ['GitHub', 'en_github'],
  ['API Playground', 'en_api_playground'],
  ['Version', 'en_version'],
  ['All', 'en_all'],
  ['Hermes Memory', 'en_hermes_memory'],
  ['Global', 'en_global'],
  ['🌐 Global', 'en_global_with_icon'],
  // CollectionsView
  ['📚 Collections', 'en_collections'],
  ['+ New Collection', 'en_new_collection'],
  ['Loading collections...', 'en_loading_collections'],
  ['📁 No collections yet', 'en_no_collections'],
  ['Create your first collection', 'en_first_collection'],
  // Steps
  ['🤖 Hermes', 'en_hermes_preset'],
  ['📦 AgentMemory', 'en_agentmemory_preset'],
  // TemplateEditor
  ['Template name', 'en_template_name'],
  ['Description', 'en_description'],
  ['📝', 'en_template_icon'],
  ['e.g. Task: {task_name}', 'en_title_template_hint'],
  ['e.g. Task: {task_name}\\nOutcome: {outcome}', 'en_content_template_hint'],
  ['Default Type', 'en_default_type'],
  ['Default Tags (comma-separated)', 'en_default_tags'],
  ['tag1, tag2, tag3', 'en_tags_default_hint'],
  ['tag1, tag2', 'en_tag_pair_hint'],
  ['Fields', 'en_fields'],
  ['+ Add Field', 'en_add_field'],
  ['Req', 'en_req'],
  ['Save', 'en_save'],
  // Dialog
  ['Cancel', 'en_cancel'],
  ['Delete', 'en_delete'],
  ['Edit', 'en_edit'],
  // WhatsNew
  ['Built-in', 'en_builtin'],
  ['Use Template', 'en_use_template'],
  // Generic
  ['QR Code', 'en_qr_code'],
]

const files = findFiles()
let totalReplacements = 0
let totalFiles = 0

for (const file of files) {
  let text = fs.readFileSync(file, 'utf8')
  const originalTpl = extractTemplate(text)
  if (!originalTpl) continue
  let tpl = originalTpl
  let tplModified = false
  
  // Build a list of (placeholder, replacement) pairs
  // But we need to do it carefully — only replace text that's not already $t() wrapped
  // And only inside template, not script
  
  // Strategy: for each EN_LABEL, find it in the template (with quote/angle boundary)
  // and replace with {{ $t('key') }}
  for (const [english, key] of EN_LABELS) {
    // Multiple replacement patterns:
    // 1. >English< (visible text)
    // 2. "English" (attribute value, but we need to be careful)
    // 3. 'English'
    // 4. placeholder="English"
    
    // Pattern 1: >English<
    const tplRe = new RegExp(`>${escapeRegex(english)}<`, 'g')
    if (tplRe.test(tpl)) {
      // Reset regex
      const re = new RegExp(`>${escapeRegex(english)}<`, 'g')
      tpl = tpl.replace(re, `>{{ $t('${key}') }}<`)
      tplModified = true
    }
    
    // Pattern 2: title="English" (only if standalone)
    const titleRe = new RegExp(`title="${escapeRegex(english)}"`, 'g')
    if (titleRe.test(tpl)) {
      const re = new RegExp(`title="${escapeRegex(english)}"`, 'g')
      tpl = tpl.replace(re, `:title="$t('${key}')"`)
      tplModified = true
    }
    
    // Pattern 3: aria-label="English"
    const ariaRe = new RegExp(`aria-label="${escapeRegex(english)}"`, 'g')
    if (ariaRe.test(tpl)) {
      const re = new RegExp(`aria-label="${escapeRegex(english)}"`, 'g')
      tpl = tpl.replace(re, `:aria-label="$t('${key}')"`)
      tplModified = true
    }
    
    // Pattern 4: placeholder="English"
    const phRe = new RegExp(`placeholder="${escapeRegex(english)}"`, 'g')
    if (phRe.test(tpl)) {
      const re = new RegExp(`placeholder="${escapeRegex(english)}"`, 'g')
      tpl = tpl.replace(re, `:placeholder="$t('${key}')"`)
      tplModified = true
    }
  }
  
  if (tplModified) {
    text = text.replace(originalTpl, tpl)
    fs.writeFileSync(file, text, 'utf8')
    totalReplacements++
    totalFiles++
    console.log(`  ${path.relative(ROOT, file)}: patched`)
  }
}

console.log(`\nTotal: ${totalFiles} files, ${totalReplacements} patches`)

function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}