from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List
import re


@dataclass
class BrandConfig:
    concept_anchor: str = "clean, trustworthy, practical lifestyle"
    color_palette: str = "soft beige, ivory, muted green"
    lighting_style: str = "natural soft light"
    composition_style: str = "editorial product-focused composition"
    banned_elements: str = "exaggerated beauty filter, aggressive sales text, watermark"


@dataclass
class PromptPackage:
    title: str
    audience: str
    product: str
    mood: str
    concept: str
    positive_prompt: str
    negative_prompt: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


MOOD_RULES = {
    "calm": ["저자극", "안심", "부드", "케어", "안정", "진정"],
    "energetic": ["활력", "강력", "빠르게", "즉시", "강한", "임팩트"],
    "premium": ["프리미엄", "고급", "럭셔리", "정교", "세련"],
    "fresh": ["봄", "신선", "맑은", "가벼운", "산뜻"],
}

CONCEPT_RULES = {
    "education": ["가이드", "방법", "팁", "비교", "정리", "체크리스트"],
    "problem-solving": ["해결", "문제", "트러블", "개선", "예방"],
    "trust-building": ["후기", "검증", "근거", "전문", "성분"],
}


def _score_rules(text: str, rules: Dict[str, List[str]]) -> Dict[str, int]:
    score = {k: 0 for k in rules}
    for label, keywords in rules.items():
        for kw in keywords:
            score[label] += len(re.findall(re.escape(kw), text))
    return score


def _pick_best(score: Dict[str, int], default: str) -> str:
    best = max(score, key=score.get)
    return best if score[best] > 0 else default


def build_prompt_package(
    article: str,
    title: str,
    audience: str,
    product: str,
    brand_config: BrandConfig | None = None,
) -> PromptPackage:
    brand = brand_config or BrandConfig()

    mood = _pick_best(_score_rules(article, MOOD_RULES), default="calm")
    concept = _pick_best(_score_rules(article, CONCEPT_RULES), default="education")

    positive_prompt = (
        f"Create a hero image for an informational commerce article. "
        f"Topic: {title}. Audience: {audience}. Product context: {product}. "
        f"Mood: {mood}. Concept: {concept}. "
        f"Maintain concept anchor: {brand.concept_anchor}. "
        f"Use {brand.color_palette} palette, {brand.lighting_style}, "
        f"and {brand.composition_style}. "
        "Include realistic textures, clean layout, and trustworthy tone. "
        "No text overlay. High detail, commercially safe, web editorial style."
    )

    negative_prompt = (
        f"Avoid: {brand.banned_elements}, sensational style, clickbait visuals, "
        "distorted anatomy, cluttered background, over-saturated colors, "
        "misleading before-after comparison, medical claim graphics."
    )

    return PromptPackage(
        title=title,
        audience=audience,
        product=product,
        mood=mood,
        concept=concept,
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
    )
