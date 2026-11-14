"""Redaktions-Workflow (v2): Storys, Belege, Jobs, Kostenmessung und Budget, Orchestrator.

Der Orchestrator ist deterministisch; Sprachmodelle kommen nur in den Rollen unter news_radar/agents/ zum Einsatz,
und jeder Modellaufruf läuft über workflow.providers.Claude (Messung + Budget).
"""
