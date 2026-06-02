"""Natural Language Query service (F-39) — LLM-powered NL to structured query.

Converts natural language questions into structured API query conditions.
Uses a simple pattern-matching approach with optional LLM enhancement.
"""

import re
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)


# --- NLQ Pattern-based parsing (offline fallback) ---

_TYPE_KEYWORDS = {
    "bug": ["bug", "错误", "缺陷", "问题", "issue"],
    "fact": ["fact", "事实", "信息"],
    "pattern": ["pattern", "模式", "规律"],
    "preference": ["preference", "偏好", "喜欢", "习惯"],
    "workflow": ["workflow", "流程", "工作流", "步骤"],
    "architecture": ["architecture", "架构", "设计"],
}

_TIME_KEYWORDS = {
    "today": ["今天", "today"],
    "yesterday": ["昨天", "yesterday"],
    "this_week": ["本周", "这周", "this week"],
    "last_week": ["上周", "last week"],
    "this_month": ["本月", "this month"],
    "last_month": ["上月", "last month"],
    "recent": ["最近", "recent", "近期"],
}

_STRENGTH_KEYWORDS = {
    "high": ["strong", "strongest", "重要", "关键", "high strength", "高"],
    "low": ["weak", "weakest", "低", "low strength", "衰减"],
    "medium": ["medium", "中等"],
}

_SORT_KEYWORDS = {
    "newest": ["最新", "最近创建", "newest", "latest"],
    "oldest": ["最旧", "最早", "oldest"],
    "strongest": ["最强", "highest strength", "strongest"],
    "weakest": ["最弱", "lowest strength", "weakest"],
}


def _parse_type(question: str) -> Optional[list[str]]:
    """Extract memory type from question."""
    q_lower = question.lower()
    found_types = []
    for type_name, keywords in _TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in q_lower:
                found_types.append(type_name)
                break
    return found_types if found_types else None


def _parse_time_range(question: str) -> Optional[dict]:
    """Extract date range from question."""
    q_lower = question.lower()
    now = datetime.now(timezone.utc)

    for period, keywords in _TIME_KEYWORDS.items():
        for kw in keywords:
            if kw in q_lower:
                if period == "today":
                    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    return {"date_from": start.strftime("%Y-%m-%d"), "date_to": now.strftime("%Y-%m-%d")}
                elif period == "yesterday":
                    start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    return {"date_from": start.strftime("%Y-%m-%d"), "date_to": end.strftime("%Y-%m-%d")}
                elif period == "this_week":
                    start = now - timedelta(days=now.weekday())
                    return {"date_from": start.strftime("%Y-%m-%d"), "date_to": now.strftime("%Y-%m-%d")}
                elif period == "last_week":
                    end = now - timedelta(days=now.weekday())
                    start = end - timedelta(days=7)
                    return {"date_from": start.strftime("%Y-%m-%d"), "date_to": end.strftime("%Y-%m-%d")}
                elif period == "this_month":
                    start = now.replace(day=1)
                    return {"date_from": start.strftime("%Y-%m-%d"), "date_to": now.strftime("%Y-%m-%d")}
                elif period == "last_month":
                    first_this = now.replace(day=1)
                    end = first_this - timedelta(days=1)
                    start = end.replace(day=1)
                    return {"date_from": start.strftime("%Y-%m-%d"), "date_to": end.strftime("%Y-%m-%d")}
                elif period == "recent":
                    start = now - timedelta(days=14)
                    return {"date_from": start.strftime("%Y-%m-%d"), "date_to": now.strftime("%Y-%m-%d")}
    return None


def _parse_strength(question: str) -> Optional[dict]:
    """Extract strength range from question."""
    q_lower = question.lower()

    # Check for explicit number: "strength > 7" or "strength >= 5"
    num_match = re.search(r"strength\s*([><=!]+)\s*(\d+)", q_lower)
    if num_match:
        op, val = num_match.group(1), int(num_match.group(2))
        if ">" in op:
            return {"strength_min": val + 1 if "=" not in op else val}
        elif "<" in op:
            return {"strength_max": val - 1 if "=" not in op else val}
        elif "=" in op:
            return {"strength_min": val, "strength_max": val}

    # Check for keywords
    for level, keywords in _STRENGTH_KEYWORDS.items():
        for kw in keywords:
            if kw in q_lower:
                if level == "high":
                    return {"strength_min": 7}
                elif level == "low":
                    return {"strength_max": 3}
                elif level == "medium":
                    return {"strength_min": 4, "strength_max": 6}
    return None


