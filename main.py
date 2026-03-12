from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.concept_engine import build_prompt_package
from src.image_client import generate_image_via_pollinations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="정보글 기반 이미지 컨셉 통일 생성기")
    parser.add_argument("--article", help="정보글 본문 텍스트")
    parser.add_argument("--article-file", help="정보글 txt 파일 경로")
    parser.add_argument("--title", required=True, help="글 제목")
    parser.add_argument("--audience", required=True, help="타깃 독자")
    parser.add_argument("--product", required=True, help="상품/카테고리")
    parser.add_argument("--save-json", help="프롬프트 결과 JSON 저장 경로")
    parser.add_argument("--generate-image", action="store_true", help="이미지 생성 실행")
    parser.add_argument("--output-image", default="output/generated.png", help="생성 이미지 경로")
    return parser.parse_args()


def load_article(args: argparse.Namespace) -> str:
    if args.article:
        return args.article.strip()
    if args.article_file:
        return Path(args.article_file).read_text(encoding="utf-8").strip()
    raise ValueError("--article 또는 --article-file 중 하나는 필수입니다.")


def main() -> None:
    args = parse_args()
    article = load_article(args)

    pkg = build_prompt_package(
        article=article,
        title=args.title,
        audience=args.audience,
        product=args.product,
    )

    payload = pkg.to_dict()

    print("\n=== Prompt Package ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.save_json:
        path = Path(args.save_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[Saved] {path}")

    if args.generate_image:
        image_path = generate_image_via_pollinations(pkg.positive_prompt, args.output_image)
        print(f"[Image Generated] {image_path}")


if __name__ == "__main__":
    main()
