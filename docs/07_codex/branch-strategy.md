# Branch Strategy

## 기본 브랜치

`main`은 배포 가능한 안정 상태를 유지한다. 기능 작업은 별도 브랜치에서 진행하고 검증 후 PR로 병합한다.

## 브랜치 이름

```text
feature/v{version}-{feature-name}
fix/v{version}-{issue-name}
refactor/v{version}-{target-name}
docs/v{version}-{document-name}
```

예시:

```text
feature/v0.1.2-career-profile
fix/v0.1.1-refresh-token-cookie
docs/v0.2.0-api-spec
```

## 작업 흐름

1. `main`을 최신 상태로 맞춘다.
2. 작업 브랜치를 생성한다.
3. 코드와 문서를 함께 수정한다.
4. 테스트, lint, build를 실행한다.
5. 커밋을 만든다.
6. 원격 브랜치에 push한다.
7. PR을 생성한다.
8. 검증 통과 후 병합한다.

## 금지 사항

* `git push --force`
* 기존 태그 삭제 또는 덮어쓰기
* `git reset --hard`
* `git clean -fd`
* 검증 실패 상태에서 main 병합
* 사용자 승인 없는 운영 배포

## 릴리즈 태그

릴리즈 태그는 annotated tag를 사용한다.

```bash
git tag -a v0.1.1 -m "ApplyMate AI v0.1.1"
```

태그는 검증된 main 최신 커밋을 가리켜야 한다.