def _parse_sort(question: str) -> Optional[str]:
    """Extract sort preference from question."""
    q_lower = question.lower()
    for sort_key, keywords in _SORT_KEYWORDS.items():
        for kw in keywords:
            if kw in q_lower:
                return sort_key
    return None


def _extract_search_terms(question: str) -> Optional[str]:
    """Extract key search terms from question (strip question words)."""
    # Remove common question patterns
    cleaned = question
    remove_patterns = [
        r"(show|find|list|get|search|显示|查找|找到|列出|搜索)\s*(me|us|all)?\s*",
        r"(what|which|how|where|when|who)\s+(are|is|was|were|do|does|did)\s+(the|my|all)?\s*",
        r"(请|帮我|给我)\s*",
        r"(的|了|吗|呢|啊)\s*$",
    ]
    for pattern in remove_patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip()
    # If too short after cleaning, use original
    if len(cleaned) < 2:
        return None
    return cleaned


def parse_natural_query(question: str) -> dict:
    """Parse a natural language question into structured query conditions.
    
    Uses offline pattern matching. Returns query conditions and explanation.
    """
    start_time = time.time()

    types = _parse_type(question)
    time_range = _parse_time_range(question)
    strength = _parse_strength(question)
    sort = _parse_sort(question)
    search_terms = _extract_search_terms(question)

    conditions: dict = {}
    explanation_parts: list[str] = []

    if types:
        conditions["type"] = types
        explanation_parts.append(f"类型: {', '.join(types)}")

    if time_range:
        conditions.update(time_range)
        explanation_parts.append(f"时间: {time_range.get('date_from', '')} ~ {time_range.get('date_to', '')}")

    if strength:
        conditions.update(strength)
        if "strength_min" in strength and "strength_max" in strength:
            explanation_parts.append(f"强度: {strength['strength_min']}-{strength['strength_max']}")
        elif "strength_min" in strength:
            explanation_parts.append(f"强度: >{strength['strength_min']}")
        else:
            explanation_parts.append(f"强度: <{strength['strength_max']}")

    if sort:
        conditions["sort_by"] = sort
        explanation_parts.append(f"排序: {sort}")

    if search_terms:
        conditions["query"] = search_terms
        explanation_parts.append(f"关键词: {search_terms}")

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    # Build human-readable explanation
    if explanation_parts:
        explanation = "解析结果: " + "; ".join(explanation_parts)
    else:
        explanation = "未能解析出结构化条件，将使用全文搜索"

    return {
        "original_question": question,
        "conditions": conditions,
        "explanation": explanation,
        "parse_method": "pattern",
        "parse_time_ms": elapsed_ms,
        "confidence": 0.7 if conditions else 0.3,
    }


def try_llm_parse(question: str) -> Optional[dict]:
    """Try to use LLM service for better NLQ parsing.
    
    Falls back to pattern-based parsing if LLM is not available.
    """
    try:
        from app.services import llm_service
        if not hasattr(llm_service, 'available') or not llm_service.available():
            return None

        prompt = f"""Convert this natural language question into a JSON query for memory search.
        
Valid fields:
- type: array of strings (bug, fact, pattern, preference, workflow, architecture)
- date_from: ISO date string
- date_to: ISO date string
- strength_min: integer 0-10
- strength_max: integer 0-10
- query: string (search keywords)
- sort_by: string (newest, oldest, strongest, weakest)
- tags: array of strings

Question: {question}

Return ONLY a JSON object with the query conditions. No explanation."""

        response = llm_service.generate(prompt)
        if response:
            # Parse JSON from response
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                conditions = json.loads(json_match.group())
                return {
                    "original_question": question,
                    "conditions": conditions,
                    "explanation": f"LLM 解析: {json.dumps(conditions, ensure_ascii=False)}",
                    "parse_method": "llm",
                    "confidence": 0.9,
                }
    except Exception as e:
        logger.debug(f"LLM NLQ fallback: {e}")

    return None


def process_nlq(question: str) -> dict:
    """Main NLQ entry point. Tries LLM first, falls back to pattern matching.
    
    AC-F39-4: When LLM not configured, falls back gracefully.
    """
    # Try LLM first
    llm_result = try_llm_parse(question)
    if llm_result:
        return llm_result

    # Fall back to pattern matching
    return parse_natural_query(question)
