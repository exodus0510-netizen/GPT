# Cafe24 정보글-이미지 컨셉 통일 생성기

정보성 글(블로그/상품 가이드/비교글)을 입력하면, 글의 핵심 메시지·톤·타깃 독자를 반영한 **일관된 이미지 생성 프롬프트**를 만들고, 선택적으로 실제 이미지를 생성하는 Python 프로그램입니다.

핵심 목표는 다음 2가지입니다.

1. 글과 이미지의 분위기(무드) 통일
2. 쇼핑몰 브랜드 컨셉의 일관성 유지

## 기능

- 글 본문에서 키워드 기반으로 톤/무드 추정
- 브랜드 고정 컨셉(색감, 촬영 스타일, 금지요소) 적용
- 이미지 생성용 `positive_prompt` / `negative_prompt` 자동 생성
- (옵션) Pollinations API를 통해 실제 이미지 파일 생성
- 결과를 `json`으로 저장해 Cafe24 콘텐츠 제작 워크플로우에 재사용

## 빠른 시작

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1) 글을 직접 입력해서 프롬프트 생성

```bash
python main.py \
  --article "봄철 민감성 피부를 위한 저자극 클렌징 루틴을 소개합니다..." \
  --title "민감성 피부 클렌징 가이드" \
  --audience "20~30대 민감성 피부 고객" \
  --product "약산성 클렌저" \
  --save-json output/result.json
```

### 2) 실제 이미지까지 생성(옵션)

```bash
python main.py \
  --article-file samples/article.txt \
  --title "민감성 피부 클렌징 가이드" \
  --audience "20~30대 민감성 피부 고객" \
  --product "약산성 클렌저" \
  --generate-image \
  --output-image output/skin-guide.png
```

> `--generate-image`는 네트워크가 가능한 환경에서 동작합니다.

## Cafe24 적용 팁

- 상품 카테고리별로 브랜드 컨셉(톤/조명/배경)을 고정해 `brand_config`를 운영하세요.
- 업로드 전에 생성 결과의 `negative_prompt`를 확인해 과장/자극적 표현을 차단하세요.
- 같은 시리즈 글은 같은 `concept_anchor`를 유지해 썸네일 통일감을 확보하세요.

## 프로젝트 구조

- `main.py`: CLI 엔트리포인트
- `src/concept_engine.py`: 글 분석 + 컨셉/프롬프트 생성
- `src/image_client.py`: 이미지 생성 API 호출
- `tests/test_concept_engine.py`: 핵심 로직 테스트

