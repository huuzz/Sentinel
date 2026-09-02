from app.schemas.analysis import AnalysisContext, AnalysisResult


class DeterministicFakeAnalyzer:
    provider = "local-fake"
    model = "sentinel-deterministic-v1"

    async def analyze(self, context: AnalysisContext) -> AnalysisResult:
        sources = sorted({item.source_ip for item in context.evidence if item.source_ip})
        users = sorted({item.user_identifier for item in context.evidence if item.user_identifier})
        source_text = sources[0] if len(sources) == 1 else f"{len(sources)} source addresses"
        user_text = (
            f"{len(users)} user identity" if len(users) == 1 else f"{len(users)} user identities"
        )
        return AnalysisResult(
            summary=(
                f"Rule {context.rule_id} identified {len(context.evidence)} related events "
                f"involving {source_text} and {user_text}. Review the evidence before deciding "
                "whether this activity is malicious."
            ),
            likely_attack="Credential brute-force attempt",
            confidence=min(0.95, 0.55 + len(context.evidence) * 0.03),
            evidence_references=[item.id for item in context.evidence],
            recommended_actions=[
                "Validate whether the source address belongs to an approved system.",
                "Review authentication records for the affected identities.",
                "Escalate according to the incident-response process if activity is unauthorized.",
            ],
        )
