
import tiktoken
import openai
import time

# Default model prices (can be updated as needed)
MODEL_PRICES = {
    "gpt-3.5-turbo": 0.0015,  # input per 1K tokens
    "gpt-3.5-turbo-16k": 0.003,
    "gpt-4": 0.03,
    "gpt-4-32k": 0.06
}

class OpenAIUsageTracker:
    def __init__(self, model="gpt-4", price_per_1k_tokens=None):
        self.model = model
        self.price_per_1k_tokens = price_per_1k_tokens or MODEL_PRICES.get(model, 0.03)
        self.total_tokens = 0
        self.total_cost = 0.0
        self.log = []

    def _num_tokens(self, text: str) -> int:
        enc = tiktoken.encoding_for_model(self.model)
        return len(enc.encode(text))

    def track(self, prompt: str, response: str, extra_metadata=None):
        prompt_tokens = self._num_tokens(prompt)
        response_tokens = self._num_tokens(response)
        total = prompt_tokens + response_tokens
        cost = (total / 1000) * self.price_per_1k_tokens

        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": self.model,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total,
            "cost": cost,
            "extra": extra_metadata or {}
        }
        self.log.append(entry)
        self.total_tokens += total
        self.total_cost += cost

        return entry

    def summary(self):
        return {
            "model": self.model,
            "total_requests": len(self.log),
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 5)
        }

    def print_audit_log(self):
        for item in self.log:
            print(f"[{item['timestamp']}] {item['model']} - {item['total_tokens']} tokens → ${item['cost']:.4f}")

