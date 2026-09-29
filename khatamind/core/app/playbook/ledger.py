import random
from typing import List, Tuple
from core.domain.models import TacticStat

class TacticLedger:
    def __init__(self, repos):
        self.repos = repos

    async def get_prior_stats(self, tenant_id: str, tactic_key: str) -> Tuple[float, float]:
        # Tenant level stats as prior
        stats = await self.repos.get_tactic_stats(tenant_id, tactic_key=tactic_key)
        alpha0 = 1.0 + sum(s.successes for s in stats)
        beta0 = 1.0 + sum(s.trials - s.successes for s in stats)
        return alpha0, beta0

    async def select_tactic(self, tenant_id: str, customer_id: str, candidate_keys: List[str]) -> str:
        best_key = None
        best_score = -1.0

        for key in candidate_keys:
            alpha0, beta0 = await self.get_prior_stats(tenant_id, key)

            # Add customer level stats
            cust_stats = await self.repos.get_tactic_stats(tenant_id, tactic_key=key)
            cust_successes = sum(s.successes for s in cust_stats if s.customer_id == customer_id)
            cust_trials = sum(s.trials for s in cust_stats if s.customer_id == customer_id)

            # Beta distribution sampling
            alpha = alpha0 + cust_successes
            beta = beta0 + cust_trials - cust_successes
            score = random.betavariate(alpha, beta)

            if score > best_score:
                best_score = score
                best_key = key

        return best_key or candidate_keys[0] if candidate_keys else ""
