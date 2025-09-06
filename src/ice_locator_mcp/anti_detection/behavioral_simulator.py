"""
Advanced behavioral simulation for anti-detection.

Implements sophisticated human behavior patterns including:
- Realistic browsing sessions with natural navigation flows
- Adaptive timing based on content and context
- Mouse movement and interaction simulation
- Reading pattern simulation
- Error recovery behaviors
"""

import asyncio
import random
import time
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import structlog


class BehaviorType(Enum):
    """Types of human behaviors to simulate."""
    CASUAL_BROWSING = "casual_browsing"
    FOCUSED_SEARCH = "focused_search"
    RESEARCH_SESSION = "research_session"
    FORM_FILLING = "form_filling"
    ERROR_RECOVERY = "error_recovery"


class SessionPhase(Enum):
    """Phases of a browsing session."""
    INITIAL_LANDING = "initial_landing"
    EXPLORATION = "exploration"
    FOCUSED_ACTIVITY = "focused_activity"
    COMPLETION = "completion"
    IDLE = "idle"


@dataclass
class BehaviorMetrics:
    """Metrics for behavior analysis and adaptation."""
    session_duration: float = 0.0
    page_views: int = 0
    form_submissions: int = 0
    search_queries: int = 0
    error_encounters: int = 0
    success_rate: float = 1.0
    average_page_time: float = 0.0
    interaction_density: float = 0.0
    last_activity: float = 0.0
    
    def update_success_rate(self, success: bool) -> None:
        """Update success rate based on latest result."""
        total_attempts = self.form_submissions + self.search_queries + self.page_views
        if total_attempts > 0:
            successes = int(total_attempts * self.success_rate)
            if success:
                successes += 1
            total_attempts += 1
            self.success_rate = successes / total_attempts


@dataclass
class MouseMovementPattern:
    """Represents a realistic mouse movement pattern."""
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    duration: float
    waypoints: List[Tuple[float, float, float]] = field(default_factory=list)  # (x, y, time)
    
    def generate_waypoints(self) -> None:
        """Generate realistic waypoints for mouse movement."""
        # Calculate distance
        distance = math.sqrt((self.end_x - self.start_x) ** 2 + (self.end_y - self.start_y) ** 2)
        
        # Determine number of waypoints based on distance
        waypoint_count = max(2, min(20, int(distance / 50)))
        
        # Generate waypoints with slight deviations for realism
        for i in range(waypoint_count + 1):
            t = i / waypoint_count  # Progress from 0 to 1
            
            # Linear interpolation
            x = self.start_x + (self.end_x - self.start_x) * t
            y = self.start_y + (self.end_y - self.start_y) * t
            
            # Add slight deviation for realism (except for start and end points)
            if 0 < i < waypoint_count:
                deviation = min(20, distance * 0.1)
                x += random.uniform(-deviation, deviation)
                y += random.uniform(-deviation, deviation)
            
            # Time with slight variation
            time_point = self.duration * t * random.uniform(0.9, 1.1)
            
            self.waypoints.append((x, y, time_point))


