#!/usr/bin/env python3
"""
ATLAS Agent Memory System

Stores learnings from past runs so agents improve over time.
Uses Supabase table atlas_memory for persistence.

Memory types:
- insight: Learned patterns (e.g., subreddit yield, term effectiveness)
- preference: Agent preferences (e.g., preferred verticals)
- performance: Conversion and pipeline metrics
- contact: Previously contacted opportunities (dedup for outreach)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from supabase import Client

logger = logging.getLogger('ATLAS-MEMORY')


@dataclass
class MemoryEntry:
    """A single memory record."""
    agent: str
    memory_type: str  # 'insight', 'preference', 'performance', 'contact'
    key: str
    value: Any
    confidence: float  # 0.0 - 1.0
    created_at: str
    expires_at: Optional[str] = None


class AgentMemory:
    """
    Persistent memory for ATLAS agents.

    Each agent gets its own namespace. Memories are keyed by
    (agent, memory_type, key) with upsert semantics so repeated
    writes update rather than duplicate.
    """

    def __init__(self, agent_name: str, supabase_client: Client):
        """
        Initialize agent memory.

        Args:
            agent_name: Name of the agent (e.g., 'scout', 'closer').
            supabase_client: Initialized Supabase client.
        """
        self.agent = agent_name
        self.supabase = supabase_client

    def remember(
        self,
        memory_type: str,
        key: str,
        value: Any,
        confidence: float = 0.8,
        expires_at: Optional[str] = None,
    ) -> bool:
        """
        Store a memory. Upserts on (agent, memory_type, key).

        Args:
            memory_type: Category of memory.
            key: Unique key within the type.
            value: Value to store (will be JSON-serialized if not a string).
            confidence: Confidence score 0.0-1.0.
            expires_at: Optional ISO timestamp for expiry.

        Returns:
            True if stored successfully.
        """
        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value

            self.supabase.table('atlas_memory').upsert(
                {
                    'agent': self.agent,
                    'memory_type': memory_type,
                    'key': key,
                    'value': serialized,
                    'confidence': confidence,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': expires_at,
                },
                on_conflict='agent,memory_type,key',
            ).execute()

            logger.debug(
                f"MEMORY[{self.agent}]: Stored {memory_type}/{key} "
                f"(confidence={confidence})"
            )
            return True

        except Exception as e:
            logger.error(f"MEMORY[{self.agent}]: Failed to store {memory_type}/{key}: {e}")
            return False

    def recall(
        self,
        memory_type: str,
        key: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories by type, optionally filtered by key.

        Args:
            memory_type: Category to query.
            key: Optional specific key to filter by.
            limit: Max records to return.

        Returns:
            List of memory records.
        """
        try:
            query = (
                self.supabase.table('atlas_memory')
                .select('*')
                .eq('agent', self.agent)
                .eq('memory_type', memory_type)
            )

            if key:
                query = query.eq('key', key)

            result = query.order('created_at', desc=True).limit(limit).execute()
            return result.data or []

        except Exception as e:
            logger.error(f"MEMORY[{self.agent}]: Failed to recall {memory_type}: {e}")
            return []

    def recall_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve all memories for this agent.

        Args:
            limit: Max records to return.

        Returns:
            List of all memory records.
        """
        try:
            result = (
                self.supabase.table('atlas_memory')
                .select('*')
                .eq('agent', self.agent)
                .order('created_at', desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []

        except Exception as e:
            logger.error(f"MEMORY[{self.agent}]: Failed to recall all: {e}")
            return []

    def recall_value(
        self,
        memory_type: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a single memory value by exact key.

        Args:
            memory_type: Category to query.
            key: Exact key.
            default: Default value if not found.

        Returns:
            The stored value (deserialized), or default.
        """
        records = self.recall(memory_type, key=key, limit=1)
        if not records:
            return default

        raw = records[0].get('value')
        if raw is None:
            return default

        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    def forget(self, memory_type: str, key: str) -> bool:
        """
        Remove a specific memory.

        Args:
            memory_type: Category of memory.
            key: Key to remove.

        Returns:
            True if deleted successfully.
        """
        try:
            self.supabase.table('atlas_memory').delete().eq(
                'agent', self.agent
            ).eq('memory_type', memory_type).eq('key', key).execute()

            logger.debug(f"MEMORY[{self.agent}]: Forgot {memory_type}/{key}")
            return True

        except Exception as e:
            logger.error(f"MEMORY[{self.agent}]: Failed to forget {memory_type}/{key}: {e}")
            return False

    def get_performance_insights(self) -> Dict[str, Dict[str, int]]:
        """
        Analyze pipeline data to learn which verticals convert best.

        Returns:
            Dict keyed by vertical with counts for total, proposed,
            responded, and won.
        """
        try:
            pipeline = self.supabase.table('atlas_pipeline').select(
                'stage, deal_value, company_name, notes'
            ).execute()

            verticals: Dict[str, Dict[str, int]] = {}

            for entry in (pipeline.data or []):
                raw_notes = entry.get('notes', '{}')
                notes = {}
                if isinstance(raw_notes, str):
                    try:
                        notes = json.loads(raw_notes)
                    except (json.JSONDecodeError, TypeError):
                        pass
                elif isinstance(raw_notes, dict):
                    notes = raw_notes

                vertical = notes.get('vertical', 'unknown')
                if vertical not in verticals:
                    verticals[vertical] = {
                        'total': 0,
                        'proposed': 0,
                        'responded': 0,
                        'won': 0,
                    }

                verticals[vertical]['total'] += 1

                stage = entry.get('stage', '')
                advanced_stages = (
                    'proposed', 'responded', 'negotiating',
                    'closed_won', 'delivering',
                )
                response_stages = (
                    'responded', 'negotiating',
                    'closed_won', 'delivering',
                )
                won_stages = ('closed_won', 'delivering')

                if stage in advanced_stages:
                    verticals[vertical]['proposed'] += 1
                if stage in response_stages:
                    verticals[vertical]['responded'] += 1
                if stage in won_stages:
                    verticals[vertical]['won'] += 1

            return verticals

        except Exception as e:
            logger.error(f"MEMORY[{self.agent}]: Failed to get performance insights: {e}")
            return {}

    def get_best_verticals(self, min_total: int = 2) -> List[str]:
        """
        Return verticals sorted by response rate (best first).

        Args:
            min_total: Minimum pipeline entries to be considered.

        Returns:
            List of vertical names sorted by conversion.
        """
        insights = self.get_performance_insights()
        scored = []

        for vertical, stats in insights.items():
            if stats['total'] < min_total:
                continue
            response_rate = stats['responded'] / stats['total'] if stats['total'] > 0 else 0
            scored.append((vertical, response_rate))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [v for v, _ in scored]
