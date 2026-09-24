from threading import Event

from app.services.priority_advisor import PriorityAdvisor, TaskPriority


def test_heuristic_works_without_llm_configuration():
    advisor = PriorityAdvisor()

    assert advisor.suggest_priority("Resolver incidente urgente") == TaskPriority.HIGH
    assert advisor.suggest_priority("Revisar tarefa importante") == TaskPriority.MEDIUM
    assert advisor.suggest_priority("Organizar documentação") == TaskPriority.LOW


def test_valid_llm_response_is_used():
    advisor = PriorityAdvisor(
        llm_client=lambda _: {"priority": "high"},
        api_key="test-key",
    )

    assert advisor.suggest_priority("Organizar documentação") == TaskPriority.HIGH


def test_invalid_llm_response_uses_heuristic_fallback():
    advisor = PriorityAdvisor(
        llm_client=lambda _: "not-a-priority",
        api_key="test-key",
    )

    assert advisor.suggest_priority("Organizar documentação") == TaskPriority.LOW


def test_llm_error_uses_heuristic_fallback():
    def failing_client(_):
        raise RuntimeError("provider unavailable")

    advisor = PriorityAdvisor(llm_client=failing_client, api_key="test-key")

    assert advisor.suggest_priority("Tarefa urgente") == TaskPriority.HIGH


def test_llm_timeout_uses_heuristic_fallback():
    release_client = Event()

    def slow_client(_):
        release_client.wait()
        return "high"

    advisor = PriorityAdvisor(
        llm_client=slow_client,
        api_key="test-key",
        timeout_seconds=0.01,
    )

    result = advisor.suggest_priority("Organizar documentação")
    release_client.set()

    assert result == TaskPriority.LOW