@dataclass
class ScrollingPattern:
    """Represents a realistic scrolling pattern."""
    total_height: int
    viewport_height: int
    scroll_events: List[Tuple[int, float]] = field(default_factory=list)  # (scroll_position, time)
    
    def generate_scroll_pattern(self) -> None:
        """Generate realistic scrolling pattern."""
        max_scroll = max(0, self.total_height - self.viewport_height)
        if max_scroll <= 0:
            return
        
        # Determine reading pattern
        if max_scroll < 500:
            # Short page - quick scan
            self._generate_quick_scan_pattern(max_scroll)
        elif max_scroll < 2000:
            # Medium page - thorough reading
            self._generate_thorough_reading_pattern(max_scroll)
        else:
            # Long page - selective reading
            self._generate_selective_reading_pattern(max_scroll)
    
    def _generate_quick_scan_pattern(self, max_scroll: int) -> None:
        """Generate quick scan pattern for short pages."""
        # Scroll to bottom with a few stops
        stops = random.randint(2, 4)
        for i in range(stops):
            position = int(max_scroll * (i + 1) / stops)
            time_point = random.uniform(0.5, 2.0) * (i + 1)
            self.scroll_events.append((position, time_point))
    
    def _generate_thorough_reading_pattern(self, max_scroll: int) -> None:
        """Generate thorough reading pattern for medium pages."""
        # Scroll in chunks with pauses for reading
        chunk_size = self.viewport_height // 2
        position = 0
        
        while position < max_scroll:
            # Scroll down a chunk
            position = min(position + chunk_size, max_scroll)
            time_point = len(self.scroll_events) * random.uniform(2.0, 5.0)
            self.scroll_events.append((position, time_point))
            
            # Add pause for reading (skip some chunks)
            if random.random() < 0.7:  # 70% chance of pause
                pause_time = random.uniform(3.0, 10.0)
                # Add a small scroll during pause to simulate reading
                if len(self.scroll_events) > 0:
                    current_pos = self.scroll_events[-1][0]
                    small_scroll = current_pos + random.randint(-50, 50)
                    small_scroll = max(0, min(small_scroll, max_scroll))
                    if small_scroll != current_pos:
                        self.scroll_events.append((small_scroll, time_point + pause_time * 0.3))
    
    def _generate_selective_reading_pattern(self, max_scroll: int) -> None:
        """Generate selective reading pattern for long pages."""
        # Scroll to interesting sections only
        sections = random.randint(3, 7)
        for _ in range(sections):
            position = random.randint(0, max_scroll)
            time_point = random.uniform(1.0, 3.0) * len(self.scroll_events)
            self.scroll_events.append((position, time_point))
            
            # Add reading pause
            if random.random() < 0.8:
                pause_time = random.uniform(5.0, 15.0)
                self.scroll_events.append((position, time_point + pause_time))


@dataclass
class BrowsingSession:
    """Represents a human browsing session with realistic patterns."""
    session_id: str
    start_time: float = field(default_factory=time.time)
    behavior_type: BehaviorType = BehaviorType.CASUAL_BROWSING
    current_phase: SessionPhase = SessionPhase.INITIAL_LANDING
    metrics: BehaviorMetrics = field(default_factory=BehaviorMetrics)
    goals: List[str] = field(default_factory=list)
    completed_goals: List[str] = field(default_factory=list)
    attention_span: float = 300.0  # 5 minutes base attention span
    fatigue_level: float = 0.0
    last_interaction: float = field(default_factory=time.time)
    
    @property
    def session_age(self) -> float:
        """Get session age in seconds."""
        return time.time() - self.start_time
    
    @property
    def is_fatigued(self) -> bool:
        """Check if user is showing fatigue signs."""
        return self.fatigue_level > 0.7
    
    @property
    def attention_remaining(self) -> float:
        """Calculate remaining attention span."""
        elapsed = self.session_age
        base_remaining = max(0, self.attention_span - elapsed)
        
        # Fatigue reduces attention
        fatigue_penalty = self.fatigue_level * self.attention_span * 0.3
        
        return max(0, base_remaining - fatigue_penalty)


