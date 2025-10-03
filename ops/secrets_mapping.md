# secrets_mapping (masking only)

환경별 시크릿 소스 및 키 매핑(값 미포함)

## Keys
- NOTION_TOKEN
- WEBHOOK_SECRET_KEY (HMAC_SECRET)
- SLACK_WEBHOOK_URL
- DEV_DB_ID
- NEWS_DB_ID
- TARGET_DATABASE_ID (선택)

## Flow
- dev: .env (로컬) → GitHub Secrets(CI) → GCP Secret Manager(운영)
- prod: Secret Manager만 사용

## Notes
- 키 회전 주기 반영, 로컬 .env는 커밋 금지(.gitignore)
- CI에서 필요한 최소 키만 주입, 런타임은 SM 참조


