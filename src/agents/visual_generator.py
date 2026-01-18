"""
Visual Generator - Creates PNG charts for markdown reports
"""

import os
from typing import Dict, List
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class VisualGenerator:
    """Generates visual elements for markdown reports"""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _save_plot(self, fig, name: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        path = os.path.join(self.output_dir, filename)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return path

    def generate_relevance_chart(self, evidence: List[Dict]) -> str:
        """Bar chart of evidence relevance scores"""
        if not evidence:
            return ""

        top = evidence[:10]
        scores = [e.get("relevance", 0) for e in top]
        titles = [e.get("title", f"Source {i+1}")[:30] for i, e in enumerate(top)]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(range(len(scores)), scores, color="steelblue")
        ax.set_yticks(range(len(scores)))
        ax.set_yticklabels(titles)
        ax.set_xlabel("Relevance Score")
        ax.set_title("Top Evidence Relevance Scores")
        ax.set_xlim(0, 1.0)

        path = self._save_plot(fig, "evidence_relevance")
        return f"![Evidence Relevance]({path})"

    def generate_evidence_distribution_chart(self, evidence: List[Dict]) -> str:
        """Pie chart of evidence distribution by relevance"""
        if not evidence:
            return ""

        high = sum(1 for e in evidence if e.get("relevance", 0) >= 0.8)
        medium = sum(1 for e in evidence if 0.5 <= e.get("relevance", 0) < 0.8)
        low = sum(1 for e in evidence if e.get("relevance", 0) < 0.5)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(
            [high, medium, low],
            labels=["High (>=0.8)", "Medium (0.5-0.8)", "Low (<0.5)"],
            autopct="%1.0f%%",
            colors=["#4CAF50", "#FFC107", "#F44336"]
        )
        ax.set_title("Evidence Distribution by Relevance")

        path = self._save_plot(fig, "evidence_distribution")
        return f"![Evidence Distribution]({path})"

    def generate_source_distribution_chart(self, evidence: List[Dict]) -> str:
        """Bar chart of top source domains"""
        if not evidence:
            return ""

        domains = {}
        for e in evidence:
            source = e.get("source", "")
            if "http" in source:
                try:
                    domain = source.split("//")[1].split("/")[0]
                    domain = domain.replace("www.", "").split(":")[0]
                    domains[domain] = domains.get(domain, 0) + 1
                except:
                    domains["unknown"] = domains.get("unknown", 0) + 1
            else:
                domains["unknown"] = domains.get("unknown", 0) + 1

        top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:6]
        labels = [d[0] for d in top_domains]
        counts = [d[1] for d in top_domains]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(labels, counts, color="mediumpurple")
        ax.set_ylabel("Count")
        ax.set_title("Top Source Domains")
        ax.tick_params(axis="x", rotation=45)

        path = self._save_plot(fig, "source_distribution")
        return f"![Source Distribution]({path})"

    def generate_visual_summary(self, plan: Dict, evidence: List[Dict]) -> str:
        """Generate visual summary markdown section"""
        visuals = []

        relevance_chart = self.generate_relevance_chart(evidence)
        if relevance_chart:
            visuals.append("## Visual Summary\n\n" + relevance_chart)

        distribution_chart = self.generate_evidence_distribution_chart(evidence)
        if distribution_chart:
            visuals.append("\n### Evidence Distribution\n\n" + distribution_chart)

        source_chart = self.generate_source_distribution_chart(evidence)
        if source_chart:
            visuals.append("\n### Source Distribution\n\n" + source_chart)

        return "\n".join(visuals) if visuals else ""