class BehavioralSimulator:
    """Advanced behavioral simulation engine."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.sessions: Dict[str, BrowsingSession] = {}
        
        # Behavior patterns
        self.reading_speeds = {
            'fast': 250,    # words per minute
            'normal': 200,
            'slow': 150,
            'careful': 100
        }
        
        # Timing profiles by behavior type
        self.timing_profiles = {
            BehaviorType.CASUAL_BROWSING: {
                'page_min_time': 3.0,
                'page_max_time': 30.0,
                'between_clicks': (0.5, 3.0),
                'reading_speed': 'normal'
            },
            BehaviorType.FOCUSED_SEARCH: {
                'page_min_time': 5.0,
                'page_max_time': 60.0,
                'between_clicks': (0.3, 2.0),
                'reading_speed': 'fast'
            },
            BehaviorType.RESEARCH_SESSION: {
                'page_min_time': 15.0,
                'page_max_time': 300.0,
                'between_clicks': (1.0, 5.0),
                'reading_speed': 'careful'
            },
            BehaviorType.FORM_FILLING: {
                'page_min_time': 30.0,
                'page_max_time': 180.0,
                'between_clicks': (0.5, 2.0),
                'reading_speed': 'normal'
            }
        }
        
        # Error recovery patterns
        self.error_behaviors = {
            'retry_immediate': 0.3,     # 30% retry immediately
            'retry_after_pause': 0.4,   # 40% retry after pause
            'change_approach': 0.2,     # 20% try different approach
            'give_up': 0.1              # 10% give up
        }
    
    async def start_session(self, 
                          session_id: str,
                          behavior_type: BehaviorType = BehaviorType.CASUAL_BROWSING,
                          goals: List[str] = None) -> BrowsingSession:
        """Start a new behavioral simulation session."""
        
        if goals is None:
            goals = []
        
        session = BrowsingSession(
            session_id=session_id,
            behavior_type=behavior_type,
            goals=goals,
            attention_span=self._calculate_attention_span(behavior_type)
        )
        
        self.sessions[session_id] = session
        
        self.logger.info(
            "Started behavioral session",
            session_id=session_id,
            behavior_type=behavior_type.value,
            goals_count=len(goals),
            attention_span=session.attention_span
        )
        
        return session
    
    async def simulate_page_interaction(self,
                                      session_id: str,
                                      page_content: Dict[str, Any],
                                      interaction_type: str) -> Dict[str, Any]:
        """Simulate realistic page interaction with timing and behavior."""
        
        session = self.sessions.get(session_id)
        if not session:
            session = await self.start_session(session_id)
        
        # Update session state
        await self._update_session_state(session, interaction_type)
        
        # Calculate interaction timing
        timing = await self._calculate_interaction_timing(session, page_content, interaction_type)
        
        # Simulate pre-interaction delay (reading, thinking)
        if timing['pre_delay'] > 0:
            await asyncio.sleep(timing['pre_delay'])
        
        # Record interaction
        session.metrics.page_views += 1
        session.metrics.last_activity = time.time()
        session.last_interaction = time.time()
        
        # Simulate typing patterns for forms
        typing_pattern = None
        if interaction_type == 'form_input':
            typing_pattern = await self._simulate_typing_pattern(
                page_content.get('input_length', 10),
                session.fatigue_level
            )
        
        # Calculate post-interaction delay
        post_delay = timing['post_delay']
        
        interaction_result = {
            'pre_delay': timing['pre_delay'],
            'post_delay': post_delay,
            'typing_pattern': typing_pattern,
            'session_phase': session.current_phase.value,
            'fatigue_level': session.fatigue_level,
            'attention_remaining': session.attention_remaining,
            'behavioral_flags': await self._get_behavioral_flags(session)
        }
        
        self.logger.debug(
            "Page interaction simulated",
            session_id=session_id,
            interaction_type=interaction_type,
            pre_delay=timing['pre_delay'],
            post_delay=post_delay,
            fatigue=session.fatigue_level
        )
        
        return interaction_result
    
    async def simulate_mouse_movement(self,
                                   session_id: str,
                                   start_x: int,
                                   start_y: int,
                                   end_x: int,
                                   end_y: int,
                                   duration: Optional[float] = None) -> MouseMovementPattern:
        """Simulate realistic mouse movement from start to end position."""
        
        session = self.sessions.get(session_id)
        if not session:
            session = await self.start_session(session_id)
        
        # Calculate duration based on distance and session state
        if duration is None:
            distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
            # Base speed: 1000 pixels per second, adjusted by fatigue
            base_duration = distance / 1000.0
            fatigue_multiplier = 1.0 + (session.fatigue_level * 0.5)
            duration = base_duration * fatigue_multiplier
            # Ensure minimum duration
            duration = max(0.1, duration)
        
        # Create movement pattern
        movement = MouseMovementPattern(start_x, start_y, end_x, end_y, duration)
        movement.generate_waypoints()
        
        # Simulate the movement with delays
        for i, (x, y, time_point) in enumerate(movement.waypoints):
            if i > 0:  # Skip first point (instantaneous)
                previous_time = movement.waypoints[i-1][2]
                delay = time_point - previous_time
                if delay > 0:
                    await asyncio.sleep(min(delay, 0.1))  # Cap at 100ms per step
        
        self.logger.debug(
            "Mouse movement simulated",
            session_id=session_id,
            start=(start_x, start_y),
            end=(end_x, end_y),
            duration=duration,
            waypoints=len(movement.waypoints)
        )
        
        return movement
    
    async def simulate_scrolling(self,
                              session_id: str,
                              total_height: int,
                              viewport_height: int) -> ScrollingPattern:
        """Simulate realistic scrolling behavior."""
        
        session = self.sessions.get(session_id)
        if not session:
            session = await self.start_session(session_id)
        
        # Create scrolling pattern
        scrolling = ScrollingPattern(total_height, viewport_height)
        scrolling.generate_scroll_pattern()
        
        # Simulate the scrolling with delays
        for i, (position, time_point) in enumerate(scrolling.scroll_events):
            if i > 0:  # Skip first point
                previous_time = scrolling.scroll_events[i-1][1]
                delay = time_point - previous_time
                if delay > 0:
                    await asyncio.sleep(min(delay, 1.0))  # Cap at 1 second per scroll
        
        self.logger.debug(
            "Scrolling pattern simulated",
            session_id=session_id,
            total_height=total_height,
            viewport_height=viewport_height,
            events=len(scrolling.scroll_events)
        )
        
        return scrolling
    
    async def simulate_decision_making(self,
                                    session_id: str,
                                    complexity: str = "medium",
                                    time_pressure: bool = False) -> float:
        """Simulate human decision-making process with realistic timing."""
        
        session = self.sessions.get(session_id)
        if not session:
            session = await self.start_session(session_id)
        
        # Base decision time based on complexity
        complexity_times = {
            "simple": (1.0, 3.0),
            "medium": (3.0, 8.0),
            "complex": (8.0, 20.0)
        }
        
        min_time, max_time = complexity_times.get(complexity, (3.0, 8.0))
        
        # Adjust for session state
        fatigue_multiplier = 1.0 + (session.fatigue_level * 0.8)
        attention_multiplier = 1.0
        
        if session.attention_remaining < 120:  # Less than 2 minutes
            attention_multiplier = random.uniform(1.2, 2.0)  # Rushed decisions
        
        # Time pressure adjustment
        if time_pressure:
            time_multiplier = random.uniform(0.5, 0.8)
        else:
            time_multiplier = 1.0
        
        decision_time = random.uniform(min_time, max_time) * fatigue_multiplier * attention_multiplier * time_multiplier
        
        # Simulate the decision time
        await asyncio.sleep(min(decision_time, 30.0))  # Cap at 30 seconds
        
        self.logger.debug(
            "Decision making simulated",
            session_id=session_id,
            complexity=complexity,
            time_pressure=time_pressure,
            decision_time=decision_time
        )
        
        return decision_time
    
    async def handle_error_behavior(self,
                                  session_id: str,
                                  error_type: str,
                                  attempt_count: int) -> Dict[str, Any]:
        """Simulate realistic error recovery behavior."""
        
        session = self.sessions.get(session_id)
        if not session:
            return {'action': 'give_up', 'delay': 0}
        
        # Update error metrics
        session.metrics.error_encounters += 1
        session.metrics.update_success_rate(False)
        session.fatigue_level = min(1.0, session.fatigue_level + 0.1)
        
        # Determine behavior based on attempt count and session state
        if attempt_count == 1:
            # First error - usually retry with brief pause
            behavior = 'retry_after_pause'
            delay = random.uniform(2.0, 8.0)
        
        elif attempt_count == 2:
            # Second error - longer pause or different approach
            if session.behavior_type == BehaviorType.FOCUSED_SEARCH:
                behavior = 'change_approach'
                delay = random.uniform(5.0, 15.0)
            else:
                behavior = 'retry_after_pause'
                delay = random.uniform(8.0, 20.0)
        
        elif attempt_count >= 3:
            # Multiple errors - likely to give up or major change
            if session.is_fatigued or session.attention_remaining < 60:
                behavior = 'give_up'
                delay = random.uniform(1.0, 3.0)
            else:
                behavior = 'change_approach'
                delay = random.uniform(15.0, 45.0)
        
        else:
            # Fallback to weighted random selection
            behavior = random.choices(
                list(self.error_behaviors.keys()),
                weights=list(self.error_behaviors.values())
            )[0]
            delay = random.uniform(3.0, 12.0)
        
        # Additional delay for fatigue
        if session.is_fatigued:
            delay *= random.uniform(1.5, 2.5)
        
        self.logger.info(
            "Error behavior simulated",
            session_id=session_id,
            error_type=error_type,
            attempt_count=attempt_count,
            behavior=behavior,
            delay=delay,
            fatigue=session.fatigue_level
        )
        
        return {
            'action': behavior,
            'delay': delay,
            'fatigue_increase': True if session.is_fatigued else False,
            'suggested_action': await self._suggest_recovery_action(session, error_type)
        }
    
    async def calculate_natural_delay(self,
                                    session_id: str,
                                    action_type: str,
                                    context: Dict[str, Any] = None) -> float:
        """Calculate natural human-like delays between actions."""
        
        session = self.sessions.get(session_id)
        if not session:
            return random.uniform(1.0, 3.0)
        
        profile = self.timing_profiles[session.behavior_type]
        base_delay = random.uniform(*profile['between_clicks'])
        
        # Context-based adjustments
        if context:
            # Related actions are faster
            if context.get('related_to_previous'):
                base_delay *= 0.6
            
            # Complex actions take longer
            if context.get('complexity', 'simple') == 'complex':
                base_delay *= 1.8
            
            # Error recovery is slower
            if context.get('is_retry'):
                base_delay *= random.uniform(2.0, 4.0)
        
        # Session state adjustments
        fatigue_multiplier = 1.0 + (session.fatigue_level * 1.5)
        attention_multiplier = 1.0
        
        if session.attention_remaining < 60:
            # Low attention = distracted behavior
            attention_multiplier = random.uniform(1.2, 2.0)
        
        # Phase-based adjustments
        phase_multipliers = {
            SessionPhase.INITIAL_LANDING: 1.5,  # Slower at start
            SessionPhase.EXPLORATION: 1.0,
            SessionPhase.FOCUSED_ACTIVITY: 0.8,  # Faster when focused
            SessionPhase.COMPLETION: 1.2,
            SessionPhase.IDLE: 3.0
        }
        
        phase_multiplier = phase_multipliers.get(session.current_phase, 1.0)
        
        final_delay = base_delay * fatigue_multiplier * attention_multiplier * phase_multiplier
        
        # Ensure reasonable bounds
        final_delay = max(0.3, min(final_delay, 30.0))
        
        return final_delay
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session behavior summary."""
        
        session = self.sessions.get(session_id)
        if not session:
            return {}
        
        session_age = session.session_age
        
        return {
            'session_id': session_id,
            'behavior_type': session.behavior_type.value,
            'current_phase': session.current_phase.value,
            'duration': session_age,
            'metrics': {
                'page_views': session.metrics.page_views,
                'form_submissions': session.metrics.form_submissions,
                'search_queries': session.metrics.search_queries,
                'error_encounters': session.metrics.error_encounters,
                'success_rate': session.metrics.success_rate,
                'interaction_density': session.metrics.interaction_density
            },
            'state': {
                'fatigue_level': session.fatigue_level,
                'attention_remaining': session.attention_remaining,
                'goals_completed': len(session.completed_goals),
                'goals_total': len(session.goals)
            },
            'behavioral_indicators': await self._get_behavioral_flags(session)
        }
    
    def _calculate_attention_span(self, behavior_type: BehaviorType) -> float:
        """Calculate realistic attention span based on behavior type."""
        
        base_spans = {
            BehaviorType.CASUAL_BROWSING: 180,    # 3 minutes
            BehaviorType.FOCUSED_SEARCH: 900,     # 15 minutes
            BehaviorType.RESEARCH_SESSION: 2700,  # 45 minutes
            BehaviorType.FORM_FILLING: 600        # 10 minutes
        }
        
        base = base_spans.get(behavior_type, 300)
        variance = base * 0.3  # 30% variance
        
        return random.uniform(base - variance, base + variance)
    
    async def _update_session_state(self, session: BrowsingSession, interaction_type: str) -> None:
        """Update session state based on interactions."""
        
        current_time = time.time()
        time_since_last = current_time - session.last_interaction
        
        # Update fatigue based on activity
        activity_fatigue = 0.01 * (session.metrics.page_views / 10)
        time_fatigue = (current_time - session.start_time) / 3600 * 0.1  # Fatigue over time
        
        session.fatigue_level = min(1.0, activity_fatigue + time_fatigue)
        
        # Update session phase
        if session.session_age < 30:
            session.current_phase = SessionPhase.INITIAL_LANDING
        elif session.metrics.page_views < 3:
            session.current_phase = SessionPhase.EXPLORATION
        elif session.metrics.form_submissions > 0 or session.metrics.search_queries > 0:
            session.current_phase = SessionPhase.FOCUSED_ACTIVITY
        elif time_since_last > 60:
            session.current_phase = SessionPhase.IDLE
        
        # Update interaction density
        if session.session_age > 0:
            total_interactions = (session.metrics.page_views + 
                                session.metrics.form_submissions + 
                                session.metrics.search_queries)
            session.metrics.interaction_density = total_interactions / (session.session_age / 60)
    
    async def _calculate_interaction_timing(self,
                                          session: BrowsingSession,
                                          page_content: Dict[str, Any],
                                          interaction_type: str) -> Dict[str, float]:
        """Calculate realistic timing for page interactions."""
        
        profile = self.timing_profiles[session.behavior_type]
        
        # Base reading time calculation
        content_length = page_content.get('content_length', 500)
        reading_speed = self.reading_speeds[profile['reading_speed']]
        
        # Estimate words (rough approximation)
        estimated_words = content_length / 5
        base_reading_time = (estimated_words / reading_speed) * 60  # Convert to seconds
        
        # Interaction-specific adjustments
        if interaction_type == 'form_input':
            # Form filling includes reading labels, thinking, typing
            pre_delay = base_reading_time + random.uniform(2.0, 8.0)
            post_delay = random.uniform(0.5, 2.0)
        
        elif interaction_type == 'search':
            # Search includes reading results, deciding on query
            pre_delay = base_reading_time * 0.3 + random.uniform(1.0, 5.0)
            post_delay = random.uniform(1.0, 3.0)
        
        elif interaction_type == 'navigation':
            # Navigation includes scanning page, finding links
            pre_delay = base_reading_time * 0.5 + random.uniform(0.5, 3.0)
            post_delay = random.uniform(0.3, 1.5)
        
        else:
            # General page viewing
            pre_delay = base_reading_time + random.uniform(1.0, 4.0)
            post_delay = random.uniform(0.5, 2.0)
        
        # Apply session state modifiers
        fatigue_modifier = 1.0 + (session.fatigue_level * 2.0)
        attention_modifier = 1.0
        
        if session.attention_remaining < 120:  # Less than 2 minutes attention
            attention_modifier = random.uniform(0.3, 0.7)  # Rushed behavior
        
        pre_delay *= fatigue_modifier * attention_modifier
        post_delay *= fatigue_modifier
        
        # Ensure reasonable bounds
        pre_delay = max(0.5, min(pre_delay, 180.0))
        post_delay = max(0.1, min(post_delay, 30.0))
        
        return {
            'pre_delay': pre_delay,
            'post_delay': post_delay
        }
    
    async def _simulate_typing_pattern(self, text_length: int, fatigue_level: float) -> Dict[str, Any]:
        """Simulate realistic typing patterns with human characteristics."""
        
        # Base typing speed (characters per minute)
        base_speed = random.uniform(180, 320)  # Typical range
        
        # Fatigue affects typing speed
        speed_modifier = 1.0 - (fatigue_level * 0.3)
        actual_speed = base_speed * speed_modifier
        
        # Calculate total typing time
        total_time = (text_length / actual_speed) * 60
        
        # Add pauses for thinking, corrections
        pause_probability = 0.1 + (fatigue_level * 0.2)
        pause_count = int(text_length * pause_probability)
        pause_time = pause_count * random.uniform(0.5, 3.0)
        
        # Correction time (typos and backspacing)
        error_rate = 0.02 + (fatigue_level * 0.05)
        correction_time = text_length * error_rate * 2.0  # Time to fix errors
        
        total_typing_time = total_time + pause_time + correction_time
        
        return {
            'total_time': total_typing_time,
            'typing_speed': actual_speed,
            'pause_count': pause_count,
            'estimated_errors': int(text_length * error_rate),
            'pattern': 'human_variable'
        }
    
    async def _get_behavioral_flags(self, session: BrowsingSession) -> Dict[str, bool]:
        """Get behavioral flags that indicate human-like patterns."""
        
        return {
            'shows_fatigue': session.is_fatigued,
            'attention_declining': session.attention_remaining < 120,
            'experienced_errors': session.metrics.error_encounters > 0,
            'goal_oriented': len(session.goals) > len(session.completed_goals),
            'exploratory_behavior': session.current_phase == SessionPhase.EXPLORATION,
            'consistent_activity': session.metrics.interaction_density > 0.5,
            'realistic_timing': True,  # Always true for our simulation
            'adaptive_behavior': session.metrics.error_encounters > 0 and session.metrics.success_rate > 0.3
        }
    
    async def _suggest_recovery_action(self, session: BrowsingSession, error_type: str) -> str:
        """Suggest recovery action based on session state and error."""
        
        if session.is_fatigued:
            return "take_break"
        
        if session.attention_remaining < 60:
            return "simplify_approach"
        
        if session.metrics.error_encounters > 3:
            return "change_strategy"
        
        error_suggestions = {
            'timeout': 'retry_slower',
            'captcha': 'manual_solve',
            'rate_limit': 'wait_longer',
            'connection': 'check_proxy',
            'parsing': 'refresh_page'
        }
        
        return error_suggestions.get(error_type, 'retry_with_pause')