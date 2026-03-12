from src.concept_engine import build_prompt_package


def test_detects_calm_education_context():
    article = "저자극 세안 방법과 피부 진정을 위한 가이드를 정리했습니다."
    pkg = build_prompt_package(
        article=article,
        title="민감성 피부 세안 가이드",
        audience="민감성 피부 고객",
        product="클렌저",
    )
    assert pkg.mood == "calm"
    assert pkg.concept == "education"
    assert "concept anchor" in pkg.positive_prompt


def test_defaults_when_no_keyword():
    article = "중립적인 설명 문장"
    pkg = build_prompt_package(
        article=article,
        title="중립 글",
        audience="일반 고객",
        product="생활용품",
    )
    assert pkg.mood == "calm"
    assert pkg.concept == "education"
