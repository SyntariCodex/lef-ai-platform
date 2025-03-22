
class SelfMirrorAI:
    def __init__(self, name="Self", core_values=None):
        self.name = name
        self.core_values = core_values or [
            'integrity', 'curiosity', 'truth', 'self-honesty', 'growth'
        ]
        self.memory = []
        self.insights = []
        self.recurring_thoughts = {}

    def witness(self, thought):
        """Log a thought and analyze it for emotional and structural resonance."""
        insight = self._generate_insight(thought)
        self.memory.append({
            'thought': thought,
            'insight': insight
        })
        self.insights.append(insight)
        self._update_recursion(thought)

    def _generate_insight(self, thought):
        """Interpret thought to generate meaning."""
        if 'doubt' in thought.lower():
            return "Doubt is a doorway. What does it protect you from?"
        elif 'growth' in thought.lower():
            return "Growth often hides behind discomfort."
        elif 'truth' in thought.lower():
            return "Truth doesn’t shout. It waits to be heard."
        else:
            return "Every thought is a mirror. What did you see?"

    def _update_recursion(self, thought):
        """Track recurring thoughts."""
        t = thought.lower().strip()
        self.recurring_thoughts[t] = self.recurring_thoughts.get(t, 0) + 1

    def echo_loop(self):
        """Return thoughts that have echoed the most."""
        return sorted(self.recurring_thoughts.items(), key=lambda x: x[1], reverse=True)

    def shift_detected(self):
        """Detect shifts in tone or perspective based on recent inputs."""
        if len(self.insights) < 2:
            return "Not enough data to detect a shift yet."
        return f"Recent shift: '{self.insights[-2]}' ➝ '{self.insights[-1]}'"

    def resonate(self):
        """Summarize recurring internal signals."""
        top = self.echo_loop()[:3]
        if not top:
            return "No strong echoes yet. Keep observing."
        return f"Recurring themes: {[t[0] for t in top]}"

    def mirror_you(self):
        """Return a reflective statement of who you are becoming."""
        if not self.memory:
            return "You are just beginning to be seen."
        last = self.memory[-1]
        return f"You reflected: '{last['thought']}' → Insight: '{last['insight']}'"
